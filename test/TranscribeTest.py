import os
import time

import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv("./../.env")

aws_default_region = os.getenv("AWS_DEFAULT_REGION")

transcribe = boto3.client('transcribe', region_name=aws_default_region)


def check_job_name(job_name):
    job_verification = True

    # all the transcriptions
    existed_jobs = transcribe.list_transcription_jobs()

    for job in existed_jobs['TranscriptionJobSummaries']:
        if job_name == job['TranscriptionJobName']:
            job_verification = False
            break

    if job_verification == False:
        command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")
        if command.lower() == "y" or command.lower() == "yes":
            transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        elif command.lower() == "n" or command.lower() == "no":
            job_name = input("Insert new job name? ")
            check_job_name(job_name)
        else:
            print("Input can only be (Y/N)")
            command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")
    return job_name


def amazon_transcribe(audio_file_name):
    # Assuming your bucket name is set in the environment variable AWS_S3_BUCKET
    bucket_name = os.getenv("AWS_S3_BUCKET")
    job_uri = f"s3://{bucket_name}/{audio_file_name}"

    job_name = (audio_file_name.split('.')[0]).replace(" ", "")
    file_format = audio_file_name.split('.')[1]

    job_name = check_job_name(job_name)
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat=file_format,
        LanguageCode='en-US')

    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(15)

    if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        df = pd.read_json(uri)
        transcript_text = df['results']['transcripts'][0]['transcript']
        return transcript_text
    else:
        return "Transcription failed"


print(amazon_transcribe("audio_to_transcribe.wav"))
