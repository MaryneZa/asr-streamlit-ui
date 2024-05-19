import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage
import pandas as pd
import os
from uuid import uuid4
import math
from io import BytesIO, StringIO

# from io import StringIO


# serviceAccount = os.path.join(os.path.dirname(__file__), ".", "serviceAccount.json")

storageBucket = st.secrets["storageBucket"]

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


def upload_csv_files(folder_path, group_size):
    """
    Upload CSV files from a local folder to Firebase Storage after modifying them.

    Args:
        folder_path (str): The path of the local folder containing the CSV files.
        group_size (int): The size of each group for grouping CSV files.

    Returns:
        None

    Raises:
        FileNotFoundError: If the specified folder path does not exist.
        ValueError: If the folder_path is None or invalid, or if group_size is not positive.
        IOError: If there are issues reading, modifying, or uploading the CSV files to Firebase Storage.
    """
    try:
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"The folder path '{folder_path}' does not exist.")
        # Get the parent folder name
        parent_folder_name = os.path.basename(folder_path)
        folder_name = f"{parent_folder_name}"

        files = {}

        # Iterate over the files in the folder
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                # Read the CSV file into a DataFrame
                file_path = os.path.join(folder_path, file_name)

                df = pd.read_csv(file_path)
                len_df = len(df)
                # Add a new column to the DataFrame
                df["audio_link"] = get_audio_link(df, "full_path", parent_folder_name)
                df["raw_text"] = df["text"]  # Example data for the new column

                df["multi_speaker"] = [False] * len_df
                df["loud_noise"] = [False] * len_df
                df["unclear"] = [False] * len_df
                df["incomplete_sentence"] = [False] * len_df

                df["edit_status"] = [False] * len_df

                files[file_name] = df
                print(f"len {file_name} : {len(df)}")
        df_get_group, total_group = get_group(files, group_size)

        group_data = {}  # Dictionary to accumulate data for each group

        # Iterate over each file and accumulate data for each group
        for df_key, df in files.items():
            df["group"] = df_get_group[df_key]

            for i in range(total_group + 1):
                df_group = df[df["group"] == i]
                if not df_group.empty:
                    group_data.setdefault(i, []).append(df_group)

        # Now, upload the accumulated data for each group to Firebase Storage
        for i, data_list in group_data.items():
            # Concatenate all DataFrames in the list for the same group
            combined_df = pd.concat(data_list)

            print(f"group: {i}, len: {len(combined_df)}")

            # Convert the combined DataFrame back to a CSV string
            modified_csv_content = combined_df.to_csv(index=False)
            csv_content_bytes = modified_csv_content.encode()

            # Upload the modified CSV content to Firebase Storage
            blob = bucket.blob(f"csv_files/{folder_name}/group_{i}.csv")
            blob.upload_from_string(csv_content_bytes, content_type="text/csv")

        for df_key, df in files.items():
            df["group"] = df_get_group[df_key]
            # Convert the DataFrame back to a CSV string
            modified_csv_content = df.to_csv(index=False)
            csv_content_bytes = modified_csv_content.encode()

            # Define the folder name for Firebase Storage
            folder_name = f"{parent_folder_name}"

            # Upload the modified CSV content to Firebase Storage
            blob = bucket.blob(f"csv_files/{folder_name}/{df_key}")

            blob.upload_from_string(csv_content_bytes, content_type="text/csv")

        print("Upload csv files successfully !")

    except Exception as e:
        print("An error occurred:", e)


def upload_edited_csv_file(csv_content, csv_file_path):
    """
    Upload edited CSV content to Firebase Storage.

    Args:
        csv_content (str): The edited CSV content as a string.
        csv_file_path (str): The path of the CSV file on Firebase Storage.

    Returns:
        None

    Raises:
        ValueError: If the provided CSV content or file path is None or empty.
        IOError: If there are issues uploading the CSV content to Firebase Storage.
    """
    try:
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

    except Exception as e:
        print("An error occurred:", e)


def upload_audio_files(folder_path):
    """
    Upload audio files (.wav) from a local folder to Firebase Storage.

    Args:
        folder_path (str): The path of the local folder containing the audio files.

    Returns:
        None

    Raises:
        FileNotFoundError: If the specified folder path does not exist.
        ValueError: If the folder_path is None or invalid.
        IOError: If there are issues uploading the audio files to Firebase Storage.
    """
    try:
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"The folder path '{folder_path}' does not exist.")
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
    except Exception as e:
        print("An error occurred:", e)


