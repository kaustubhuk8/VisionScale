import boto3
import base64
import time
from botocore.exceptions import ClientError


def getNoOfAppInstances():
    try:
        ec2_client = boto3.client('ec2',region_name="us-east-1",
        aws_access_key_id="ADD YOUR ACCESS KEY ID",
        aws_secret_access_key="ADD YOUR SECRET KEY")
        response = ec2_client.describe_instances(Filters=[
            {'Name': 'image-id', 'Values': ['ami-0936929666ace4c2f']},
            {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'shutting-down', 'stopping']}
        ])
       
        return sum(len(reservation['Instances']) for reservation in response['Reservations'])
    except ClientError as e:
        print(f"Error retrieving instance count: {e}")
        return -1

def create_app_tier_ec2(cnt):
    try:
        ec2_client = boto3.client('ec2',region_name="us-east-1",
        aws_access_key_id="ADD YOUR ACCESS KEY ID",
        aws_secret_access_key="ADD YOUR SECRET KEY") 
        
        user_data_encoded = 'IyEvYmluL2Jhc2gKY2QgL2hvbWUvZWMyLXVzZXIvCnB5dGhvbjMgYXBwX3RpZXIucHk='
        response = ec2_client.run_instances(
            MaxCount=1,
            MinCount=1,
            ImageId='ami-0936929666ace4c2f',
            InstanceType='t2.micro',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': f'app-tier-instance-{cnt}'},
                    ]
                },
            ],
            UserData=user_data_encoded
        )
        return response['Instances'][0]['InstanceId']
    except ClientError as e:
        print(f"Error creating EC2 instance: {e}")
        return None

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

def main():
    while True:
        try:
            noOfAppInstances = getNoOfAppInstances()
            noOfMsgReqQueue = getNumberMsgReqQueue()
            if noOfMsgReqQueue > 0 and noOfMsgReqQueue > noOfAppInstances:
                print(noOfAppInstances, noOfMsgReqQueue)
                if (20 - noOfAppInstances) > 0:
                    instances_needed = min(20 - noOfAppInstances, noOfMsgReqQueue - noOfAppInstances)
                    for i in range(instances_needed):
                        create_app_tier_ec2(i + 1)
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()