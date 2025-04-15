import boto3
from flask import Flask, request, jsonify
import time
import threading
import os

app = Flask(__name__)

maa = []

def uploadToS3(fileToUpload, fileName):
    s3 = boto3.resource("s3", aws_access_key_id="ADD YOUR ACCESS KEY ID",region_name="us-east-1",
        aws_secret_access_key="ADD YOUR SECRET KEY")
    s3.Bucket('ADD YOUR BUCKET NAME').upload_fileobj(fileToUpload, fileName)
    return fileName

def addToReqSqs(s3Path):
    sqs = boto3.client("sqs",aws_access_key_id="ADD YOUR ACCESS KEY ID",region_name="us-east-1",
        aws_secret_access_key="ADD YOUR SECRET KEY")
    queueUrl = 'REQUEST QUEUE URL'
    response = sqs.send_message(QueueUrl=queueUrl, MessageBody=s3Path)
    return response['MessageId']

# def fetchFromRespSqs(req_msg_id):
#     sqs = boto3.client("sqs",aws_access_key_id="ADD YOUR ACCESS KEY ID",
#         aws_secret_access_key="ADD YOUR SECRET KEY")
#     queueUrl = 'RESPONSE QUEUE URL'
#     while True:
#         messages = sqs.receive_message(QueueUrl=queueUrl, MessageAttributeNames=['All'])
#         if 'Messages' in messages:
#             message = messages['Messages'][0]
#             receipt_handle = message['ReceiptHandle']
#             resp_msg_id = message['MessageAttributes']['messageId']['StringValue']
#             if req_msg_id == resp_msg_id:
#             # Delete received message from queue
#                 sqs.delete_message(QueueUrl=queueUrl, ReceiptHandle=receipt_handle)
#                 return message['Body']
#         time.sleep(1)  # Wait for 5 seconds before polling again

def fetchFromRespSqs(req_msg_id):
    sqs = boto3.client("sqs",aws_access_key_id="ADD YOUR ACCESS KEY ID",region_name="us-east-1",
        aws_secret_access_key="ADD YOUR SECRET KEY")
    queueUrl = 'RESPONSE QUEUE URL'
    if maa:
        while True:
            for i in maa:
                if i['resp_msg_id'] == req_msg_id:
                    
                    sqs.delete_message(QueueUrl=queueUrl, ReceiptHandle=i['receipt_handle'])
                    return i['body']
            time.sleep(0.2)
              
        
def runThread():
    while True:
        sqs = boto3.client("sqs",aws_access_key_id="ADD YOUR ACCESS KEY ID",region_name="us-east-1",
            aws_secret_access_key="ADD YOUR SECRET KEY")
        queueUrl = 'RESPONSE QUEUE URL'
        messages = sqs.receive_message(QueueUrl=queueUrl, MessageAttributeNames=['All'], VisibilityTimeout=300, MaxNumberOfMessages=10)
        global maa
        print(messages)
        if 'Messages' in messages:
            for i in (messages['Messages']):
                    mapofmsg= {}
                    mapofmsg['receipt_handle'] = i['ReceiptHandle']
                    mapofmsg['resp_msg_id'] = i['MessageAttributes']['messageId']['StringValue']
                    mapofmsg['body'] = i['Body']
                    maa.append(mapofmsg)
                    print(maa)
       

@app.route('/', methods=['POST'])
def handle_request():
    file = request.files['inputFile']
    s3Path = uploadToS3(file, file.filename)
    req_msg_id = addToReqSqs(s3Path)
    fileName = file.filename.split('.')[0]
    response = fetchFromRespSqs(req_msg_id)
    return f'{fileName}:{response}'

if __name__ == '__main__':
    controller_thread = threading.Thread(target=runThread)
    controller_thread.daemon = True
    controller_thread.start()
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
