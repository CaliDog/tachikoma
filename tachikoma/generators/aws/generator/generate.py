from jinja2 import Template
import os

TMPL = '''from tachikoma.generators.aws import AWSGenerator

class AWS{{ service_name }}Generator(AWSGenerator):
    service = "{{ service_name_normalized }}"

    async def generate_{{ service_name_normalized }}_services_from_client(self):
        self.context = await self.get_multiregion_aggregation_for_functions()
'''

all_services = {
    'ACM': 'acm',
    'APIGateway': 'apigateway',
    'Application_Autoscaling': 'application-autoscaling',
    'AppStream': 'appstream',
    'Athena': 'athena',
    'AutoScaling': 'autoscaling',
    'Batch': 'batch',
    'Budgets': 'budgets',
    'CloudDirectory': 'clouddirectory',
    'CloudFormation': 'cloudformation',
    'CloudFront': 'cloudfront',
    'CloudHSM': 'cloudhsm',
    'CloudHSMv2': 'cloudhsmv2',
    'CloudSearch': 'cloudsearch',
    'CloudSearchDomain': 'cloudsearchdomain',
    'CloudTrail': 'cloudtrail',
    'CloudWatch': 'cloudwatch',
    'CodeBuild': 'codebuild',
    'CodeCommit': 'codecommit',
    'CodeDeploy': 'codedeploy',
    'CodePipeline': 'codepipeline',
    'Codestar': 'codestar',
    'Cognito-identity': 'cognito-identity',
    'Cognito-idp': 'cognito-idp',
    'Cognito-sync': 'cognito-sync',
    'Config': 'config',
    'CUR': 'cur',
    'DataPipeline': 'datapipeline',
    'Dax': 'dax',
    'DeviceFarm': 'devicefarm',
    'DirectConnect': 'directconnect',
    'Discovery': 'discovery',
    'DMS': 'dms',
    'DS': 'ds',
    'DynamoDB': 'dynamodb',
    'DynamoDBstreams': 'dynamodbstreams',
    'EC2': 'ec2',
    'ECR': 'ecr',
    'ECS': 'ecs',
    'EFS': 'efs',
    'Elasticache': 'elasticache',
    'ElasticBeanstalk': 'elasticbeanstalk',
    'ElasticTranscoder': 'elastictranscoder',
    'ELB': 'elb',
    'ELBv2': 'elbv2',
    'EMR': 'emr',
    'ES': 'es',
    'Events': 'events',
    'Firehose': 'firehose',
    'Gamelift': 'gamelift',
    'Glacier': 'glacier',
    'Glue': 'glue',
    'GreenGrass': 'greengrass',
    'Health': 'health',
    'Iam': 'iam',
    'ImportExport': 'importexport',
    'Inspector': 'inspector',
    'Iot': 'iot',
    'Iot_Data': 'iot-data',
    'Kinesis': 'kinesis',
    'Kinesisanalytics': 'kinesisanalytics',
    'Kms': 'kms',
    'Lambda': 'lambda',
    'Lex_Models': 'lex-models',
    'Lex_Runtime': 'lex-runtime',
    'Lightsail': 'lightsail',
    'Logs': 'logs',
    'Machinelearning': 'machinelearning',
    'Marketplace-Entitlement': 'marketplace-entitlement',
    'Marketplacecommerceanalytics': 'marketplacecommerceanalytics',
    'Meteringmarketplace': 'meteringmarketplace',
    'MGH': 'mgh',
    'MTurk': 'mturk',
    'OpsWorks': 'opsworks',
    'OpsWorkSCM': 'opsworkscm',
    'Organizations': 'organizations',
    'Pinpoint': 'pinpoint',
    'Polly': 'polly',
    'RDS': 'rds',
    'Redshift': 'redshift',
    'Rekognition': 'rekognition',
    'Route53': 'route53',
    'Route53domains': 'route53domains',
    'S3': 's3',
    'SDB': 'sdb',
    'ServiceCatalog': 'servicecatalog',
    'SES': 'ses',
    'Shield': 'shield',
    'SMS': 'sms',
    'Snowball': 'snowball',
    'SNS': 'sns',
    'SQS': 'sqs',
    'SSM': 'ssm',
    'StepFunctions': 'stepfunctions',
    'StorageGateway': 'storagegateway',
    'STS': 'sts',
    'Support': 'support',
    'SWF': 'swf',
    'WAF': 'waf',
    'WAF-regional': 'waf-regional',
    'Workdocs': 'workdocs',
    'Workspaces': 'workspaces',
    'Xray': 'xray'
}

services = {
    'ACM': 'acm',
    'IAM': 'iam',
}

for service_name, service_name_normalized in services.items():
    skel = Template(TMPL)

    class_file = skel.render({
        "service_name": service_name,
        "service_name_normalized": service_name_normalized
    })

    output_file = '../{}.py'.format(service_name_normalized)

    if os.path.exists(output_file) and not os.getenv("OVERWRITE_ALL", False):
        raise Exception("Refusing to overwrite stuff!")

    with open(output_file, 'w') as f:
        f.write(class_file)