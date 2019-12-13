def versiontuple(v):
    return tuple(map(int, (v.split("."))))

Version = versiontuple("0.1.16.0")