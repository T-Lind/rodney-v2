import os

import boto3
from dotenv import load_dotenv

load_dotenv("./../.env")

aws_default_region = os.getenv("AWS_DEFAULT_REGION")

# Initialize the Rekognition client
rekognition_client = boto3.client('rekognition', region_name=aws_default_region)


def detect_faces_in_image(image_path):
    with open(image_path, 'rb') as image:
        response = rekognition_client.detect_faces(
            Image={'Bytes': image.read()},
            Attributes=['ALL']
        )
    return response['FaceDetails']


# Use the function
image_path = r'C:\Users\tenant\PycharmProjects\rodney-v2\test\image.jpg'
faces = detect_faces_in_image(image_path)

for face in faces:
    print(face)