def get_group(files, group):
    """Split files into groups based on group size.

    Args:
        files (dict): A dictionary containing file names as keys and DataFrames as values.
        group (int): The size of each group.

    Raises:
        TypeError: If files is not a dictionary or group is not an integer.
        ValueError: If group is not positive.

    Returns:
        dict: A dictionary containing file names as keys and grouped DataFrames as values.
    """
    try:
        len_train = len(files["train.csv"])
        len_val = len(files["val.csv"])
        arr = [0] * (len_train + len_val)

        # Calculate total number of groups and assign group numbers to the array
        total_group = math.ceil(len(arr) / group)
        for i in range(total_group):
            print(f"i : {i}")
            start_idx = i * group
            end_idx = min(start_idx + group, len(arr))
            arr[start_idx:end_idx] = [i + 1] * (end_idx - start_idx)

        # Split array into train and val DataFrames
        df_dict = {}
        df_dict["train.csv"] = pd.DataFrame(arr[:len_train], columns=["group"])
        df_dict["val.csv"] = pd.DataFrame(arr[len_train:], columns=["group"])

        return df_dict, total_group

    except Exception as e:
        print("An error occurred:", e)


def name_csv_list(folder_path):
    """
    List the names of CSV files in a specified folder path on Firebase Storage.

    Args:
        folder_path (str): The path of the folder containing the CSV files on Firebase Storage.

    Returns:
        set: A set containing the names of CSV files found in the specified folder.

    Raises:
        ValueError: If the folder_path is None or invalid.
        IOError: If there are issues listing the CSV files.
    """
    try:
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
    except Exception as e:
        print("An error occurred:", e)


def name_csv_group_list(folder_path):
    """
    List the names of CSV files in a specified folder path on Firebase Storage.

    Args:
        folder_path (str): The path of the folder containing the CSV files on Firebase Storage.

    Returns:
        set: A set containing the names of CSV files found in the specified folder.

    Raises:
        ValueError: If the folder_path is None or invalid.
        IOError: If there are issues listing the CSV files.
    """
    try:
        # List all files in the specified folder
        blobs = bucket.list_blobs(prefix=f"{folder_path}")
        folder_names = set()

        for blob in blobs:
            # Get the path after the prefix
            relative_path = os.path.relpath(blob.name, folder_path)
            # Extract folder name from the relative path
            if relative_path not in ["", "train.csv", "val.csv"]:
                folder_names.add(relative_path)

        return folder_names

    except Exception as e:
        print("An error occurred:", e)


def get_csv_file(folder_path, file):
    """
    Get the content of a CSV file from Firebase Storage.

    Args:
        folder_path (str): The path of the folder containing the CSV file on Firebase Storage.
        file (str): The name of the CSV file to retrieve.

    Returns:
        tuple or bytes or None: If successful, returns a tuple containing the file content as bytes,
            an informative message, and any additional data. If the file does not exist, returns None.

    Raises:
        ValueError: If the folder_path is None.
        IOError: If there are issues retrieving the CSV file.
    """
    try:
        if folder_path is None:
            return None, "Folder path is None.", None

        blob = bucket.get_blob(f"csv_files/{folder_path}/{file}")

        if blob is not None:
            return (
                blob.download_as_string()
            )  # Return the file content as bytes and no error message
        else:
            return None

    except Exception as e:
        print("An error occurred:", e)


def get_audio_link(df, columns, folder_name):
    """Get download links for audio files stored in a cloud bucket.

    Args:
        df (DataFrame): DataFrame containing audio file information.
        columns (str or list of str): Name(s) of the column(s) containing the audio file paths.
        folder_name (str): Name of the folder where audio files are stored in the bucket.

    Raises:
        KeyError: If the specified column(s) do not exist in the DataFrame.
        ValueError: If the specified folder name is invalid or if the DataFrame is empty.

    Returns:
        list: A list containing download links for each audio file.
    """
    try:
        audio_link = []
        for index, row in df.iterrows():

            audio_path = row[columns].split("/")[-1]

            bucket_path = f"audio_files/{folder_name}/{audio_path}"

            # Get a blob reference to the audio file
            blob = bucket.get_blob(bucket_path)

            # Check if the blob exists
            if not blob.exists():
                print(f"{bucket_path} : not found")
                audio_link.append(None)
                continue

            # Fetches object metadata
            metadata = blob.metadata

            # Firebase Access Token
            token = metadata["firebaseStorageDownloadTokens"]

            firebase_storageURL = "https://firebasestorage.googleapis.com/v0/b/{}/o/{}?alt=media&token={}".format(
                storageBucket,
                bucket_path.replace("/", "%2F").replace(" ", "%20"),
                token,
            )

            audio_link.append(firebase_storageURL)

        print(f"len audio link ({folder_name}): {len(audio_link)}")
        print(f"len df ({folder_name}): {len(df)}")
        return audio_link

    except Exception as e:
        print("An error occurred:", e)


