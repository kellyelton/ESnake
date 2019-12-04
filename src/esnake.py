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

if __name__=='__main__':
    logger: logging.Logger = logging.getLogger(__name__)

    try:
        logPath = os.path.join(os.getcwd(), "log.txt")           

        logging.basicConfig(filename=logPath, filemode='w', format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

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
        message = str(exception)
        logger.fatal(f"Unhandled Exception: {message}", exc_info=True)
    finally:
        logger.info("END")