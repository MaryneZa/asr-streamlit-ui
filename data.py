from database import (
    upload_csv_files,
    upload_audio_files,
    download_csv_file,
    concat_csv_files_for_downloading,
    editing_done,
)

# Please upload your audio files before uploading your CSV files.
# The names of your audio and CSV folders should match.

upload_audio_files(folder_path=r"D:\work\kru_mild-01\kru_mild-01")

upload_csv_files(folder_path=r"D:\work\kru_mild-01", group_size=50)

concat_csv_files_for_downloading(
    remote_file_path="kru_mild-01", local_destination_folder="D:/work"
)

editing_done(remote_file_path="kru_mild-01", group_num=6)
