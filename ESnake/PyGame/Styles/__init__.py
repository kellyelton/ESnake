from .DefaultStyle.style import ClassicStyle

def loadStyle(styleName):
    if styleName.casefold() == 'classic'.casefold():
        return ClassicStyle()
    else:
        #TODO log this failure
        return ClassicStyle()