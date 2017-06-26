import urllib2
import socket
import os
import time
import sys

FILE_VERSION = 1.2
VERSION_CHECK_URL = "https://raw.githubusercontent.com/Ray1235/CoDMayaTools/master/version"
WORKING_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

def HasInternetAccess():
    # Apparently we needed Admin privs. to use ping -c that Aidan used originally..
    try:
        # Check for connection, no URL names to avoid DNS look-up.
        socket.create_connection(("8.8.8.8", 80))
        return True
    except:
        # No connection, return.
        return False


def CheckForUpdates():
    try:
        if not HasInternetAccess():
            print("<-- No connection.\n\n")
            return None
            
        response = urllib2.urlopen(VERSION_CHECK_URL, timeout=2)
        info = response.readlines()
        response.close()
        
        if not info or len(info) == 0:
            return None

        mostRecentVersion = float(info[0])
        downloadUpdateURL = info[1] # Location of the most recent file
        
        if mostRecentVersion > FILE_VERSION:
            return (mostRecentVersion, downloadUpdateURL)
    except Exception as e :
        print("<-- Exception occured in \"CheckForUpdates()\": %s.\n\n" % e)
    
    return None
    
def DownloadUpdate(downloadUpdateURL):
    try:
        if not HasInternetAccess():
            print("<-- No connection.\n\n")
            return None
            
        response = urllib2.urlopen(downloadUpdateURL, timeout=5)
        newCode = response.read()
        response.close()

        print("<-- Downloading update from: %s\n" % str(downloadUpdateURL))

        path = os.path.join(WORKING_DIR, "CoDMayaTools.py")

        with open(path, 'w') as f:
            f.write(newCode)
        
        print("<-- Update complete, reload script or restart Maya to apply changes.\n\n")
    except Exception as e:
        print("<-- Exception occured in \"DownloadUpdate()\": %s.\n\n" % e)

if __name__ == '__main__':
    print("<-- COD Maya Tools Update --\n\n")
    print("<-- Checking for updates...\n\n")
    update = CheckForUpdates()

    if update:
        print("<-- New update available: VERSION %s\n\n" % str(update[0]))
        DownloadUpdate(update[1])
        
    print("This window will close in 5 seconds")
    time.sleep(5)