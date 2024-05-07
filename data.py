from database import upload_csv_files, upload_audio_files, download_csv_file

# Please upload your audio files before uploading your CSV files.
# The names of your audio and CSV folders should match.

upload_audio_files(folder_path=r"D:\work\cee-06\cee-06")

upload_csv_files(folder_path=r"D:\work\cee-07", group_size=50)

download_csv_file(
    remote_file_path="cee-07/train.csv", local_destination_folder="D:/work"
)
download_csv_file(
    remote_file_path="cee-07/val.csv", local_destination_folder="D:/work"
)



