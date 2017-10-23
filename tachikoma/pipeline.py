import asyncio

import re
import warnings

import structlog
import time

from tachikoma import loop, settings
from tachikoma.differs import MultiDiffer
from tachikoma.persistance.flatfile import ShelveDB


class BasePipeline(object):
    db = ShelveDB()

    def __init__(self, generators, analyzers, emitters):
        self.generators = generators
        self.analyzers = analyzers
        self.emitters = emitters
        self.logger = structlog.get_logger()
        self.context = {
            "generators": {},
            "analyzers": {},
            "emitters": {},
            "diffs": {}
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

        self.context['diffs'].update(diffs)

        self.db.store_diffs(diffs)
        self.db.store_new_results(self.context['generators'])

        analysis = self.call_analyzers()


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

    def call_analyzers(self):
        notifications = []
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
                    global_ctx=self.context
                )

            notifications += analyzer_instance.notifications

        return notifications


class Pipeline(BasePipeline):
    pass
