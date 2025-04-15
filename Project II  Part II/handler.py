import os
import imutils
import cv2
import json
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1
from shutil import rmtree
import numpy as np
import torch
import boto3

print('Loading function after lambda 1 is called')

os.environ['TORCH_HOME']='/tmp/'

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion

s3_client = boto3.client('s3',region_name="us-east-1",
    aws_access_key_id="ADD YOUR ACCESS KEY ID",
    aws_secret_access_key="ADD YOUR SECRET KEY")

def handler(event, context):
    # Get the object from the event and show its content type
    print('Event fileName->',event['fileName'])
    print('Event type', type(event))
    # bucket_name = event['bucket_name']
    fileName = event['fileName']
    
    download_files(fileName)
    filePath = f'/tmp/{fileName}'

    outFileName = fileName.split('.')[0] + '.txt'
    output = face_recognition_function(filePath)
    outFilePath = f'/tmp/{outFileName}'
    print('Output', output)

    uploadToS3(outFileName, outFilePath)


def uploadToS3(fileName, outFilePath):    
    s3_client.upload_file(outFilePath,'ADD YOUR BUCKET NAME', fileName)
    print('Uploaded: ', fileName)
    
def download_files(filename): 
    s3_client.download_file('ADD YOUR BUCKET NAME', 'data.pt', f'/tmp/data.pt')
    print('Downloaded: data.pt')
    s3_client.download_file('ADD YOUR BUCKET NAME', filename, f'/tmp/{filename}')
    print('Downloaded: ',filename)

def face_recognition_function(key_path):
    print('Inside FR')
    # Face extraction
    img = cv2.imread(key_path, cv2.IMREAD_COLOR)
    boxes, _ = mtcnn.detect(img)

    # Face recognition
    key = os.path.splitext(os.path.basename(key_path))[0].split(".")[0]
    print('Key: ', key)
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    face, prob = mtcnn(img, return_prob=True, save_path=None)
    saved_data = torch.load('/tmp/data.pt')  # loading data.pt file
    print('Loaded data.pt: ', saved_data)
    if face != None:
        emb = resnet(face.unsqueeze(0)).detach()  # detech is to make required gradient false
        embedding_list = saved_data[0]  # getting embedding data
        name_list = saved_data[1]  # getting list of names
        dist_list = []  # list of matched distances, minimum distance is used to identify the person
        for idx, emb_db in enumerate(embedding_list):
            dist = torch.dist(emb, emb_db).item()
            dist_list.append(dist)
        idx_min = dist_list.index(min(dist_list))

        # Save the result name in a file
        with open("/tmp/" + key + ".txt", 'w+') as f:
            f.write(name_list[idx_min])
        return name_list[idx_min]
    else:
        print(f"No face is detected")
    return
