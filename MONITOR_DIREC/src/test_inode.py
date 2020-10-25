# Python script to monitor file location and create a zip file using UTC time zone as password
# Steps:
#1:  Monitor file location
#2:  Create password protected zip
#3:  Move the zip to other location

import sys
import shutil
import time,os
import pyminizip
import inotify.adapters


def notify_and_create_zip(monitor_loc, dest_loc):
    """
    Method to Start monitoring folder. If *.txt file is copied/created/dropped, it will
    generate UTC timezone and create password protected file.

    :param monitor_loc: Monitor location
    :param dest_loc: Destination location
    :return None
    """
    # instance of inotify - inode notify
    inot_folder = inotify.adapters.Inotify()

    # add folder location in the watch list
    inot_folder.add_watch(monitor_loc)

    # continuously monitor the event in the monitor location
    for event in inot_folder.event_gen(yield_nones=False):
        (_, event_type_names, path, filename) = event
        if event_type_names[0] in ['IN_CREATE', 'IN_MOVED_TO'] and filename:
            # if file is created/moved/dropped in the location
            print("Path:{}\nFilename:{}\n".format(path, filename))

            # get the UTC time zone and local time
            print("Getting Time Zone")
            UTC_TIME = time.time()
            local_time = time.localtime(UTC_TIME)
            zip_filename = "{}_{}_{}_{}_{}_{}".format(local_time.tm_year,
                                                      local_time.tm_mon,
                                                      local_time.tm_mday,
                                                      local_time.tm_hour,
                                                      local_time.tm_min,
                                                      local_time.tm_sec)
            print("Zip file:- ", zip_filename)
            password = str(int(UTC_TIME))
            zip_filename = zip_filename + '.zip'

            # creating zip file with password protected
            print("Creating ZIP file")
            file_location = os.path.join(monitor_loc, filename)
            pyminizip.compress(file_location, monitor_loc, zip_filename, password, 1 )

            # move the zip into the destination folder
            target_location = os.path.join(dest_loc, zip_filename)
            print("Target_location: {}".format(target_location))
            shutil.copyfile(zip_filename, target_location)


def display_usage():
    print("\n\nPlease Use the following command. \
        \nUsage: python <filename>.py <monitor_folder> <decode_folder>\n\n")


def check_des_folder(source_location, dest_location):
    """
    Method to check the destination folder content
    If files are present, then delete them.

    :param dest_location: Destination Location
    """
    if not os.path.exists(dest_location):
        os.makedirs(dest_location)

    # check for source direc in the location and delete it if present
    locate = os.path.join(dest_location, source_location)
    if os.path.exists(locate):
        print('Remove Source Location: ', locate)
        shutil.rmtree(locate, ignore_errors=True)
    else:
        print("No Source directory found")
    # get the list of contents
    files = (os.listdir(dest_location))
    if not files:
        print("No files are present in the decode/ location")
    else:
        # check for the zip files
        for file in files:
            if file.endswith("zip"):
                print("ZIP: {} is available".format(file))
                os.remove(dest_location + file)
                print("ZIP file removed")
        else:
            print("No ZIP file available in the location")



if __name__ == '__main__':
    file_location = ''

    if len(sys.argv) != 3:
        display_usage()
        sys.exit()

    monitor_folder = sys.argv[1]
    dest_folder = sys.argv[2]
    print("Monitor location: {}".format(monitor_folder))
    print("Destination location: {}".format(dest_folder))

    # check for the destination folder
    check_des_folder(monitor_folder, dest_folder)
    notify_and_create_zip(monitor_folder, dest_folder)
