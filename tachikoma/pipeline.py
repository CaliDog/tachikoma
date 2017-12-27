import asyncio

import re
import warnings

import structlog
import time

from tachikoma import loop, settings
from tachikoma.differs import MultiDiffer
from tachikoma.persistance.shelve import ShelveDB

# TODO: Add in string-to-module resolution for specified generators/analyzers/emitters (like django)

class BasePipeline(object):
    def __init__(self, generators, analyzers, emitters, db=None):
        self.generators = generators
        self.analyzers = analyzers
        self.emitters = emitters
        self.logger = structlog.get_logger()

        if db is None:
            self.db = ShelveDB()
        else:
            self.db = db

        self.context = {
            "generators": {},
            "analyzers": {},
            "emitters": {},
            "diffs": {},
            "messages": {}
        }

        if "*" in generators.keys():
            raise ValueError("The '*' channel is reserved as a catch-all for analyzers and emitters!")

        if not generators:
            raise ValueError("You must specify at least one generator to ")

        if not analyzers:
            raise ValueError("There is no real value in only running the generators, please specify at least one analyzer!")

    def execute(self):
        """
        This is where the magic happens. This pipeline executes by:

            - kicking off each generator in parallel (all regular functions have been wrapped in a threadpool future)
            - retrieving the previous run's results
            - diffs the results
            - present the diffs + global context to each matched
        """

        self.context['generators'] = self.run_generators()

        differ = self.get_differ()

        self.context['previous-results'] = self.db.get_old_results()

        diffs = differ.diff(
            self.context['previous-results'], self.context['generators']
        )

        self.context['diffs'] = diffs

        self.db.store_diffs(self.context['diffs'])

        self.db.store_new_results(self.context['generators'])

        self.context['analyzer_messages'] = self.run_analyzers()

        self.context['sent_notifications'] = self.run_emitters()


    def run_generators(self):
        generators = [generator.run() for generator in self.generators.values()]

        generators_start_time = time.time()
        results = loop.run_until_complete(asyncio.gather(*generators, loop=loop))
        generators_end_time = time.time()

        self.logger.info("Running generator pipeline took {} seconds".format(generators_end_time - generators_start_time))

        for generator_name, result in zip(self.generators.keys(), [item for sublist in results for item in sublist]):
            if isinstance(result, Exception):
                self.generators.pop(generator_name)
                if getattr(settings, "DIE_ON_EXCEPTION", False):
                    raise result

                self.logger.error("An unhandled exception was raised in the coroutine "
                                  "for {} - {}. Make sure the keys in use have the "
                                  "proper permissions!".format(generator_name, result.response['Error']['Message']))
        return dict(zip(self.generators.keys(), results))

    def get_differ(self):
        return MultiDiffer()

    def run_analyzers(self):
        notifications = {}
        for analyzer_regex, analyzer_instance in self.analyzers.items():
            matched_channels = [x for x in self.context.get('generators').keys() if re.match(analyzer_regex, x)]
            if not matched_channels:
                warnings.warn("The analyzer regex '{}' didn't match any generator channels, this shouldn't happen!")

            for channel in matched_channels:
                analyzer_instance.analyze(
                    previous_results=self.context.get('previous-results', {}).get(channel, {}),
                    new_results=self.context.get('generators').get(channel, {}),
                    diffs=self.context.get('diffs', {}).get(channel, {}),
                    channel=channel,
                    pipeline=self
                )

                if analyzer_instance.notifications:
                    if channel not in notifications:
                        notifications[channel] = []
                    notifications[channel] += analyzer_instance.notifications

        return notifications

    def run_emitters(self):
        sent_notifications = []
        for emitter_regex, emitter_instance in self.emitters.items():
            matched_channels = [x for x in self.context.get('generators').keys() if re.match(emitter_regex, x)]
            if not matched_channels:
                warnings.warn("The emitter regex '{}' didn't match any generator channels, this shouldn't happen!")

            for channel in matched_channels:
                sent_notification = emitter_instance.emit(
                    channel=channel,
                    message=self.context['analyzer_messages'][channel],
                    pipeline=self
                )
                sent_notifications.append(sent_notification)

        return sent_notifications

class Pipeline(BasePipeline):
    pass
