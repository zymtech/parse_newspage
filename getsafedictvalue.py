def getsafedictvalue(dict, pathval, defval):
    childs = pathval.split("/")
    childdict = dict
    try:
        for child in childs:
            childdict = childdict[child]
        retval = childdict
    except KeyError:
        retval = defval
        pass
    return retval