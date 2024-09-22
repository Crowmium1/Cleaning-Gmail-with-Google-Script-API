import os.path
import base64
import json
import re
import time
import random
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

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
    messages = []
    response = None
    try:
        response = service.users().messages().list(userId=user_id, labelIds=label_ids, maxResults=500).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

    while 'messages' in response:
        messages.extend(response['messages'])
        if 'nextPageToken' in response:
            try:
                print(f"Fetching next batch of messages with token: {response['nextPageToken']}")
                response = service.users().messages().list(userId=user_id, labelIds=label_ids, pageToken=response['nextPageToken'], maxResults=500).execute()
            except HttpError as error:
                print(f"An error occurred while fetching the next batch: {error}")
                break
        else:
            break

    return messages

def delete_messages(service, user_id, message_ids):
    max_retries = 5  # Number of retry attempts
    for message_id in message_ids:
        retries = 0
        while retries < max_retries:
            try:
                service.users().messages().trash(userId=user_id, id=message_id['id']).execute()
                print(f"Deleted message {message_id['id']}")
                break  # Exit retry loop on success
            except HttpError as error:
                if error.resp.status in [429, 500, 503]:
                    retries += 1
                    wait_time = (2 ** retries) + (random.uniform(0, 1))  # Exponential backoff with jitter
                    print(f"Rate limit or server error (status: {error.resp.status}). Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    # Other errors should not be retried
                    print(f"Failed to delete message {message_id['id']}. Error: {error}")
                    break

            if retries == max_retries:
                print(f"Failed to delete message {message_id['id']} after {max_retries} retries.")

def main():
    user_id = 'me'
    
    print("Getting Gmail service...")
    service = get_service()
    
    print("Fetching labels...")
    labels = service.users().labels().list(userId=user_id).execute()
    label_map = {label['name']: label['id'] for label in labels['labels']}
    
    if 'CATEGORY_PROMOTIONS' not in label_map or 'CATEGORY_SOCIAL' not in label_map or 'CATEGORY_UPDATES' not in label_map:
        print("Error: One or more required labels ('CATEGORY_PROMOTIONS', 'CATEGORY_SOCIAL', 'CATEGORY_UPDATES') not found.")
        return
    
    promotional_label_id = label_map['CATEGORY_PROMOTIONS']
    social_label_id = label_map['CATEGORY_SOCIAL']
    updates_label_id = label_map['CATEGORY_UPDATES']

    # Fetch and delete promotional messages
    print("Fetching promotional messages...")
    promotional_messages = get_messages_with_labels(service, user_id, [promotional_label_id])
    print(f"Found {len(promotional_messages)} promotional messages.")
    promotional_message_ids = [{'id': message['id']} for message in promotional_messages]
    print("Deleting promotional messages...")
    delete_messages(service, user_id, promotional_message_ids)

    # Fetch and delete social messages
    print("Fetching social messages...")
    social_messages = get_messages_with_labels(service, user_id, [social_label_id])
    print(f"Found {len(social_messages)} social messages.")
    social_message_ids = [{'id': message['id']} for message in social_messages]
    print("Deleting social messages...")
    delete_messages(service, user_id, social_message_ids)

    # Fetch and delete updates messages
    print("Fetching updates messages...")
    updates_messages = get_messages_with_labels(service, user_id, [updates_label_id])
    print(f"Found {len(updates_messages)} updates messages.")
    updates_message_ids = [{'id': message['id']} for message in updates_messages]
    print("Deleting updates messages...")
    delete_messages(service, user_id, updates_message_ids)

    print("Done!")

if __name__ == '__main__':
    main()