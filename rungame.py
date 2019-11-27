#!/usr/bin/env python
__author__ = 'kellyandloranelton'

"""
Simple snake game
"""

import sys
import traceback
import logging
import os
from ESnake.app import App 
from ESnake.config import DefaultConfig
from ESnake.PyGame.engine import PyGameEngine
from pprint import pformat
from ESnake.debug import Debug


if __name__=='__main__':
    logger: logging.Logger = None

    try:
        logging.basicConfig(filename='log.txt', filemode='w', format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

        logger = logging.getLogger(__name__)

        logger.info("START")

        debug = Debug()
        debugString = pformat(vars(debug))
        logger.info("Debug Settings")
        logger.info(debugString)

        logger.info("loading config")
        config = DefaultConfig()
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