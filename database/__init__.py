import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage
import pandas as pd
import os
from uuid import uuid4

# serviceAccount = os.path.join(os.path.dirname(__file__), ".", "serviceAccount.json")

storageBucket = "asr-streamlit-6da8e.appspot.com"

# Initialize Firebase Admin SDK
# Check if the Firebase Admin SDK is already initialized
if not firebase_admin._apps:
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate(
        {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"],
            "universe_domain": st.secrets["universe_domain"],
        }
    )
    firebase_admin.initialize_app(cred, {"storageBucket": storageBucket})

# Get a reference to the Firebase Storage bucket
bucket = storage.bucket()


def upload_edited_csv_file(csv_content, csv_file_path):

    bucket_path = f"csv_files/{csv_file_path}"

    # Check if the file already exists in Firebase Storage
    existing_blob = bucket.blob(bucket_path)

    # If the file exists, delete it
    if existing_blob.exists():
        existing_blob.delete()

    # Convert the CSV content to bytes
    csv_content_bytes = csv_content.encode()

    # Upload the CSV content to Firebase Storage
    blob = bucket.blob(bucket_path)

    blob.upload_from_string(csv_content_bytes, content_type="text/csv")

    print("save edited file!")


def upload_csv_files(folder_path):
    # Get the parent folder name
    parent_folder_name = os.path.basename(folder_path)

    # Iterate over the files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            # Read the CSV file into a DataFrame
            file_path = os.path.join(folder_path, file_name)

            df = pd.read_csv(file_path)

            # Add a new column to the DataFrame
            df["audio_link"] = get_audio_link(df, "full_path", parent_folder_name)
            df["raw_text"] = df["text"]  # Example data for the new column

            # Convert the DataFrame back to a CSV string
            modified_csv_content = df.to_csv(index=False)
            csv_content_bytes = modified_csv_content.encode()

            # Define the folder name for Firebase Storage
            folder_name = f"{parent_folder_name}"

            # Upload the modified CSV content to Firebase Storage
            blob = bucket.blob(f"csv_files/{folder_name}/{file_name}")

            blob.upload_from_string(csv_content_bytes, content_type="text/csv")


def name_csv_list(folder_path):
    # List all files in the specified folder
    blobs = bucket.list_blobs(prefix=f"{folder_path}")

    folder_names = set()
    for blob in blobs:
        # Get the path after the prefix
        relative_path = os.path.relpath(blob.name, folder_path)

        # Extract folder name from the relative path
        folder_name = os.path.dirname(relative_path)

        folder_names.add(folder_name)

    if "" in folder_names:
        folder_names.remove("")

    return folder_names


def get_csv_file(folder_path, file):
    if folder_path is None:
        return None, "Folder path is None.", None

    path = folder_path.split("/")

    blob = bucket.get_blob(f"csv_files/{folder_path}/{file}")

    if blob is not None:
        return (
            blob.download_as_string(),
            None,
        )  # Return the file content as bytes and no error message
    else:
        return None, f"File '{path[1]}' not found in folder '{path[0]}'."


def get_audio_link(df, columns, folder_name):
    audio_link = []
    for index, row in df.iterrows():

        audio_path = row[columns].split("/")[-1]

        bucket_path = f"audio_files/{folder_name}/{audio_path}"

        # Get a blob reference to the audio file
        blob = bucket.get_blob(bucket_path)

        # Check if the blob exists
        if not blob.exists():
            audio_link.append(None)
            continue

        # Fetches object metadata
        metadata = blob.metadata

        # Firebase Access Token
        token = metadata["firebaseStorageDownloadTokens"]

        firebase_storageURL = "https://firebasestorage.googleapis.com/v0/b/{}/o/{}?alt=media&token={}".format(
            storageBucket, bucket_path.replace("/", "%2F").replace(" ", "%20"), token
        )

        audio_link.append(firebase_storageURL)

    print(f"len link: {len(audio_link)}")
    print(f"len df: {len(df)}")
    return audio_link


def download_csv_file(destination_file_path):
    # Download the CSV file from Firebase Storage
    blob = bucket.blob(
        f"csv_files/{destination_file_path}"
    )  # Path to the CSV file in Firebase Storage
    
    blob.download_to_filename(f"D:/{destination_file_path}")

    print("CSV file downloaded successfully.")


def upload_audio_files(folder_path):
    # Get the parent folder name
    parent_folder_name = os.path.basename(folder_path)

    # Iterate over the files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".wav"):
            # Read the CSV file into a DataFrame
            file_path = os.path.join(folder_path, file_name)

            # Upload the modified CSV content to Firebase Storage
            bucket_path = f"audio_files/{parent_folder_name}/{file_name}"
            blob = bucket.blob(bucket_path)

            token = uuid4()
            
            metadata = {"firebaseStorageDownloadTokens": token}
            
            # Assign the token as metadata
            blob.metadata = metadata

            blob.upload_from_filename(file_path)

            # Make the file public (OPTIONAL). To be used for Cloud Storage URL.
            blob.make_public()

            print(
                f"{parent_folder_name}/{file_name} : Audio file uploaded successfully."
            )
