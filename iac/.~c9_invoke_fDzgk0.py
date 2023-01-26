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
    aws_rekognition as rekognition,
)


class IacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        kvs = kinesisvideo.CfnStream(self, "MyVideoStream",
            data_retention_in_hours=24
        )
        
        kds = kinesis.CfnStream(self, "MyCfnStream",
            name="MyDataStream",
            retention_period_hours=24,
            shard_count=123,
            stream_mode_details=kinesis.CfnStream.StreamModeDetailsProperty(
                stream_mode="on-demand"
            ),
        )
        
        bucket_faces = s3.Bucket(
            self,
            'Face_Bucket',
            bucket_name = 'faces_collection'
        )
        
        bucket_metadata = s3.Bucket(
            self,
            'Metadata_Bucket',
            bucket_name = 'metadata_rekognition_234'
        )
        
        queue = sqs.Queue(
            self, "IacQueue",
            visibility_timeout=Duration.seconds(300),
        )
        
        lambdaStream = lambda_.Function(self, "LambdaStream",
            runtime = lambda_.Runtime.PYTHON_3_9,
            handler = "notifier.lambda_handler",
            code = lambda_.Code.from_asset(path.join(__dirname, "lambda-handler")),
            environment = {Queue_URL: queue.queue_url},
        
        )
        
        collection = rekognition.CfnCollection(self, "MyCfnCollection",
            collection_id="face_collection",
            )
        
        

        

     
