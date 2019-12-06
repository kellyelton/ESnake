import json
import requests

def isAvailable():
    response = requests.get("https://api.github.com/repos/kellyelton/esnake/releases/latest")

    latestRelease = response.json()

def run():
    pass