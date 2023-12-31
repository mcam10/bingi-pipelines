# import os libs
import os.path

#google drive libs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#import aws libs
import boto3

## Gdrive Globals
# If modifying these scopes, delete the file token.json:
SCOPES = ["https://www.googleapis.com/auth/drive.metadata", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.metadata.readonly"]

## AWS Globals
ENDPOINT_URL = "http://localhost.localstack.cloud:4566"

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


def get_dataset_files():
    
    # Authenticate Google Drive
    creds = authenticate_google_drive("token.json", "credentials.json")
    # Connect to Google Drive API
    service = build("drive", "v3", credentials=creds)
     # Get the list of files 
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name, description)",
                                  q="mimeType='application/vnd.google-apps.folder'",
                                  ).execute()

    list_of_folders = results.get('files', [])

    for folder in list_of_folders:
        if folder['name'] == 'Dataset':
           dataset_drive_id = folder['id'] 
    else: 
        'Not found'

    query_for_files = service.files().list(q = "'" + dataset_drive_id + "' in parents",
                                        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    
    list_of_files = query_for_files.get('files', [])                                        

    for file in list_of_files:
        response = service.files().list(q="'" + file['id'] + "' in parents", pageSize=1000,fields="nextPageToken, files(id, name, description)").execute()
        poop = response.get('files',[])
        for p in poop:
            print(f"({file['name']}: {p}")

def get_list_of_files():
    pass
    
def list_s3_buckets():
    client = boto3.client('s3', endpoint_url=ENDPOINT_URL)
    response = client.list_buckets.get('Buckets')
    print(response)
'''
if __name__ == "__main__":
    get_dataset_files()
#  main()

#  list_s3_buckets()
