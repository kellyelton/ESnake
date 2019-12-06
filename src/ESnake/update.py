import json
import requests

def versiontuple(v):
    return tuple(map(int, (v.split("."))))

def isAvailable():
    response = requests.get("https://api.github.com/repos/kellyelton/esnake/releases/latest")

    latestRelease = response.json()

    releasename = latestRelease["name"] # v0.1.7.0
    tagname = latestRelease["tag_name"] # v0.1.7.0

    latestVersionString = tagname.lstrip("v")
    latestVersion = versiontuple(latestVersionString)

    ##TODO: Get current version
    currentVersion = versiontuple("12.0.0.0")

    if latestVersion <= currentVersion: return False

    ## Update available, return url

    assets = latestRelease["assets"] # array of assets

    download_url = False

    for asset in assets:
        if asset["name"] == "esnake.exe":
            download_url = asset["browser_download_url"]

    return download_url

def run():
    pass