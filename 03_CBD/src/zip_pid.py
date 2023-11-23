"""
zips the PID folder and renames it to PID.fmu
"""
import os
import shutil
import zipfile

def zip_pid():
    output_folder = "../input/"
    folder_to_zip = "../output/PID/"

    # zip the folder
    shutil.make_archive(output_folder + "PID", 'zip', folder_to_zip)
    # remove the old PID.fmu if it exists
    if os.path.exists(output_folder + "PID.fmu"):
        os.remove(output_folder + "PID.fmu")

    # rename from PID.zip to PID.fmu overwriting the old PID.fmu
    os.rename(output_folder + "PID.zip", output_folder + "PID.fmu")


if __name__ == "__main__":
    zip_pid()