import boto3
import time
import urllib
import json
import os

transcribe_client = boto3.client('transcribe')
s3 = boto3.client('s3')
# here you can change the folder from wich you're gonna upload your files
n_clips = os.listdir("D:\\Documents\\transcibe\\New folder")
audioBucket = "translatebucketvincent"  # the destiny bucket for your files

# Transcription function


def transcribe_file(job_name, file_uri, transcribe_client):
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='mp4',
        LanguageCode='en-US'
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                response = urllib.request.urlopen(
                    job['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                data = json.loads(response.read())
                text = data['results']['transcripts'][0]['transcript']
                print(
                    "========== below is output of speech-to-text ========================")
                print(text)
                print(
                    "=====================================================================")
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)

# Main Function


def main():
    count = 0
    for i in range(len(n_clips)):
        print(n_clips[i])
        s3.upload_file(
            f"D:\\Documents\\transcibe\\New folder\{n_clips[i]}", audioBucket, f"clip{i}")  # Put here the folder + files that you're adding, and also the bucket

    objects = s3.list_objects(Bucket=audioBucket)["Contents"]
    for object in objects:
        key = object["Key"]
        url = f"https://{audioBucket}.s3.amazonaws.com/{key}"
        print(url)

        file_uri = url  # start transcribing
        transcribe_file(f'Example-job{count}', file_uri, transcribe_client)
        count += 1


if __name__ == '__main__':
    main()
