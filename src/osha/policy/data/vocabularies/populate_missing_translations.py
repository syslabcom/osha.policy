#!/usr/bin/python2.7
# -*- coding: utf8 -*-

# (c) 2013 Peter Lamut

from lxml import etree as ET


_name = 'Subcategory'
_filename = "%s.vdex" % _name
_out_filename = "%s.fixed.vdex" % _name
_tag_prefix = "{http://www.imsglobal.org/xsd/imsvdex_v1p0}"
_xpath_lang_tpl = "./{{http://www.imsglobal.org/xsd/imsvdex_v1p0}}langstring[@language='{0}']"

_languages = [
    "bg",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "et",
    "fi",
    "fr",
    "hu",
    "hr",
    "is",
    "it",
    "lt",
    "lv",
    "mt",
    "nl",
    "no",
    "pl",
    "pt",
    "ro",
    "sk",
    "sl",
    "sv",
]


def _fix_tree(root):
    """Fix missing language strings in a tree."""
    if len(root) == 0:
        return

    for child in root:
        if (
            child.tag == _tag_prefix + "vocabName" or
            child.tag == _tag_prefix + "caption"
        ):
            _fix_lang_strings(child)
        else:
            _fix_tree(child)


def _fix_lang_strings(root):
    """Check for missing language strings and add them if necessary."""
    if len(root) == len(_languages):
        return  # nothing to do, no language is missing

    # 1. obtain english language string
    en_lang = root.find(_xpath_lang_tpl.format("en"))
    if en_lang is None:
        raise Exception("English <langstring> element not found.")

    # 2. for each language check if element exists and if not,
    #    create it and use english translation for it
    for lang_code in _languages:
        el = root.find(_xpath_lang_tpl.format(lang_code))
        if el is None:
            new_el = ET.Element("langstring", language=lang_code)
            new_el.text = en_lang.text
            root.append(new_el)


def main():
    # remove whitespace when parsing so that pretty print will work
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(_filename, parser)
    root = tree.getroot()

    _fix_tree(root)

    tree.write(
        _out_filename,
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True
    )


if __name__ == '__main__':
    main()
