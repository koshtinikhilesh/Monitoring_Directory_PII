 # Steps
 #1 Monitor the todecode folder
 #2 Get the zip file, extract localtime, get the password
 #3 extract the file
 #4 perform PII filering and saveit in unfiltered pii file


import sys
import time
import spacy
import datetime
import inotify.adapters
import pyminizip
import os
nlp = spacy.load('en')


def remove_pii_info(source_location, decode_location, file_name):
    """
    Method to remove PII from the file
    and save it in the other file

    :param content_location: Contents  Location (txt location)
    :param file_name: Zip filename
    """
    updated_content = []
    file_prefix = 'PII_filtered_'
    txt_location = os.path.join(source_location, file_name)
    with open(txt_location, 'r') as file_content:
        lines = file_content.readlines()

    for line in lines:
        l = line.replace('\\', '  ')
        l = l.replace('c:', '<d>')
        l = l.replace('C:', '<d>')

        sent = nlp(l)

        for d in sent.ents:
            if d.label_ == 'PERSON':
                val = str(d).strip()
                l = l.replace(val, '<user>')
                new_val = l.replace('  ', '\\')
                updated_content.append(new_val)
            else:
                new_value = l.replace('  ', '\\')
                updated_content.append(new_value)

        if not sent.ents:
            empty_user_value = l.replace('  ', '\\')
            updated_content.append(empty_user_value)

    # writing into the another separate file
    filter_filename = file_prefix + file_name
    filter_filelocation = os.path.join(decode_location, source_location, filter_filename)
    print("Filtered file: {}".format(filter_filelocation))

    with open(filter_filelocation, 'w+') as filehandle:
        for item in set(updated_content):
            print('Item: {} '.format(item))
            filehandle.write('%s\n' % item)



def notify_decode(source_location, decode_location):
    """
    Method to Notify Decode location for the zip file.
    Extract it using password

    :param source_location: Source Location where txt files are available
    :param decode_location: Location of the decode folder
    :return None
    """
    # instance of the inotify - inode notify
    inot_decode = inotify.adapters.Inotify()

    # add decode location in the watch list
    inot_decode.add_watch(decode_location)
    current_dir = os.getcwd()
    # continuously monitor the location
    for event in inot_decode.event_gen(yield_nones=False):
        (_, event_types_names, path, filename) = event

        if event_types_names[0] in ['IN_CREATE', 'IN_MOVED_TO'] and filename:
            # if file is created/moved/dropped in the location
            print("Path:{}\nFilename:{}\n".format(path, filename))

            # remove file extention
            file_wo_exten = os.path.splitext(filename)[0]
            # get the password from the filename
            passw = get_password(file_wo_exten)
            print("Password received: {}".format(passw))
            file_location = os.path.join(decode_location, filename)

            # count for waiting for the file
            count = 0
            while count <= 5:
                if os.path.exists(file_location):
                    print("File location is available")
                    break
                else:
                    print("Wait for some time.")
                    time.sleep(1)
                    print("After timeout File status: ", os.path.exists(file_location))
                    count = count + 1

            # decompress the zip file
            before_files = []
            extract_location = os.path.join(decode_location, source_location)
            if os.path.exists(extract_location):
                print("Path available. Check the list of directory")
                before_files = os.listdir(extract_location)
                print("Available Files before uncompress: {}".format(before_files))

            # before_files
            print(file_location, passw, decode_location)
            print("Current path: {}".format(os.getcwd()))
            pyminizip.uncompress(file_location, str(passw), decode_location, 0)
            print("After Current path: {}".format(os.getcwd()))

            curr_files = os.listdir(source_location)
            print("Current Files: {}".format(curr_files))

            # fetch the current filename

            time.sleep(2)
            os.chdir(current_dir)

            print("Extracting PII from content")
            # extract personal identifier information (PII) from the file
            if not before_files:
                txt_name = os.listdir(source_location)[0]
            else:
                for file_title in before_files:
                    if file_title in curr_files:
                        curr_files.remove(file_title)

                txt_name = curr_files[0]

            remove_pii_info(source_location, decode_location, txt_name)

            os.chdir(current_dir)

def display_usage():
    print("\n\nPlease Use the following command. \
        \nUsage: python <filename>.py <decode folder>\n\n")


def get_password(filename):
    file_tuple = list(filename.split('_'))
    timestamp = [int(data) for data in file_tuple]
    print("UTC Elapsed time: {}".format(timestamp))

    upd_time = datetime.datetime(timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5]).timetuple()
    elapsed_time = int(time.mktime(upd_time))
    print("Elapsed time: {}".format(elapsed_time))
    return elapsed_time


if __name__ == '__main__':
    if len(sys.argv) != 3:
        display_usage()
        sys.exit()

    source_location = sys.argv[1]
    decode_location = sys.argv[2]
    print("Decode location: {}".format(decode_location))
    print("Source location: {}".format(source_location))
    notify_decode(source_location, decode_location)
