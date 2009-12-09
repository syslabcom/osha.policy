from elementtree.ElementTree import parse, Element

# New tags are in the file subcategories. We made a manual check to
# control whether the tag names are acceptable
tags = {}
for tag in file('subcategories.txt').read().split('\n'):
    if not tag:
        continue
    key = 'whp::' + tag.replace('&', '').replace('-', '').replace(' ', '_').lower()
    tags[key] = tag

tree = parse('/home/patrick/projects/osha_git/osha.policy/src/osha/policy/data/vocabularies/Subcategory.vdex')
ns = '{http://www.imsglobal.org/xsd/imsvdex_v1p0}'

# We ensure that the tags don't exist yet
assert not set(tags.keys()).intersection(set([x.text for x in tree.findall('.//%stermIdentifier' % ns)]))

# All languages
all_languages = set([x.get('language') for x in tree.findall('.//%slangstring' % ns)])

#This mapping quickly adds captions for all languages
def addLangs(element, msg):
    for lang in all_languages:
        elem = Element(ns + 'langstring')
        elem.set('language', lang)
        elem.text = msg
        element.append(elem) 
    

#ugly way to find the right position for adding our stuff
termIdBefore = [x for x in tree.findall('.//%stermIdentifier' % ns) if x.text == 'stress'][0]
termBefore = [x for x in tree.getroot() if len(x) and x[0] == termIdBefore][0]
term_position = [x for x in tree.getroot()].index(termBefore)

# XML Creation
new_root_element = Element(ns + 'term')
termIdentifier = Element(ns + 'termIdentifier')
termIdentifier.text = 'whp'
new_root_element.append(termIdentifier)
caption = Element(ns + 'caption')
addLangs(caption, 'Workplace Health Promotion')
new_root_element.append(caption)
for key, value in tags.items():
    new_element = Element(ns + 'term')
    termIdentifier = Element(ns + 'termIdentifier')
    termIdentifier.text = key
    new_element.append(termIdentifier)
    caption = Element(ns + 'caption')
    addLangs(caption, value)
    new_element.append(caption)
    new_root_element.append(new_element)

tree.getroot().insert(term_position + 1, new_root_element)
# you have to strip the ns0 and beautify it
tree.write('out.xml')


