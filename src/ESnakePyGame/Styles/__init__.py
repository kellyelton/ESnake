from .DefaultStyle.style import ClassicStyle

def loadStyle(styleName):
    if styleName.casefold() == 'classic'.casefold():
        return ClassicStyle()
    else:
        raise Exception(f"Style '{styleName}' could not be found.")