from plone.app.linkintegrity import parser
from plone.app.linkintegrity.parser import LinkParser
from HTMLParser import HTMLParseError


def extractLinks(data):
    """ parse the given html and return all links """
    if not data:
        return []
    try:
        data = data.decode('utf-8')
    except:
        pass
    parser = LinkParser()
    try:
        parser.feed(data)
        parser.close()
    except (HTMLParseError, TypeError):
        pass
    return parser.getLinks()

parser.extractLinks = extractLinks

