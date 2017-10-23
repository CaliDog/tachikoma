import tachikoma

from tachikoma.analyzers.aws.all import AWSAnalyzer
from tachikoma.analyzers.slack import SlackAnalyzer

from tachikoma.generators.aws.acm import AWSACMGenerators
from tachikoma.generators.aws.iam import AWSIAMGenerators
from tachikoma.generators.slack import SlackGenerator

pipeline = tachikoma.Pipeline(
    generators={
        "aws.iam": AWSIAMGenerators(),
        "aws.acm": AWSACMGenerators(),
        "slack": SlackGenerator()
    },
    analyzers={
        "aws.*": AWSAnalyzer(),
        "slack": SlackAnalyzer()
    },
    emitters={
         # "aws.*": SlackEmitter()
    },
)

pipeline.execute()
