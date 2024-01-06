from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle
import os.path

def authenticate_google(): #{{{
    """Authenticate and create a Google Drive API service using a pre-existing token."""
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = None
    token_file = 'token.pickle'

    # Load the token if it exists
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If the credentials are expired, refresh them
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build('drive', 'v3', credentials=creds)
    return service
#}}}

def upload_file(service, file_path, mime_type, folder_id): #{{{
    """Upload a file to a specific folder on Google Drive."""
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]  # Specify the folder ID here
    }
    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')}")
#}}}

# Authenticate with Google Drive
service = authenticate_google()

# Example usage: replace '/path/to/your/file.xlsx', 'your-folder-id' with your file path and folder ID
xlsx_file = '../data/Funds2.xlsx'
folder_id = '16MN1Dk06bZp42rsVDjtjr77ZX2cZu7uu'
upload_file(service,xlsx_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', folder_id)

