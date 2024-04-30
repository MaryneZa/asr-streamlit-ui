from database import upload_csv_files, upload_audio_files, download_csv_file

# plz upload your audio files before upload your csv files
# your audio and csv folder name should be the same

upload_audio_files(r"D:\work\Natcha NCS-01\Natcha-01")

upload_csv_files(r"D:\work\Natcha-01", 100)

download_csv_file("Natcha-01/train.csv")

download_csv_file("Natcha-01/val.csv")
