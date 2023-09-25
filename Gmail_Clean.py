import os.path
import base64
import json
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Set the scopes and credentials file
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]
CREDS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def get_messages_with_labels(service, user_id, label_ids):
    response = service.users().messages().list(userId=user_id, labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    return messages


def delete_messages(service, user_id, message_ids):
    for message_id in message_ids:
        service.users().messages().trash(userId=user_id, id=message_id['id']).execute()


def main():
    user_id = 'me'
    labels = get_service().users().labels().list(userId=user_id).execute()
    label_map = {label['name']: label['id'] for label in labels['labels']}

    # Assuming 'Promotions' and 'Social' are the labels for your promotional and social inboxes
    promotional_label_id = label_map['CATEGORY_PROMOTIONS']
    social_label_id = label_map['CATEGORY_SOCIAL']

    service = get_service()

    promotional_messages = get_messages_with_labels(service, user_id, [promotional_label_id])
    social_messages = get_messages_with_labels(service, user_id, [social_label_id])

    promotional_message_ids = [{'id': message['id']} for message in promotional_messages]
    social_message_ids = [{'id': message['id']} for message in social_messages]

    delete_messages(service, user_id, promotional_message_ids)
    delete_messages(service, user_id, social_message_ids)


if __name__ == '__main__':
    main()