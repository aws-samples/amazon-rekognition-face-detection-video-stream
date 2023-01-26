## This sample demonstrates how to create a Face Recognition through Stream Video application with a serverless architecture using Python CDK.


![Alt text](https://d195kho0tyqjph.cloudfront.net/Arquitetura-Blogpost.drawio.png "Solution Overview")

1. Storage Pipeline: This component is responsible for storing the faces collection (bucket 1) that should be recognized during the video stream, and storing the Rekognition output metadata (bucket 2) for possible audits
2. Stream Pipeline: This component input only occurs after the video has been streamed through the Amazon Kinesis Video Stream API to access the Video Stream endpoint. The video transmission can be done by RTSP cameras - using a RaspberryPI, for example - or you can use your Desktop's webcam. After the component's input been configured, Rekognition will be analyzing the video and AWS Lambda 1 will be analyzing Rekognition's outputs so that if there is any face recognition, the notification pipeline will be triggered.
3. Notification Pipeline: This component is responsible for processing messages sent by AWS Lambda 1 through a queue. Each message received in Amazon SQS will be an event that will activate AWS Lambda 2, responsible for performing a POST in the API of a messaging application. In this sample, we will use Amazon SES to do the notification, but you could do the notification with any other messaging app (Slack; Whatsapp, for example). For this reason, I have not included Amazon SES in the solution overview.

## Pre-requisites
* AWS [CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) with [credentials configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) which will also be used by the CDK.
* Create and source a Python virtualenv on MacOS and Linux, and install python dependencies: 
<pre><code>python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
</code></pre>

* Install the latest version of the AWS [CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) CLI:
<pre><code>npm i -g aws-cdk</code></pre>
* [Bootstrapping](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) your CDK with:
<pre><code>cdk bootstrap</code></pre>

## Running
Make sure you have AWS CDK installed and working, all the dependencies of this project defiend in the requirements.txt file, and make sure you are runnning on US East (N. Virginia) region or other region that Amazon Rekognition Video streaming API is available. You can check [here](https://docs.aws.amazon.com/general/latest/gr/rekognition.html)


1.
<pre><code>git clone https://github.com/henriquelsz/amazon-rekogntion-face-detection-video-stream.git
cd iac
</code></pre>
2. Run <code>cdk deploy</code> and wait for the deployment to finish successfully;

## Testing
1. Open your AWS Console and go to AWS S3 Service and go to the bucket faces-collection-<some randon ID>
2. Upload a photo of yourself (make sure to upload a JPG file)
3. Create a tag for the photo you have just uploaded, on Key field please put the same name of the object (please, don't forget to put the objecet name with the ".jpg" extension) and on the Value field put the name of the person recognized - this step is for resolve desambiguity, in case you upload of 2+ photos of the same person on your dataset.
4. Go to Amazon SES service and create identity, on Identity type choose "Email address" and put your own email, click on "Create Identity". After this go to your inbox email and authorize AWS to send emails.
5. Now go to your terminal and run the following command to start the stream processor you created.
<pre><code>aws rekognition start-stream-processor --name stream-video-rekognition-processor</code></pre>
6. Start stream to your video stream that you just created - MyDataStream. You can use [Amazon Kinesis Video Streams Producer SDK](https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp#building-from-source) from the AWS Labs GitHub repository, that includes various ways of writing to a Kinesis Video Stream. These include native SDKs, a gstreamer application that uses the webcam on your Mac or PC, a Raspberry Pi project, and other methods.

## Cleaning Up
Open your terminal on the root of the clone repository and these commands:
<pre><code>cd iac
cdk destroy
</code></pre>

