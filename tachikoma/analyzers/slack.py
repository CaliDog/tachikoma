
from tachikoma.analyzers import BaseAnalyzer


class SlackAnalyzer(BaseAnalyzer):
    def analyze(self, previous_results, new_results, diffs, channel, pipeline):
        for operation, path, diff in diffs['dict_diff']:
            if operation == "add" and path == "users":
                for index, addition in diff:
                    self.add_notification(
                        title="User \"{}\" added to Slack".format(addition['name']),
                        description="User \"{}\" added to Slack".format(addition['name'])
                    )