import json
import boto3 
import base64
import os
from datetime import datetime

#acessando os servicos da AWS através do boto3
sqs = boto3.client('sqs')
dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')

#defining enviroments variables
queue_url = os.environ['queue_url_variable']
metadata_bucket_name = os.environ['metadata_bucket_name_variable']
face_bucket_name = os.environ['face_bucket_name_variable']

#function to return non-repeating values in a list
def unique(lista):
  
    # initialize an empty list
    unique_list = []
  
    for x in lista:
        # check if there is a single value or not
        if x not in unique_list:
            unique_list.append(x)
            
    return unique_list


def lambda_handler(event, context):
    #list that will store the names of recognized faces
    listaNome = []
    
    #The "event" variable is the trigger input coming from the Kinesis Data Stream (in this case a JSON file)
    for record in event['Records']:
        #the file comes in base64, here we decode it to ascii and put it in JSON format
        data = json.loads(base64.b64decode(record['kinesis']['data']).decode('ascii'))
       
        #iteration within the 'FaceSearchResponse' fields, a field that indicates which faces were recognized 
        for response in data['FaceSearchResponse']:
            for matchedface in response['MatchedFaces']:
                face = matchedface['Face']
                #variable 
                imageId = face.get('ExternalImageId')
                
                if imageId != None:
                    #storing the rekognition JSON response in an S3 bucket for possible audits
                    s3.put_object(Body=json.dumps(data), Bucket=metadata_bucket_name, Key='rekognition-metadata-{}.json'.format(datetime.now()))
                    
                    response = s3.get_object_tagging(
                        Bucket = face_bucket_name,
                        Key = '{}.jpg'.format(str(imageId))
                    )

                    nomeID = response['TagSet']
                    listaNome.append(nomeID[0]['Value'])
                    
    #removing repeated names
    lista2 = unique(listaNome)   
    
    for nome in lista2:
        message = '{} was recognized'.format(nome)
        messageReturn = sqs.send_message(QueueUrl=queue_url,MessageBody=message)
    
   
                
    return {
        'statusCode': 200,
        'body': json.dumps('')
    }

