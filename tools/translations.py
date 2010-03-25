from elementtree.ElementTree import parse
from itertools import ifilter
import sys
import csv

tree = parse(sys.argv[1])
ns = '{http://www.imsglobal.org/xsd/imsvdex_v1p0}'

all_terms = [term for term in tree.findall('//%sterm' % ns)]
parents = {}
for term in all_terms:
    for children in term.findall('%sterm' % ns):
        childid = children.find('%stermIdentifier' % ns).text
        assert childid
        parents[childid] = term

def getParents(term):
    id = term.find('%stermIdentifier' % ns).text
    try:
        parent = parents[id]
    except KeyError:
        return []
    retval = getParents(parent)
    retval.append(getEnglishTranslation(parent))
    return retval

def getEnglishTranslation(term):
    for subterm in term.findall('%scaption/%slangstring' % (ns, ns)):
        if subterm.attrib['language'] == 'en':
            return subterm.text

def filterRule(a):
    return len(set([x.text for x in a.findall('%scaption/%slangstring' % (ns, ns))])) < 2

untranslated_terms = ifilter(filterRule, all_terms)

translations = ['id', 'Path (for context only)', 'Term to translate','translation']

writer = csv.writer(open('translate.csv', 'wb'))
writer.writerow(translations)
for term in untranslated_terms:
    id = term[0].text
    ttt = term[1][0].text
    path = ' -> '.join(getParents(term))
    writer.writerow([id, path, ttt, ''])
