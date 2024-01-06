from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle
import os.path

def authenticate_google(): #{{{
    """Authenticate and create a Google Drive API service using a pre-existing token."""
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = None
    token_file = './web/token.pickle'

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
    """
    Upload a file to a specific folder on Google Drive, replacing it if it already exists.

    Args:
    service: Authorized Google Drive service instance.
    file_path (str): Path of the file to upload.
    mime_type (str): MIME type of the file.
    folder_id (str): ID of the folder where the file will be uploaded.
    """
    file_name = os.path.basename(file_path)
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"

    # Search for the file in the specified folder
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])

    # File update (if exists) or upload (if not exists)
    media = MediaFileUpload(file_path, mimetype=mime_type)
    if files:
        # If the file exists, update it
        file_id = files[0].get('id')
        updated_file = service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Updated File ID: {updated_file.get('id')}")
    else:
        # If the file does not exist, upload it
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Uploaded File ID: {file.get('id')}")
#}}}

# Authenticate with Google Drive
service = authenticate_google()

# Example usage: replace '/path/to/your/file.tsv', 'your-folder-id' with your file path and folder ID
tsv_file = './data/Funds2.tsv'
folder_id = '16MN1Dk06bZp42rsVDjtjr77ZX2cZu7uu'
#mime_type =  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' # xlsx mime
mime_type = 'text/tab-separated-values' # tsv mime
upload_file(service,tsv_file, mime_type, folder_id)

