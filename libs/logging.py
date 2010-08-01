
def info(*args):
    r = []
    for x in args:
        if not isinstance(x,basestring):
            r.append(str(x))
        else:
            r.append(x)
    print ' '.join(r)

warn = info
error = info