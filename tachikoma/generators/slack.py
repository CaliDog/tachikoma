from tachikoma.generators import ThreadedGenerator
from tachikoma import settings
from slacker import Slacker

class SlackGenerator(ThreadedGenerator):
    def _get_slack_client(self):
        slack = Slacker(getattr(settings, 'SLACK_API_TOKEN'))
        return slack

    def generate_user_list(self):
        self.logger.info("Starting generate_user_list")
        slack = self._get_slack_client()
        users = slack.users.list()
        return {
            "users": users.body['members']
        }

    def generate_group_info(self):
        self.logger.info("Starting generate_group_info")
        slack = self._get_slack_client()
        groups = slack.groups.list()
        return {
            "groups": groups.body['groups']
        }
