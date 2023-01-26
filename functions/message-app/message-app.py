import boto3
from botocore.exceptions import ClientError

def send_email(SUBJECT):
    SENDER = "your@email.com" # must be verified in AWS SES Email
    RECIPIENT = "your@email.com" # must be verified in AWS SES Email

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Face Recognition Notification\r\n"
                "This email is an automatic notification"
                )
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
    <h1>Face Recognition Notification</h1>
    <p>This email is an automatic notification</p>
    </body>
    </html>
                """            

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses')

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
        
                        'Data': BODY_HTML
                    },
                    'Text': {
        
                        'Data': BODY_TEXT
                    },
                },
                'Subject': {

                    'Data': SUBJECT
                },
            },
            Source=SENDER
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def lambda_handler(event, context):
    for records in event['Records']:
        #Leitura do campo que contém a mensagem no sqs
        payload = str(records['body'])
        
    send_email(payload)
