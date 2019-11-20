#!/usr/bin/env python
__author__ = 'kellyandloranelton'

"""
Simple snake game
"""

import sys
import traceback
from ESnake.app import App 
from ESnake.config import DefaultConfig
from ESnake.PyGame.engine import PyGameEngine


if __name__=='__main__':
    try:
        print("Launching...")

        config = DefaultConfig()

        engine = PyGameEngine()

        app = App(engine, config)

        app.run()
    except Exception as exception:
        exceptionString = traceback.format_exc()
        print(exceptionString, file=sys.stderr)
    finally:
        print("DONE")