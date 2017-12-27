import asyncio

from tachikoma.generators.aws import AWSGenerator, run_in_all_regions

class AWSACMGenerator(AWSGenerator):
    service = "acm"

    @run_in_all_regions
    async def generate_certificate_list(self, region_name=None):
        self.logger.debug("Generating certificate list with region {}".format(region_name))

        boto_client = self.boto_session.create_client(self.service, region_name=region_name)

        certificates = await self.paginate_call(boto_client, 'list_certificates')

        if not certificates['CertificateSummaryList']:
            await boto_client.close()
            return {}

        self.logger.debug("Got certificates! Scheduling them to be described.".format(region_name))

        futures = []
        for certificate in certificates['CertificateSummaryList']:
            futures.append(
                boto_client.describe_certificate(
                    CertificateArn=certificate['CertificateArn']
                )
            )

        results = await asyncio.gather(*futures, return_exceptions=True)

        self.logger.debug("Finished describing!".format(region_name))

        await boto_client.close()

        return {
            "certificates": [x.get('Certificate') for x in results]
        }