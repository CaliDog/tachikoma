import tachikoma

from tachikoma import analyzers
from tachikoma import generators
from tachikoma import emitters

pipeline = tachikoma.Pipeline(
    generators={
        "slack": generators.SlackGenerator(),
        "aws.iam": generators.AWSACMGenerator(),
        "aws.acm": generators.AWSIAMGenerator(),
    },
    analyzers={
        "aws.*": analyzers.AllAWSAnalyzer(),
        "slack": analyzers.SlackAnalyzer()
    },
    emitters={
         "aws.*": emitters.SlackEmitter()
    },
)

pipeline.execute()
