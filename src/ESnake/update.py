import json
import requests
import threading
import logging
import tempfile
import io
import os
import subprocess

def versiontuple(v):
    return tuple(map(int, (v.split("."))))

def getLatestVersion():
    response = requests.get("https://api.github.com/repos/kellyelton/esnake/releases/latest")

    latestRelease = response.json()

    releasename = latestRelease["name"] # v0.1.7.0
    tagname = latestRelease["tag_name"] # v0.1.7.0

    latestVersionString = tagname.lstrip("v")
    latestVersion = versiontuple(latestVersionString)

    assets = latestRelease["assets"] # array of assets

    download_url = None

    for asset in assets:
        if asset["name"] == "esnake.exe":
            download_url = asset["browser_download_url"]
            break

    if not download_url: raise Exception(f"Error getting latest version: Release {releasename} did not contain esnake.exe asset")

    return (latestVersion, download_url)

class Updater():
    def __init__(self, currentVersion, exelocation):
        if currentVersion == None: raise Exception("currentVersion is None");

        self.isComplete = False
        self.shutdownForUpdate = False
        self.updateError = None
        self.status = ""
        self.currentVersion = currentVersion
        self.exelocation = exelocation
        self.__thread = threading.Thread(None, self.__run)
        self.logger = logging.getLogger(__name__)

    def start(self):
        if self.status != "": raise Exception(f"Already started")

        self.status = "Checking for Update"
        self.minorstatus = ""

        self.__thread.start()
    
    def __run(self):
        try:
            self.logger.debug(f"Getting the latest version")

            (latestVersion, downloadUrl) = getLatestVersion()

            self.logger.info(f"Latest Version: {latestVersion}")
            self.logger.info(f"Download Url: {downloadUrl}")

            if self.currentVersion == latestVersion:
                self.logger.debug(f"Already have latest version installed, not updating")
                return

            self.logger.info(f"Updating from {self.currentVersion} to {latestVersion}")

            self.status = "Updating"
            self.minorstatus = "downloading update"

            downloadPath = tempfile.gettempdir()
            downloadPath = os.path.join(downloadPath, "esnakeupdate.exe")

            self.logger.info(f"downloading {downloadUrl} to {downloadPath}")
            request = requests.get(downloadUrl)

            with open(downloadPath, 'wb') as fileStream:
                fileStream.write(request.content)

            self.minorstatus = "launching updater"

            self.logger.info(f"launching {downloadPath} UPDATE '{self.exelocation}'")

            subprocess.Popen([
                downloadPath,
                "UPDATE",
                f"'{self.exelocation}'"
            ])

            self.shutdownForUpdate = True

        except Exception as exception:
            message = str(exception)
            self.logger.error(f"Error updating: {message}", exc_info=True)
            self.updateError = exception
        finally:
            self.isComplete = True