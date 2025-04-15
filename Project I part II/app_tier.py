import boto3
import os
from botocore.exceptions import ClientError

ec2_client = boto3.client('ec2', region_name='us-east-1', aws_access_key_id="ADD YOUR ACCESS KEY ID",aws_secret_access_key="ADD YOUR SECRET KEY")

#IMPLEMENT SYNCHRONISATION
def fetchFromReqSqs():
    sqs = boto3.client("sqs",region_name="us-east-1",
        aws_access_key_id="ADD YOUR ACCESS KEY ID",
        aws_secret_access_key="ADD YOUR SECRET KEY")
    queueUrl = 'REQUEST QUEUE URL'
    messages = sqs.receive_message(QueueUrl=queueUrl, MaxNumberOfMessages=1, MessageAttributeNames=['All'], VisibilityTimeout=360)
    if 'Messages' in messages:
        message = messages['Messages'][0]
        messageId = message['MessageId']
        receipt_handle = message['ReceiptHandle']
        # Delete received message from queue
        sqs.delete_message(QueueUrl=queueUrl, ReceiptHandle=receipt_handle)
        return {'messageBody': message['Body'],'messageId':messageId}
    

def download_image_from_s3(s3_path, local_path):
    s3_client = boto3.client('s3',region_name="us-east-1",
        aws_access_key_id="ADD YOUR ACCESS KEY ID",
        aws_secret_access_key="ADD YOUR SECRET KEY")
    bucket_name = 'ADD YOUR BUCKET NAME'
    s3_client.download_file(bucket_name, s3_path, local_path)

def run_model(image_path):
    # Run the model using the os library
    command = f"python3 face_recognition.py {image_path}"
    stream = os.popen(command)
    output = stream.read()
    return output

def uploadToS3(fileToUpload, fileName):
    s3 = boto3.resource("s3",region_name="us-east-1",
        aws_access_key_id="ADD YOUR ACCESS KEY ID",
        aws_secret_access_key="ADD YOUR SECRET KEY")
    s3.Object('ADD YOUR BUCKET NAME', fileName).put(Body=fileToUpload)
    
def addToRespSqs(s3OutputPath, messageId):
    sqs = boto3.client("sqs",region_name="us-east-1",
        aws_access_key_id="ADD YOUR ACCESS KEY ID",
        aws_secret_access_key="ADD YOUR SECRET KEY")
    queueUrl = 'RESPONSE QUEUE URL'
    sqs.send_message(
        QueueUrl=queueUrl,
        MessageBody=s3OutputPath,
        MessageAttributes={
            'messageId': {
                'DataType': 'String',
                'StringValue': messageId
            }
        }
    )

def get_instance_id():
    command = 'TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"` && curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id'
    stream = os.popen(command)
    output = stream.read().strip()
    return output.split()

def terminate_ec2(instance_id):
    ec2_client.terminate_instances(InstanceIds=[instance_id])

def getNumberMsgReqQueue():
    try:
        sqs_client = boto3.client('sqs',region_name="us-east-1",
        aws_access_key_id="ADD YOUR ACCESS KEY ID",
        aws_secret_access_key="ADD YOUR SECRET KEY")
        response = sqs_client.get_queue_attributes(
            QueueUrl = 'REQUEST QUEUE URL',
            AttributeNames=['ApproximateNumberOfMessages']
        )
        return int(response['Attributes']['ApproximateNumberOfMessages'])
    except ClientError as e:
        print(f"Error retrieving message count: {e}")
        return -1


def app_tier():
    while True:
        reqQueueMsg = getNumberMsgReqQueue()
        if reqQueueMsg > 0:    
            object = fetchFromReqSqs()
            s3_image_path = object['messageBody']
            messageId = object['messageId']

            # print(s3_image_path,messageId)
            if s3_image_path:
                image_name = s3_image_path.split('/')[-1]
                local_image_path = './' + image_name
                download_image_from_s3(s3_image_path, local_image_path)
                
                # Run the model
                model_output = run_model(local_image_path)
                print(model_output, type(model_output))
                addToRespSqs(model_output, messageId)
                temp = s3_image_path.split('.')[0]
                uploadToS3(model_output, temp)
                instance_id = get_instance_id()
            else:
                print("No image to process")
        elif reqQueueMsg == 0:
            break
    terminate_ec2(instance_id)

if __name__ == '__main__':
    app_tier()

