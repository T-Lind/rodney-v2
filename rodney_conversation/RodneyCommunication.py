import os
import uuid
import boto3
import pyaudio
from dotenv import load_dotenv
from pandas import read_json

from rodney_ai.Chatbot import Chatbot
from rodney_conversation.printf import printf
from rodney_conversation.prompts.PromptUtil import initial_convo_prompt

load_dotenv("./../.env")

aws_default_region = os.getenv("AWS_DEFAULT_REGION")


class RodneyCommunication:
    def __init__(self, directive):
        self.polly_client = boto3.client('polly', region_name=aws_default_region)
        self.transcribe = boto3.client('transcribe', region_name=aws_default_region)
        self.s3_client = boto3.client('s3', region_name=aws_default_region)
        self.chatbot = Chatbot(temperature=0.5)
        self.directive = directive

    def check_job_name(self, job_name):
        job_verification = True

        # all the transcriptions
        existed_jobs = self.transcribe.list_transcription_jobs()

        for job in existed_jobs['TranscriptionJobSummaries']:
            if job_name == job['TranscriptionJobName']:
                job_verification = False
                break

        if not job_verification:
            raise BufferError("Job verification is false!")
            # command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")
            # if command.lower() == "y" or command.lower() == "yes":
            #     self.transcribe.delete_transcription_job(TranscriptionJobName=job_name)
            # elif command.lower() == "n" or command.lower() == "no":
            #     job_name = input("Insert new job name? ")
            #     self.check_job_name(job_name)
            # else:
            #     print("Input can only be (Y/N)")
            #     command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")
        return job_name

    def amazon_transcribe(self, audio_file_path):
        # Generate a unique file name
        unique_filename = f"{str(uuid.uuid4())}.wav"

        # Upload the audio file to S3
        bucket_name = os.getenv("AWS_S3_BUCKET")
        self.s3_client.upload_file(audio_file_path, bucket_name, unique_filename)

        # Construct the S3 URI for the uploaded audio file
        audio_file_uri = f"s3://{bucket_name}/{unique_filename}"

        # Generate a unique job name using the unique filename
        job_name = self.check_job_name(unique_filename)

        # Start the transcription job
        self.transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': audio_file_uri},
            MediaFormat='wav',  # Change this to the actual format if needed
            LanguageCode='en-US')

        # Monitor the transcription job status
        while True:
            result = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break

        if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
            response = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
            df = read_json(uri)
            transcript_text = df['results']['transcripts'][0]['transcript']
            return transcript_text
        else:
            return "Transcription failed"

    def play_speech_from_polly(self, text, voice_id="Matthew"):
        response = self.polly_client.synthesize_speech(Text=text,
                                                       OutputFormat='pcm',
                                                       VoiceId=voice_id,
                                                       )

        # Play audio directly
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(width=2),  # 2 bytes = 16 bits
                        channels=1,
                        rate=16000,  # Amazon Polly returns PCM audio at 16kHz
                        output=True)
        stream.write(response['AudioStream'].read())
        stream.stop_stream()
        stream.close()
        p.terminate()

    def voice_conversation(self, verbose=False):
        initial_prompt = initial_convo_prompt(self.directive)
        if verbose:
            printf(f"Initial prompt:\n{initial_prompt}", color="green", type="italic")

        # Play the initial prompt
        rodneys_introduction = self.chatbot.ask(initial_prompt)

        if verbose:
            printf(f"\nResponse:\n{rodneys_introduction}", color="red", type="italic")
        self.play_speech_from_polly(rodneys_introduction)
