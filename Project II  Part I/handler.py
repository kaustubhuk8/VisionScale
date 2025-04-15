
import json
import urllib.parse
import boto3
import os
import subprocess
import math
import time

print('Loading function')

output_bucket_name = 'ADD YOUR BUCKET NAME'

lambda_client = boto3.client('lambda',region_name="us-east-1",
    aws_access_key_id="ADD YOUR ACCESS KEY ID",
    aws_secret_access_key="ADD YOUR SECRET KEY")

s3 = boto3.resource("s3",region_name="us-east-1",
    aws_access_key_id="ADD YOUR ACCESS KEY ID",
    aws_secret_access_key="ADD YOUR SECRET KEY")

s3_client = boto3.client('s3',region_name="us-east-1",
aws_access_key_id="ADD YOUR ACCESS KEY ID",
aws_secret_access_key="ADD YOUR SECRET KEY")

def handler( event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    s3_client.download_file(bucket, key, f'/tmp/{key}')
    print('Downloaded: ', key)

    video_filename = f'/tmp/{key}'
    outfile = key.split('.')[0] + '.jpg'
    
    command = '/usr/bin/ffmpeg -i ' + video_filename + ' -vframes 1 ' + f'/tmp/{outfile}'
    stream = os.popen(command)
    output = stream.read()

    s3_client.upload_file(f'/tmp/{outfile}', output_bucket_name, outfile)
    print(f'Uploaded: {outfile}')
    payload = {'bucket_name':output_bucket_name,'fileName': outfile}
    lambda_client.invoke(FunctionName = 'ADD YOUR FUNCTION NAME', InvocationType = 'RequestResponse', Payload = json.dumps(payload) )
    print("Invoked Lambda 2")