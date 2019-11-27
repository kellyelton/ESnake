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
from ESnake.app import App 
from ESnake.config import *
from ESnake.PyGame.engine import PyGameEngine
from pprint import pformat
from ESnake.debug import Debug

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

    yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/object:ESnake.config.Config', configConstructor)

    logger.info("loading config")

    configFilePath = "config.yaml"

    config = Config()

    if not os.path.exists(configFilePath):
        logger.info(f"config file {configFilePath} not found. Creating")

        config = Config()

        with open(configFilePath, "w") as fileStream:
            yaml.safe_dump(config, fileStream)
    else:
        logger.info(f"opening config file {configFilePath}")
        with open(configFilePath) as fileStream:
            config = yaml.safe_load(fileStream)

    return config

if __name__=='__main__':
    logger: logging.Logger = logging.getLogger(__name__)

    try:
        logging.basicConfig(filename='log.txt', filemode='w', format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

        logger.info("START")

        debug = Debug()
        debugString = pformat(vars(debug))
        logger.info("Debug Settings")
        logger.info(debugString)

        config = loadConfig(logger)
        configString = pformat(vars(config))
        logger.info(configString)

        engine = PyGameEngine()

        app = App(engine, config, debug)

        logger.info("running")

        app.run()
    except Exception as exception:
        logger.fatal("Unhandled Exception", exc_info=True)
    finally:
        logger.info("END")