def download_csv_file(remote_file_path, local_destination_folder):
    """
    Download a CSV file from Firebase Storage to the specified local folder.

    Parameters:
        remote_file_path (str): The path of the CSV file on Firebase Storage.
        local_destination_folder (str): The local folder where the CSV file will be downloaded.

    Raises:
        ValueError: If the remote file path or local destination folder is invalid.
        FileNotFoundError: If the CSV file does not exist in the specified remote location.
        IOError: If there are issues downloading the CSV file.

    Returns:
        None
    """
    try:
        # Download the CSV file from Firebase Storage
        blob = bucket.blob(
            f"csv_files/{remote_file_path}"  # Path to the CSV file in Firebase Storage
        )

        # Split the remote_file_path to get the file name
        file_name = ("_").join(remote_file_path.split("/"))

        # Concatenate the destination directory and file name
        local_file_path = f"{local_destination_folder}/{file_name}"

        # Download the file to the correct local directory
        blob.download_to_filename(local_file_path)

        print("CSV file downloaded successfully.")
    except Exception as e:
        print("An error occurred:", e)


def concat_csv_files_for_downloading(remote_file_path, local_destination_folder):
    """
    Concatenate CSV files from Firebase Storage and save them to the specified local folder.

    This function downloads all CSV files from a specified folder in Firebase Storage,
    concatenates them, sorts by the "group" column, and then splits the concatenated DataFrame
    into train and validation sets based on their respective lengths.

    Parameters:
        remote_file_path (str): The path of the folder containing CSV files on Firebase Storage.
        local_destination_folder (str): The local folder where the concatenated CSV files will be saved.

    Raises:
        ValueError: If the remote file path or local destination folder is invalid.
        FileNotFoundError: If there are no CSV files in the specified remote location.
        IOError: If there are issues downloading the CSV files or saving them locally.

    Returns:
        None
    """

    # Initialize an empty list to store DataFrame objects
    dfs = []
    len_train = 0
    len_val = 0
    cnt_row = 0
    # Iterate through each blob in the specified folder
    blobs = bucket.list_blobs(prefix=f"csv_files/{remote_file_path}")

    for blob in blobs:
        # Check if the blob is a CSV file
        if blob.name.endswith(".csv"):
            # Download the CSV file contents
            blob_content = blob.download_as_string()

            # Convert the CSV file contents to a DataFrame
            df = pd.read_csv(StringIO(blob_content.decode()))
            if blob.name.split("/")[-1] == "train.csv":
                len_train = len(df)
                print(len_train)

            elif blob.name.split("/")[-1] == "val.csv":
                len_val = len(df)
                print(len_val)
            else:
                # Append the DataFrame to the list
                dfs.append(df)
                cnt_row += len(df)
                print(f"{blob.name}, {len(df)}")

    # Concatenate all DataFrames in the list
    concatenated_df = pd.concat(dfs, ignore_index=True)
    # Sort the DataFrame by the "group" column
    concatenated_df_sorted = concatenated_df.sort_values(by="group")

    # Check if train.csv and val.csv lengths are found
    if len_train == 0 or len_val == 0:
        print("Failed to find lengths of train.csv or val.csv.")
        return
    print(len(concatenated_df_sorted))
    # Split concatenated DataFrame into train.csv and val.csv based on lengths
    train_df = concatenated_df_sorted[:len_train]
    val_df = concatenated_df_sorted[len_train:]
    # Save the concatenated DataFrame to a CSV file
    train_df.to_csv(
        f"{local_destination_folder}/{remote_file_path}_train.csv", index=False
    )
    val_df.to_csv(f"{local_destination_folder}/{remote_file_path}_val.csv", index=False)

    print(f"Concatenated CSV file saved to: {local_destination_folder}")


def editing_done(remote_file_path, group_num):
    """
    Mark all rows in a specified group CSV file as edited by setting the "edit_status" column to True.

    This function downloads a CSV file corresponding to a specific group from Firebase Storage,
    marks all rows as edited, and uploads the modified CSV file back to Firebase Storage.

    Parameters:
        remote_file_path (str): The path of the folder containing the group CSV files on Firebase Storage.
        group_num (int): The group number identifying which group's CSV file to edit.

    Raises:
        ValueError: If the remote file path or group number is invalid.
        FileNotFoundError: If the specified group CSV file does not exist in the remote location.
        IOError: If there are issues downloading, editing, or uploading the CSV file.

    Returns:
        None
    """

    csv_file = get_csv_file(remote_file_path, f"group_{group_num}.csv")
    df = pd.read_csv(BytesIO(csv_file))

    df["edit_status"] = [True] * len(df)
    csv = df.to_csv(index=False)

    upload_edited_csv_file(csv, f"{remote_file_path}/group_{group_num}.csv")
