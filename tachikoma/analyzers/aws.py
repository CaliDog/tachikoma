from tachikoma.analyzers import BaseAnalyzer

class AllAWSAnalyzer(BaseAnalyzer):
    def analyze_aws_iam(self, previous_results, new_results, diffs, pipeline):
        for operation, path, diff in diffs['dict_diff']:
            if operation == "add" and path == "global.access_keys":
                for index, addition in diff:
                    self.add_notification(
                        title="New access key added to AWS account.",
                        description="Access key \"{}\", owned by user \"{}\" was added on {}".format(
                            addition['AccessKeyId'],
                            addition['UserName'],
                            addition['CreateDate'].isoformat(),
                        ),
                        meta={
                            "key": addition
                        }
                    )

    def analyze_aws_acm(self, previous_results, new_results, diffs, pipeline):
        pass