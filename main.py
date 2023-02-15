from __future__ import print_function

import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import storage
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MESSAGE_ID = 'MESSAGE_ID'
BUCKET_NAME = 'pdf_storage'
FILE_NAME = 'attachment_new.csv'


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'],
                                                  q="(is:read OR is:unread) has:attachment filename:csv  "
                                                    "after:2023/02/15").execute()
        messages = results.get('messages', [])


        if not messages:
            print("You have no new messages")
        else:
            MESSAGE_ID = messages[0]['id']
            message = service.users().messages().get(userId="me", id=MESSAGE_ID).execute()
            for part in message['payload']['parts']:
                if part['filename'] and part['filename'].endswith('.csv'):
                    # Download the PDF attachment
                    attachment = service.users().messages().attachments().get(
                        userId='me', messageId=MESSAGE_ID, id=part['body']['attachmentId']).execute()

                    # Decode the attachment data and save to file
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    with open(FILE_NAME, 'wb') as f:
                        f.write(file_data)
                    print(f'Successfully downloaded PDF attachment to {FILE_NAME}!')
                    # storage_client = storage.Client.from_service_account_json('testprojectdmarc-633cf4ca3d02.json')
                    # bucket = storage_client.get_bucket(BUCKET_NAME)
                    # blob = bucket.blob(os.path.basename(FILE_NAME))
                    # blob.upload_from_filename(FILE_NAME)
                    # print(f'Successfully uploaded PDF attachment to gs://{BUCKET_NAME}/{FILE_NAME}!')

            # print(messages)

    #  labels = results.get('labels', [])

    # if not labels:
    #     print('No labels found.')
    #     return
    # print('Labels:')
    # for label in labels:
    #     print(label['name'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
