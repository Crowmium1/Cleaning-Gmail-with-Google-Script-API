import os
import sqlite3
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

# Set the scopes and credentials file
SCOPES = [
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.modify'
    ]
CREDS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
DB_FILE = 'email_senders.db'  

def get_service():
    """Authenticates and returns the Gmail service."""
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

def fetch_senders_from_db():
    """Fetches all unique senders from the emails database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Query the database to get unique senders
    cursor.execute("SELECT DISTINCT sender_email FROM blocked_senders")
    senders = cursor.fetchall()
    conn.close()

    # Flatten the list
    return [sender[0] for sender in senders]

def select_senders_to_block(senders):
    """Displays senders and allows user to select which ones to block."""
    print("\nHere are the unique senders found in the database:\n")
    for i, sender in enumerate(senders, 1):
        print(f"{i}. {sender}")

    selected_indices = input("\nEnter the numbers of the senders you want to block (comma-separated): ")
    selected_indices = [int(i.strip()) - 1 for i in selected_indices.split(",")]

    # Return the selected senders
    return [senders[i] for i in selected_indices]

def create_gmail_filter(service, sender_email):
    """Creates a Gmail filter to automatically delete emails from a specific sender."""
    filter_body = {
        "criteria": {
            "from": sender_email
        },
        "action": {
            "removeLabelIds": ["INBOX"],  # Removes the email from the inbox
            "addLabelIds": ["TRASH"]  # Moves the email to trash
        }
    }

    try:
        service.users().settings().filters().create(userId="me", body=filter_body).execute()
        print(f"Filter created for: {sender_email}")
    except HttpError as error:
        print(f"An error occurred while creating the filter for {sender_email}: {error}")

def move_existing_emails_to_trash(service, sender_email):
    """Moves all existing emails from the specified sender to Trash."""
    try:
        # Search for all messages from the sender
        query = f"from:{sender_email}"
        response = service.users().messages().list(userId='me', q=query).execute()
        messages = response.get('messages', [])

        if not messages:
            print(f"No existing emails from {sender_email} to move to Trash.")
            return

        # Collect all message IDs
        message_ids = [msg['id'] for msg in messages]

        # Use batchModify to move them to Trash
        body = {
            "ids": message_ids,
            "addLabelIds": ["TRASH"],
            "removeLabelIds": ["INBOX"]
        }

        service.users().messages().batchModify(userId='me', body=body).execute()
        print(f"Moved {len(message_ids)} emails from {sender_email} to Trash.")
    except HttpError as error:
        print(f"An error occurred while moving existing emails for {sender_email}: {error}")


def main():
    print("Starting the email blocking process...")

    # Step 1: Get the Gmail service
    service = get_service()

    # Step 2: Fetch unique senders from the database
    senders = fetch_senders_from_db()

    # Step 3: Select which senders to block
    selected_senders = select_senders_to_block(senders)

    # Step 4: Create Gmail filters for the selected senders
    for sender_email in selected_senders:
        create_gmail_filter(service, sender_email)
        move_existing_emails_to_trash(service, sender_email)

    print("Done blocking selected emails!")

if __name__ == "__main__":
    main()