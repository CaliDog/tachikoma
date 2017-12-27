import asyncio
import functools
import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import Awaitable, List, Iterable, Tuple

from structlog import get_logger

from tachikoma import loop

class BaseGenerator(object):
    """
    A generator is a collection of coroutines that run concurrently with all other generator coroutines
    """
    def __init__(self):
        self.logger = self.get_logger()
        self.logger.debug("Initializing generator {} at {}".format(self.__class__.__name__, hex(id(self))))

        self.completed = 0
        self.context = {}
        self.all_coroutines = self.get_coroutines()
        self.master_coro = asyncio.gather(*self.all_coroutines, return_exceptions=True)

    def _format_function(self, method_name):
        return "{}.{}()".format(self.__class__.__name__, method_name)

    def get_logger(self):
        return get_logger(self.__class__.__module__)

    def aggregate_dict(*args):
        res = {}
        for d in args:
            if not isinstance(d, dict):
                continue
            for k, v in d.items():
                res.setdefault(k, [])
                if isinstance(v, list):
                    res[k].extend(v)
                else:
                    res[k].append(v)
        return res

    async def run(self):
        """
        Run the actual coroutine group, returning the aggregated result context
        """
        results = await self.master_coro
        for (method_name, _), result in zip(self.enumerate_generators(), results):
            if isinstance(result, Exception):
                self.logger.error("Generator {} raised an exception -> {}".format(self._format_function(method_name), result))
                continue

            if not isinstance(result, dict):
                raise Exception("Generator routine {} didn't return a dictionary. Can't merge :(".format(self._format_function(method_name)))

            self.merge_results(result)

        return self.context

    def merge_results(self, result):
        """
        Override this for alternative merging strategies. This will refuse to update the generator context with duplicate values, but
        if you wanted to do something like append or clobber, this would be the place to do it!
        """
        existant_keys = set(self.context.keys())
        new_keys = set(result.keys())

        keys_to_clobber = new_keys.intersection(existant_keys)

        if keys_to_clobber:
            raise Exception("Cowardly refusing to overwrite the generator context variable {}, because it's already defined!".format(existant_keys))

        self.context.update(result)

    def enumerate_generators(self) -> Iterable[Tuple]:
        """
        Enumerate any callable on the current instance prefixed with "generate_". It's expected that all
        the callables are coroutines (async def...), but there's checking to make sure.
        """
        # Check to ensure that our methods are sane
        for method_name, coroutine in inspect.getmembers(self):
            if method_name.startswith('generate_'):
                if not inspect.iscoroutinefunction(coroutine):
                    raise Exception("Invalid coroutine {}! Perhaps you should be using the ThreadedGenerator?".format(self._format_function(method_name)))
                yield method_name, coroutine

    def get_coroutines(self) -> List[Awaitable]:
        """
        Gets and creates pending coroutines to be gathered and awaited further up the pipeline
        """
        coros = []
        for method_name, coroutine in self.enumerate_generators():
            coros.append(coroutine())
        return coros

class ThreadedGenerator(BaseGenerator):
    def __init__(self, thread_workers=25):
        self.threadpool = ThreadPoolExecutor(max_workers=thread_workers)
        super().__init__()

    def enumerate_generators(self):
        """
        Wrap our synchronous functions in a future running on a thread pool executor. Uses functools.partial to
        ensure that we return a callable, instead of a ready-to-go coroutine (to mirror the functionality of
        BaseGenerator.enumerate_generators)
        """
        for method_name, method_reference in inspect.getmembers(self):
            if method_name.startswith('generate_') and inspect.ismethod(method_reference):
                coroutine = functools.partial(
                    loop.run_in_executor, self.threadpool, method_reference
                )
                yield method_name, coroutine

from .aws.acm import AWSACMGenerator
from .aws.iam import AWSIAMGenerator

from .slack import SlackGenerator