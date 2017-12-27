from structlog import get_logger

class BaseAnalyzer(object):
    logger = get_logger()
    notifications = []
    def add_notification(self, title, description, meta=None):
        if meta is None:
            meta = {}

        self.notifications.append({
            "title": title,
            "description": description,
            "meta": meta
        })

    def analyze(self, previous_results, new_results, diffs, channel, pipeline):
        channel_func = channel.replace('.', '_')
        method_name = "analyze_{}".format(channel_func)

        found_method = next((x for x in dir(self) if x == method_name), None)

        if not found_method:
            self.logger.warn(
                "Warning: Didn't find a method named '{}' on {}! Either define it or override the 'analyze' method and handle the analysis pipeline yourself.".format(method_name, self.__class__.__name__),
            )
            return

        method_ref = getattr(self, method_name)

        if previous_results == new_results:
            self.logger.info("Nothing has changed for {}.{}(), skipping analysis.".format(self.__class__.__name__, method_name))
        elif previous_results:
            method_ref(previous_results, new_results, diffs, pipeline)
        else:
            self.logger.info("No previous results for {}.{}(), skipping analysis to get a baseline.".format(self.__class__.__name__, method_name))

from .aws import *
from .slack import *