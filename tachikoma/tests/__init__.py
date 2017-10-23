import unittest
import asyncio

class TachikomaTestcase(unittest.TestCase):
    loop = asyncio.get_event_loop()

    def assertGeneratorRaises(self, generator_class, exception_class):
        with self.assertRaises(exception_class):
            generator = generator_class()
            self.loop.run_until_complete(generator.run())