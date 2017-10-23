
from tachikoma.analyzers import BaseAnalyzer


class SlackAnalyzer(BaseAnalyzer):
    def analyze_aws_iam(self, previous_results, new_results, diffs, global_ctx):
        pass
        # for region in new_results:
        #     self.add_notification(
        #         title="",
        #         description=""
        #     )
