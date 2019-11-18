#!/usr/bin/env python
__author__ = 'kellyandloranelton'

"""
Simple snake game
"""

import sys
import traceback
from ESnake.game import Game


if __name__=='__main__':
    try:
        print("Launching...")

        game = Game()

        game.run()
    except Exception as exception:
        exceptionString = traceback.format_exc()
        print(exceptionString, file=sys.stderr)
    finally:
        print("DONE")