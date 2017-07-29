# AutoUpdate made for CoD Maya Tools by Scobalula with Aidan's code.
# AutoUpdater is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This can be adapted to any script by passing the arguments below.

import urllib2
import socket
import os
import time
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-name", help="Name of file to update relative to directory of the EXE (with ext.).", required = True, dest="name")
parser.add_argument("-version", help="Current Version of the script.", required = True, dest="version")
parser.add_argument("-version_info_url", help="Version info URL containing version and URL to new file on seperate lines.", required = True, dest = "version_url")

results = parser.parse_args()

NAMEOFSCRIPT = results.name.split(".")[0]
FILE_VERSION = results.version
VERSION_CHECK_URL = results.version_url
WORKING_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
PYFILE = os.path.join(WORKING_DIR, results.name)
CLOSETIME = 2

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
        
        if mostRecentVersion > float(FILE_VERSION):
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

        with open(PYFILE, 'w') as f:
            f.write(newCode)
        
        print("<-- Update complete, reload script or restart Maya to apply changes.\n\n")
    except Exception as e:
        print("<-- Exception occured in \"DownloadUpdate()\": %s.\n\n" % e)

if __name__ == '__main__':
    print("<-- %s Update\n\n" % str(NAMEOFSCRIPT))
    print("<-- Checking for updates...\n\n")
    update = CheckForUpdates()

    if update:
        print("<-- New update available: VERSION %s\n\n" % str(update[0]))
        DownloadUpdate(update[1])
        CLOSETIME = 5
    else:
    	print("<-- No updates available.\n\n")
        
    print("This window will close in %i seconds" % CLOSETIME)
    time.sleep(CLOSETIME)
