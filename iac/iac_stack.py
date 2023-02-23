from os import path
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_kinesisvideo as kinesisvideo,
    aws_kinesis as kinesis,
    aws_s3 as s3,
    aws_iam as iam,
    aws_lambda as lambda_,
    region_info,
    aws_rekognition as rekognition,
)
from aws_cdk.aws_lambda_event_sources import KinesisEventSource
from aws_cdk.aws_lambda_event_sources import SqsEventSource
import uuid

unique_id1 = str(uuid.uuid4())

class IacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        kvs = kinesisvideo.CfnStream(self, "MyVideoStream",
            data_retention_in_hours = 24
        )
        
        kds = kinesis.Stream(self, "MyStream",
            stream_name = "MyDataStream",
            retention_period = Duration.hours(24),
            stream_mode = kinesis.StreamMode.ON_DEMAND
            
        )
        
        bucket_faces = s3.Bucket(
            self,
            'Face_Bucket',
            bucket_name = 'faces-collection-{}'.format(unique_id1), 
            encryption = s3.BucketEncryption.KMS_MANAGED,
            versioned = True
        )
        
        bucket_metadata = s3.Bucket(
            self,
            'Metadata_Bucket',
            bucket_name = 'metadata-rekognition-{}'.format(unique_id1),
            encryption = s3.BucketEncryption.KMS_MANAGED,
            versioned = True
        )
        
        queue = sqs.Queue(
            self, "IacQueue",
            visibility_timeout=Duration.seconds(300),
            encryption = sqs.QueueEncryption.KMS_MANAGED
        )
        
        
        rekognition_role = iam.Role(self, "Role",
            assumed_by=iam.ServicePrincipal("rekognition.amazonaws.com"),
        )
        
        
        lambdaStream = lambda_.Function(self, "LambdaStream",
            runtime = lambda_.Runtime.PYTHON_3_9,
            handler = "notifier.lambda_handler",
            code = lambda_.Code.from_asset(path.join("functions","notifier")),
            environment = {"queue_url_variable": queue.queue_url,
                            "metadata_bucket_name_variable": bucket_metadata.bucket_name,
                            "face_bucket_name_variable": bucket_faces.bucket_name
            },
        
        )
        
        lambdaStream.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                's3:*',
                's3-object-lambda:*'
            ],
            resources=[
                '*',
            ],
        ))
        
        lambdaStream.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'sqs:*',
            ],
            resources=[
                '*',
            ],
        ))
        
        lambdaStream.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'kinesis:*',
            ],
            resources=[
                '*',
            ],
        ))
        
        lambdaStream.add_event_source(KinesisEventSource(kds,
            starting_position=lambda_.StartingPosition.TRIM_HORIZON
        ))
        
        lambdaNotification = lambda_.Function(self, "LambdaNotification",
            runtime = lambda_.Runtime.PYTHON_3_9,
            handler = "message-app.lambda_handler",
            code = lambda_.Code.from_asset(path.join("functions","message-app")),
        )
        
        lambdaNotification.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "ses:*",
                'sqs:*',
            ],
            resources=[
                '*',
            ],
        ))
        
        event_source = SqsEventSource(queue)
        lambdaNotification.add_event_source(event_source)
        
        collection = rekognition.CfnCollection(self, "MyCfnCollection",
            collection_id="face_collection",
            )
        
        cfn_stream_processor = rekognition.CfnStreamProcessor(self, "MyCfnStreamProcessor",
            kinesis_video_stream=rekognition.CfnStreamProcessor.KinesisVideoStreamProperty(
                arn = kvs.attr_arn
            ),
            role_arn=rekognition_role.role_arn,
        
            face_search_settings=rekognition.CfnStreamProcessor.FaceSearchSettingsProperty(
                collection_id = collection.collection_id,
        
                # the properties below are optional
                face_match_threshold=0.80
            ),
            kinesis_data_stream=rekognition.CfnStreamProcessor.KinesisDataStreamProperty(
                arn = kds.stream_arn
            ),
        
            name = "stream-video-rekognition-processor",
        )
        
        

     
