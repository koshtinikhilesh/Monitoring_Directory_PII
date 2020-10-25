# Monitoring_Directory_PII

### List of DIrectories
(1) src/   -   Source code Folder

(2) Monitoring - Folder where script will start monitoring

(3) todecode - Folder where zip will uncompress

### List of Files
(1) src/test_inode.py   -   Python script which will start monitoring, compress the file, and create password protected.

(2) src/test_decode.py - Python script which will decode, decompress and apply PII filtering to the text file

(3) InstallationGuide.txt - GUidelines for the installation

### Example
- Execute following commands in two terminals

``` python3 src/test_inode.py monitoring/ todecode/ ```

``` python3 src/test_decode.py monitoring/ todecode ```

### Video
 - https://github.com/koshtinikhilesh/Monitoring_Directory_PII/blob/main/MONITOR_DIREC/Walkthrough.mp4
