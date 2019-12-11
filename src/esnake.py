#!/usr/bin/env python
__author__ = 'kellyandloranelton'

"""
Simple snake game
"""

import sys
import traceback
import logging
import os
import yaml
import shutil
import subprocess
import time
from ESnake import *
from ESnakePyGame import *
from pprint import pformat

def loadConfig(logger: logging.Logger) -> Config: 
    def parseBool(boolString: str) -> bool:
        return boolString.lower() in ['true', '1']

    def configConstructor(self, node):
        config = Config()

        for nodeValues in node.value:
            nodeName = nodeValues[0].value
            nodeValue = nodeValues[1].value

            if nodeName == 'fullscreen':
                config.fullscreen = parseBool(nodeValue)
            elif nodeName == 'highScorePath':
                config.highScorePath = nodeValue
            elif nodeName == 'maxfps':
                config.maxfps = int(nodeValue)
            elif nodeName == 'style':
                config.style = nodeValue
            elif nodeName == 'screenSize':
                xnode = nodeValue[0]
                ynode = nodeValue[1]
                xstring= xnode.value
                ystring = ynode.value
                x = int(xstring)
                y = int(ystring)

                config.screenSize = [x, y]

        return config

    def configRepresenter(dumper: yaml.Dumper, data):
        return dumper.represent_yaml_object(u'!config', data, Config)

    yaml.SafeLoader.add_constructor(u'!config', configConstructor)
    yaml.add_representer(Config, configRepresenter)

    logger.info("loading config")

    configFilePath = "config.yaml"

    configFilePath = os.path.join(os.getcwd(), configFilePath)

    config = Config()

    if not os.path.exists(configFilePath):
        logger.info(f"config file {configFilePath} not found. Creating")

        with open(configFilePath, "w") as fileStream:
            yaml.dump(config, fileStream)
    else:
        logger.info(f"opening config file {configFilePath}")
        with open(configFilePath) as fileStream:
            config = yaml.safe_load(fileStream)

    return config

def update(logger, exePath, overwritePath):
    tryCount = 0

    while True:
        try:
            logger.info(f"Trying to replacing file {overwritePath} with {exePath}")

            shutil.copy2(exePath, overwritePath)

            logger.info(f"Replaced file {overwritePath}")

            break
        except Exception as exception:
            logger.warn("Error replacing file", exc_info=True)

            tryCount += 1

            if tryCount >= 5:
                raise Exception("Unable to update, file couldn't be replaced")

            time.sleep(1)

    logger.info(f"Launching updated app {overwritePath}")

    subprocess.Popen([
        overwritePath
    ])

def runGame(logger, exePath):
    debug = Debug()
    debugString = pformat(vars(debug))
    logger.info("Debug Settings")
    logger.info(debugString)

    config = loadConfig(logger)
    configString = pformat(vars(config))
    logger.info(configString)

    engine = PyGameEngine()

    app = App(engine, config, exePath, debug)

    logger.info("running")

    app.run()

if __name__=='__main__':
    logger: logging.Logger = logging.getLogger(__name__)

    try:
        logpath = "log.txt"
        runUpdater = False
        overwritePath = None

        if len(sys.argv) >= 3:
            if sys.argv[1] == "UPDATE":
                runUpdater = True
                overwritePath = sys.argv[2].strip("'\"")
                logpath = "updatelog.txt"

        logpath = os.path.join(os.getcwd(), logpath)           

        logging.basicConfig(filename=logpath, filemode='w', format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

        logger.info("START")

        isDebugging = not getattr(sys, 'frozen', False)

        exePath = None

        if not isDebugging:
            exePath = sys.executable

        logger.info(f"exePath: {exePath}")

        # log command line arguments
        count = 0
        for arg in sys.argv:
            logger.info(f"ARG {count}: {arg}")

            count+=1

        if runUpdater:
            logger.info("running updater")
            update(logger, exePath, overwritePath)
        else:
            logger.info("running game")
            runGame(logger, exePath)

    except Exception as exception:
        message = str(exception)
        logger.fatal(f"Unhandled Exception: {message}", exc_info=True)
    finally:
        logger.info("END")