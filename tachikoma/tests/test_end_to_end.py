import mock
import tachikoma

from tachikoma.emitters import BaseEmitter
from tachikoma.generators import BaseGenerator
from tachikoma.analyzers import BaseAnalyzer
from tachikoma.tests import TachikomaTestcase

class DummyGen(BaseGenerator):
    async def generate_user_list(self):
        self.called = True
        return {"test": True}

class DummyAnalyzer(BaseAnalyzer):
    def analyze_chan1(self, previous_results, new_results, diffs, pipeline):
        self.called = True
        self.add_notification(title="Hello", description="Some desc", meta={"somemeta": 1})

class DummyEmitter(BaseEmitter):
    def emit(self, channel, message, pipeline):
        self.called = True
        return {"chan1": [{"message": 1}]}

class PipelineRunTests(TachikomaTestcase):
    def test_pipeline(self):
        emitter = DummyEmitter()
        gen = DummyGen()
        analyzer = DummyAnalyzer()

        db = mock.Mock()
        db.get_old_results.return_value = {"chan1": {"test": False}}

        pipeline = tachikoma.Pipeline(
            generators={"chan1": gen},
            analyzers={"chan1": analyzer},
            emitters={"chan1": emitter},
            db=db
        )

        pipeline.execute()

        self.assertTrue(gen.called)

        self.assertTrue(analyzer.called)
        self.assertTrue(len(analyzer.notifications) > 0)

        self.assertTrue(emitter.called)

        self.assertTrue(len(pipeline.context['sent_notifications']) > 0)
        self.assertTrue(len(pipeline.context['analyzer_messages']) > 0)