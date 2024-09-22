import sqlite3
import re

DB_FILE = 'emails.db'  # Database file

def is_spam(sender_email, email_count):
    """Basic heuristic to identify spam emails."""
    # Rule 1: Look for common spammy keywords in the email address
    spam_keywords = ['promo', 'newsletter', 'sales', 'offers', 'deals', 'ads', 'no-reply']
    
    if any(keyword in sender_email.lower() for keyword in spam_keywords):
        return True

    # Rule 2: Look for high email counts (more than 20 emails from the same sender)
    if email_count > 20:
        return True

    # Rule 3: Check for specific domains that are known for spam
    spammy_domains = ['xyzpromo.com', 'spammyoffers.com']
    domain = sender_email.split('@')[-1]
    if domain in spammy_domains:
        return True

    return False

def fetch_senders_from_db():
    """Fetches senders and email counts from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Query the database to get sender emails and counts
    cursor.execute("SELECT sender_email, email_count FROM blocked_senders")
    senders = cursor.fetchall()
    conn.close()

    return senders

def analyze_senders():
    """Analyze senders and flag potential spam."""
    senders = fetch_senders_from_db()
    spam_senders = []

    for sender_email, email_count in senders:
        if is_spam(sender_email, email_count):
            spam_senders.append((sender_email, email_count))

    return spam_senders

def main():
    print("Analyzing senders for potential spam...")

    # Analyze and find spammy senders
    spam_senders = analyze_senders()

    if spam_senders:
        print("\nPotential spam senders identified:")
        for sender_email, email_count in spam_senders:
            print(f"Sender: {sender_email}, Emails Received: {email_count}")
    else:
        print("No spam senders detected.")

if __name__ == "__main__":
    main()
