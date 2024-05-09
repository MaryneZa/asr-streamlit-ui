from database import upload_csv_files, upload_audio_files, download_csv_file

# Please upload your audio files before uploading your CSV files.
# The names of your audio and CSV folders should match.

# upload_audio_files(folder_path=r"D:\work\mini-test\mini-test")

upload_csv_files(folder_path=r"D:\work\kru_mild-01", group_size=50)

download_csv_file(
    remote_file_path="kru_mild-01/train.csv", local_destination_folder="D:/work"
)
download_csv_file(
    remote_file_path="kru_mild-01/val.csv", local_destination_folder="D:/work"
)



