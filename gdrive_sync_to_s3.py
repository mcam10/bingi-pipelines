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

def get_credentials(token, credentials):

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

  try:
    service = build("drive", "v3", credentials=creds)
  except:
    print("error has occured")


def get_files_drives():
   pass 


'''

#def main():
    response = (
        service.files()
        .list(
           pageSize=10, fields="nextPageToken, files(id, name, description)",
            q="mimeType='application/vnd.google-apps.folder'",
        )
        .execute()
    )

    items = response.get('files', [])

    for item in items:
        if item['name'] == 'Dataset':
            dataset_drive_id = (item['id'])

#lets statrt the query for the folders in dataset folde -- need to refactor and dry it up.. functional programmingr    
    answers = service.files().list(q = "'" + dataset_drive_id + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()

    choco = answers.get('files', [])

    for file in choco:
# get the list of folders in dataset folder
        print('\n',file['name'],file['id'])
        response = service.files().list(q="'" + file['id'] + "' in parents", pageSize=1000,fields="nextPageToken, files(id, name)").execute()
        items.extend(response.get('files', []))
        pageToken = response.get('nextPageToken')

  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")

#need to come back to this -- add this to a list of tests that we can run.. pytest mocking calls to the cloud.. setup test suite to test functionality. Github Actions to test
def list_s3_buckets():
    client = boto3.client('s3', endpoint_url=ENDPOINT_URL)
    response = client.list_buckets.get('Buckets')
    print(response)
'''
if __name__ == "__main__":
    get_credentials("token.json","credentials.json")
#  main()

#  list_s3_buckets()
