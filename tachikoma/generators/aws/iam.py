from tachikoma.generators.aws import AWSGenerator

class AWSIAMGenerator(AWSGenerator):
    service = "iam"

    async def generate_access_key_list(self, region_name=None):
        boto_client = self.boto_session.create_client(self.service, region_name=region_name)

        access_keys = await self.paginate_call(boto_client, 'list_access_keys')

        await boto_client.close()

        return {
            "global": {
                "access_keys": access_keys['AccessKeyMetadata']
            }
        }