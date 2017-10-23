import threading

import mock
import time

from tachikoma.generators import BaseGenerator, ThreadedGenerator
from tachikoma.tests import TachikomaTestcase

class MockLoggerMixin(object):
    def get_logger(self):
        return mock.MagicMock()

class BaseGeneratorTests(TachikomaTestcase):
    def test_creation(self):
        class GoodTestGenerator(BaseGenerator):
            async def generate_some_data(self):
                return {"some-data": "Test data!"}

        generator = GoodTestGenerator()

        result = self.loop.run_until_complete(generator.run())

        self.assertEqual(result, {"some-data": "Test data!"})

    def test_failure_cases(self):
        class WrongCallableTypeGenerator(BaseGenerator):
            def generate_some_data(self):
                return {}

        class WrongReturnTypeGenerator(BaseGenerator):
            async def generate_exception(self):
                return "Boom!"

        class ExceptionRaisingGenerator(MockLoggerMixin, BaseGenerator):
            async def generate_exception(self):
                raise Exception("Boom")

        class ClobberingGenerator(BaseGenerator):
            async def generate_test_object(self):
                return {"test": "a"}

            async def generate_test_object_too(self):
                return {"test": "a"}

        # Test failure cases
        self.assertGeneratorRaises(WrongCallableTypeGenerator, Exception)
        self.assertGeneratorRaises(WrongReturnTypeGenerator, Exception)
        self.assertGeneratorRaises(ClobberingGenerator, Exception)

        # Test exceptions being raised and handled properly
        generator = ExceptionRaisingGenerator()
        self.loop.run_until_complete(generator.run())
        self.assertTrue(generator.logger.error.call_count == 1)
        self.assertTrue("raised an exception" in generator.logger.error.call_args[0][0])

class ThreadedGeneratorTests(TachikomaTestcase):
    def test_threading_generator(self):
        class TestThreadedGenerator(ThreadedGenerator):
            def generate_test_data(self):
                return {"test": "passed!"}

        generator = TestThreadedGenerator()
        results = self.loop.run_until_complete(generator.run())
        self.assertTrue(results == {"test": "passed!"})

    def test_threading_is_working(self):
        class TestThreadedGenerator(ThreadedGenerator):
            """
            The time.sleep(.01) below is to allow for 100 instructions to complete per thread before a context switch is triggered.
            Otherwise we'd be monkeying with sys.setcheckinterval, and I'd rather not mess with python VM settings during tests, as
            that could be detrimental to the entire test suite.
            """
            def generate_thread_one_data(self):
                time.sleep(.01)
                return {"thread_one": threading.get_ident()}
            def generate_thread_two_data(self):
                time.sleep(.01)
                return {"thread_two": threading.get_ident()}
            def generate_thread_three_data(self):
                time.sleep(.01)
                return {"thread_three": threading.get_ident()}
            def generate_thread_four_data(self):
                time.sleep(.01)
                return {"thread_four": threading.get_ident()}
            def generate_thread_five_data(self):
                time.sleep(.01)
                return {"thread_five": threading.get_ident()}

        generator = TestThreadedGenerator()
        results = self.loop.run_until_complete(generator.run())

        # Ensure that we were given N different thread identifiers, where N is the number of generator functions defined
        assert len(set(results.values())) == len(generator.all_coroutines)