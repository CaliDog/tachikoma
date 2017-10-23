import asyncio

import aiobotocore

from tachikoma.generators import BaseGenerator

from tachikoma import loop

def run_in_all_regions(decorated_function):
    """
    ** Note ** Your wrapped coroutine *must* take in a region name argument and use that to construct it's client

    This is a decorator to run the wrapped coroutine in every region that the generator's service knows about
    (using `botocore.Session.get_available_regions`), aggregates the results in the form:

    {
        "$REGION_NAME": $CORO_RESULT
    }
    """
    async def wrapper(generator):
        aggregation = {}
        regions = generator.boto_session.get_available_regions(generator.service)
        futures = []
        for region in regions:
            futures.append(decorated_function(generator, region))

        results = await asyncio.gather(*futures, return_exceptions=False, loop=loop)

        for region, result in zip(regions, results):
            if result:
                aggregation[region] = result

        return aggregation
    return wrapper

class AWSGenerator(BaseGenerator):
    service = None

    def __init__(self):
        if not self.service:
            raise Exception("You must define a service type for your sublcasses of AWSGenerator!")

        self.boto_session = aiobotocore.get_session(loop=loop)

        super().__init__()

    async def paginate_call(self, boto_client, aws_call, *args, **kwargs):
        """
        Paginate an aws call, this will iterate through *all* results, and return a unified payload, not just the first page worth.
        """
        payload = {}
        paginator = boto_client.get_paginator(aws_call)
        async for result in paginator.paginate(*args, **kwargs):
            payload = self.aggregate_dict(payload, self.clean_result(result))

        return payload

    def clean_result(self, result):
        result.pop('ResponseMetadata', None)
        result.pop('IsTruncated', None)
        return result
