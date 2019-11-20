import pygame

class PyPostGameScreenEngine:
    def processEvent(self, app, event):
        pass
    def draw(self, app, pyscreen):
        pyscreen.fill(app.style.postGameBackgroundColor)

        ## TODO: Draw stuff