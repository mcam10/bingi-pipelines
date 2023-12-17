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
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly", "https://www.googleapis.com/auth/drive.metadata"]

## AWS Globals
ENDPOINT_URL = "http://localhost.localstack.cloud:4566"


def main():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)

    # Call the Drive v3 API
    results = (
        service.files()
        .list(
            pageSize=10, fields="nextPageToken, files(id, name)",
            q="mimeType='application/vnd.google-apps.folder'",
         )   
        .execute()
    )
    items = results.get("files", [])

    dataset = items[0].get('id')

    answers = service.files().list(q = "'" + dataset + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()

    choco = answers.get('files', [])

    for file in choco:
        print('\n',file['name'],file['id'])
        data = service.files().get(fileId=file['id']).execute()
        print(data)


  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")


def list_s3_buckets():
    client = boto3.client('s3', endpoint_url=ENDPOINT_URL)
    response = client.list_buckets()
    print(response)

if __name__ == "__main__":
  main()
  list_s3_buckets()
