# import os libs
import os.path

#google drive libs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

#import aws libs
#import boto3
import json
import localstack_client.session as boto3


## Gdrive Globals
# If modifying these scopes, delete the file token.json:
SCOPES = ["https://www.googleapis.com/auth/drive.metadata", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.metadata.readonly"]

## AWS Globals
ENDPOINT_URL = "http://localhost.localstack.cloud:4566"

client = boto3.client('s3')

s3 = boto3.client('s3')

BUCKET_NAME="project-choco"

def authenticate_google_drive(token, credentials):

  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(token):
    creds = Credentials.from_authorized_user_file(token, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          credentials, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token, "w") as token:
      token.write(creds.to_json())

  return creds

def get_drive_id(service):

    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name, description)",
                                  q="mimeType='application/vnd.google-apps.folder'",
                                  ).execute()
    
    list_of_folders = results.get('files')

    for folder in list_of_folders:
        if folder['name'] == 'Dataset':
           dataset_drive_id = folder['id'] 
    else: 
        'Not found'
    
    return dataset_drive_id

def query_for_folder_id(service, drive_id):

    query_for_files = service.files().list(q = "'" + drive_id + "' in parents",
                                        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    
    list_of_files = query_for_files.get('files', [])                                        

# uh oh double nested for loop o(N)^2

    for file in list_of_files:
        response = service.files().list(q="'" + file['id'] + "' in parents", pageSize=1000,fields="nextPageToken, files(id, name, description)").execute()
        chocolate_images  = response.get('files',[])

        for img in chocolate_images:
            score_folders = service.files().get_media(fileId=img['id'])
            score_name = f'{img["name"]}'
            print( file['name'], score_name)
"""          
       with open(file_name, "wb") as fh:
           downloader = MediaIoBaseDownload(fh, request)
           done = False
           while not done:
                 status, done = downloader.next_chunk()
#                  file_path = os.path.join(file['name'], file_name)
#                    s3.upload_file(file_name, BUCKET_NAME, file['name'])
            #print(f"({file['name']}: {p}")
"""

def list_s3_buckets():
    pass

if __name__ == "__main__":
    creds = authenticate_google_drive("token.json", "credentials.json")
    service = build("drive", "v3", credentials=creds)
    drive_id = get_drive_id(service)
    folders = query_for_folder_id(service, drive_id)

#  list_s3_buckets()
