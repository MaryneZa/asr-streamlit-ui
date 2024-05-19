from database import upload_csv_files, upload_audio_files, download_csv_file, concat_csv_files_for_downloading, editing_done

# Please upload your audio files before uploading your CSV files.
# The names of your audio and CSV folders should match.

# upload_audio_files(folder_path=r"D:\work\kru_mild-02\kru_mild-02")

# upload_csv_files(folder_path=r"D:\work\kru_mild-02", group_size=50)

download_csv_file(
    remote_file_path="kru_mild-02/train.csv", local_destination_folder="D:/work"
)
download_csv_file(
    remote_file_path="kru_mild-02/val.csv", local_destination_folder="D:/work"
)
# download_csv_file(
#     remote_file_path="tonghison-01/group_16.csv", local_destination_folder="D:/work"
# )

# concat_csv_files_for_downloading(remote_file_path="tonghison-01", local_destination_folder="D:/work")

# editing_done(remote_file_path="tonghison-01", group_num=16)

