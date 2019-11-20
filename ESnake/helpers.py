def hasFunction(object, functionName):
    function = getattr(object, functionName, None)

    if function != None and callable(function):
        return True
    else:
        return False