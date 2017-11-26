/*
    Copyright (c) 2017 Philip/Scobalula - AutoUpdater for CoDMayaTools

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
*/

using System.Net;
using System.IO;
using System.Windows.Forms;
using System.Diagnostics;

namespace Updater
{
    class Program
    {
        /// <summary>
        /// Main Function handling loading version file and checking against version passed to program.
        /// </summary>
        /// <param name="args">Decimal Number representing current version i.e. 2.54, 2.4, etc.</param>
        static void Main(string[] args)
        {
            // Return if nothing passed
            if (args.Length < 1)
                return;
            // Current/Latest Versions
            float latestVersion;
            float currentVersion;
            // Parse Current Version
            if (!float.TryParse(args[0], out currentVersion))
                return;
            // Create Webrequest from version file
            var webRequest = WebRequest.Create(@"https://raw.githubusercontent.com/Ray1235/CoDMayaTools/master/version");
            // Ignore checking for a connection, try grab file, if we fail just exit.
            try
            {
                using (var reader = new StreamReader(webRequest.GetResponse().GetResponseStream()))
                {
                    // Parse Latest
                    if (!float.TryParse(reader.ReadLine(), out latestVersion))
                        return;
                    // Check version against previous version
                    if (currentVersion < latestVersion)
                    {
                        // Alert user
                        DialogResult dialogResult = MessageBox.Show(
                            string.Format("New CoD Maya Tools Update available.\n\nCurrent Version:    {0:0.00}\nLatest Version:       {1:0.00}\n\nWould you like to download it now?",
                            currentVersion,
                            latestVersion),
                            "Update Available", MessageBoxButtons.YesNo);
                        // Load Webpage if desired
                        if (dialogResult == DialogResult.Yes)
                            Process.Start(@"https://github.com/Ray1235/CoDMayaTools/releases");
                    }
                }
            }
            catch
            {
                return;
            }
        }
    }
}
