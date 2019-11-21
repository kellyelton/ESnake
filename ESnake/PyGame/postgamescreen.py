import pygame

class PyPostGameScreenEngine:
    def processEvent(self, app, event): pass
    def update(self, app): pass

    def draw(self, app, pyscreen):
        pyscreen.fill(app.engine.style.postGameBackgroundColor)

        ## TODO: Draw stuff