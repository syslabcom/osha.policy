from optparse import OptionParser
import os
import sys

from lxml import etree
from lxml.builder import ElementMaker
from rdflib import Graph, Literal, Namespace, RDF, URIRef


def recurse_convert_node(current_node):
    ipshell()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--vdex", dest="vdex_file",
                      help="Path to VDEX file")
    parser.add_option("--skos", dest="skos_file",
                      help="Path to SKOS file")
    parser.add_option("--overwrite", dest="overwrite", default=False,
                      action="store_true",
                      help=("Overwrite the specified output (--skos) file "
                            "if it exists."))
    options, args = parser.parse_args()

    if os.path.exists(options.vdex_file):
        vdex_file = open(options.vdex_file, "r")
    else:
        print "Invalid path to VDEX file"
        sys.exit(1)

    if options.overwrite or not os.path.exists(options.skos_file):
        skos_file = open(options.skos_file, "w")
    else:
        print "SKOS file already exists, delete it or use --overwrite"
        sys.exit(1)

    vdex = etree.parse(vdex_file)

    # Using "x" as the namespace prefix since xpath has no way to
    # specify a default namespace
    VDEX_NS = {"x":"http://www.imsglobal.org/xsd/imsvdex_v1p0"}

    graph = Graph()
    skos = Namespace('http://www.w3.org/2004/02/skos/core#')
    graph.bind('skos', skos)

    vocab_id = vdex.xpath("//x:vocabIdentifier[1]/text()",
                          namespaces=VDEX_NS)
    if vocab_id == []:
        print "Invalid VDEX? No vocabIdentifier."
        sys.exit(1)
    vocab_id = vocab_id[0]
    terms = vdex.xpath("//x:term", namespaces=VDEX_NS)
    for term in terms:
        term_id_list = term.xpath("x:termIdentifier[1]/text()",
                                  namespaces=VDEX_NS)
        if term_id_list == []:
            break
        term_id = term_id_list[0]

        langstrings = term.xpath("x:caption/x:langstring", namespaces=VDEX_NS)
        uri = '%s/%s' % (vocab_id, term_id)
        graph.add((URIRef(uri),
                   RDF['type'], skos['Concept']))
        for langstring in langstrings:
            lang = langstring.attrib["language"]
            graph.add((URIRef(uri), skos['prefLabel'],
                       Literal(langstring.text, lang=lang)))

        parent_term_id_list = term.xpath(
            "./ancestor::x:term[1]/x:termIdentifier",
            namespaces=VDEX_NS)
        if parent_term_id_list != []:
            parent_term_id = parent_term_id_list[0].text
            parent_term_uri = '%s/%s' % (vocab_id, parent_term_id)
            graph.add((URIRef(uri),
                       skos['broaderTransitive'],
                       URIRef(parent_term_uri)))


    skos_file.write(graph.serialize(format='pretty-xml'))
    skos_file.close()
    vdex_file.close()
