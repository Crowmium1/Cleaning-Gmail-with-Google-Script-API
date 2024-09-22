# Cleaning-Gmail

Cleaning-Gmail-with-Google-Script-API 

Option for filtering emails from spam include:
1. Manual Gmail Filters
2. CSV/Spreadsheet-Based Blacklist
3. Database for Managing Blacklisted Senders
4. Email Management Services or Plugins like Unroll.Me
5. Email Client Rules and Automation You can create rules or automation tasks within your email client to move, block, or delete emails from specific senders as they arrive.

Selected Option: 3
Sender_get.py
•	Authenticate and return the Gmail service
•	Define the Database Structure
•	Fetch the information from the folder(s)
•	Parse the Sender Information: Sender: Google Calendar <calendar-notification@google.com>, Count: 4
•	Store Data in SQLite Database
•	Regular Updates and De-Duplication: Implement logic to update the database whenever new emails are fetched
Use the DB browser for SQLite 
•	Querying and Viewing the Data
•	Create a new database with the blocked sender list
Blocked.py
•	Upload this new database into blocked.py
•	Authenticate and return the Gmail service
•	Fetch from database
•	Select senders to block: Displays senders numbered and allows user to select which ones to block via terminal (comma-separated).
•	Create Gmail filter: Creates a Gmail filter to automatically delete emails from a specific sender
•	Move all selected emails to trash: Separate function that moves all existing emails from the specified sender to Trash.

Where I am:
The question now is selecting from the terminal which ones to delete or selecting from the database the most efficient approach. Perhaps doing analysis on the content of the emails by isolating keywords or going deeper and using machine learning for analysis for the identification of spam. Well, I do have a very good model I can use for this exact purpose which uses machine learning. There is also the pen and paper approach of manually going through the Inbox. 

What next:
Let's go with the pen/paper approach and it into a python list, which feeds into the database accessed in blocked.py. This list can be updated periodically. Additionally, pull all senders from the Spam folder into the list.
Run the filter and move functions to put the spam emails in the trash. Gmail has a delete all trash button.
This whole project can be automated and run on a schedule. The list will still need to be updated periodically.
