import firebase_admin
from firebase_admin import credentials, storage
import re
import os
import json

serviceAccount = os.path.join(os.path.dirname(__file__), ".", "serviceAccount.json")

# Initialize Firebase Admin SDK
# Check if the Firebase Admin SDK is already initialized
if not firebase_admin._apps:
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate(serviceAccount)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'asr-streamlit-6da8e.appspot.com'
    })

# Get a reference to the Firebase Storage bucket
bucket = storage.bucket()


def get_last_string(source_path):
    # Define the regular expression pattern to match the last string after the last "/"
    pattern = r'[^/]+$'
    
    # Use re.search to find the matching substring
    match = re.search(pattern, source_path)
    
    if match:
        # Return the matching substring
        return match.group(0)
    else:
        # If no match is found (no "/" in the path), return the original string
        return source_path
      

def upload_csv_file(csv_content, csv_file_path):
    path = get_last_string(csv_file_path)
    print(csv_file_path)
    # Check if the file already exists in Firebase Storage
    existing_blob = bucket.blob(f"csv_files/{path}")

    # If the file exists, delete it
    if existing_blob.exists():
        existing_blob.delete()
    
    # Convert the CSV content to bytes
    csv_content_bytes = csv_content.encode()
    # Upload the CSV content to Firebase Storage
    blob = bucket.blob(f"csv_files/{path}")
    blob.upload_from_string(csv_content_bytes, content_type='text/csv')
  
def upload_audio_file(audio_file_path):
    path = get_last_string(audio_file_path)
    # Upload the CSV file to Firebase Storage, overwriting the original file
    blob = bucket.blob(f"audio_files/{path}")  # Path to the CSV file in Firebase Storage
    blob.upload_from_filename(audio_file_path)
    print("Audio file uploaded successfully.")

def list_files_in_folder(folder_path):
    # List all files in the specified folder
    blobs = bucket.list_blobs(prefix=f"{folder_path}/")

    # Extract file names from the blobs
    file_names = [blob.name for blob in blobs]

    return file_names

def get_file_in_folder(folder_path):
    if folder_path is None:
        return None, "Folder path is None.", None
    # Get the blob (file) within the specified folder
    path = folder_path.split("/")
    # print(path)
    blob = bucket.get_blob(folder_path)

    if blob is not None:
        return blob.download_as_string(), None, folder_path  # Return the file content as bytes and no error message
    else:
        return None, f"File '{path[1]}' not found in folder '{path[0]}'.", path

# def upload_csv_file(csv_file_path):
#     path = get_last_string(csv_file_path)
#     # Upload the CSV file to Firebase Storage, overwriting the original file
#     blob = bucket.blob(f"csv_files/{path}")  # Path to the CSV file in Firebase Storage
#     blob.upload_from_filename(csv_file_path)
#     print("CSV file uploaded successfully.")

# def download_csv_file(destination_file_path):
#     # Download the CSV file from Firebase Storage
#     blob = bucket.blob(f"csv_files/{destination_file_path}")  # Path to the CSV file in Firebase Storage
#     blob.download_to_filename(f"D:/{destination_file_path}")

#     print("CSV file downloaded successfully.")