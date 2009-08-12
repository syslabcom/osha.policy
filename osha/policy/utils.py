


def logit(*kwargs):
    " log something from the web "
    try:
        mesg = ''
        for kwarg in kwargs:
            mesg += str(kwarg) + ' '
        print mesg
    except:
        print [kwargs]
