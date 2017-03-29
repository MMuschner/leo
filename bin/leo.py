#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import argparse
try:
    from lxml import html as htmlparser
except ImportError:
    print("Error: No lxml module found. "
          "Install package python3-lxml")
    sys.exit(10)


__author__ = "Thomas Schraitle <toms@suse.de>"
__version__ = "1.0"


# Global URL
URL = "http://pda.leo.org/englisch-deutsch/{0}"


def parse():
    """Parse the command line """
    parser = argparse.ArgumentParser(description='Query Leo',
                                     usage='%(prog)s [OPTIONS] QUERYSTRING')
    parser.add_argument('-D', '--with-defs',
                        action="store_true",
                        default=False,
                        help="Include any definitions in the result "
                             "(default: %(default)s)",
                        )
    parser.add_argument('-E', '--with-examples',
                        action="store_true",
                        default=False,
                        help="Include examples in the result "
                             "(default: %(default)s)",
                        )
    parser.add_argument('-P', '--with-phrases',
                        action="store_true",
                        default=False,
                        help="Include phrases in the result "
                             "(default: %(default)s)",
                        )
    # parser.add_argument( '-F', '--with-forums',
    #   action="store_true",
    #   default=False,
    #   help="Include forums in the result (default: %(default)s)",
    #   )
    parser.add_argument('query',
                        metavar="QUERYSTRING",
                        help="Query string",
                        )
    return parser.parse_args()


def getLeoPage(url):
    """Return root node of Leo's result HTML page
    """
    doc = htmlparser.parse(url)
    html = doc.getroot()
    return html


def formattable(entry):
    """Format table entry and print formatted line
    """
    for td in entry:
        for t in td.getchildren():
            t.drop_tag()
            c1 = t.text_content().encode("UTF-8")
            print("  {0}".format(c1))


def _extracttext(element):
    x = []
    t = "" if element.text is None else element.text.strip()
    if t:
        x.append(t)
    # Iterate over all children of the element
    for i in element.getchildren():
        t = "" if i.text is None else i.text.strip()
        if t:
            x.append(t)

        for j in i.getchildren():
            t = "" if j.text is None else j.text.strip()
            if t:
                x.append(t)

        if i.tail is not None:
            x.append(i.tail.strip())

    t = " ".join(x).strip().encode("UTF-8")
    if sys.version_info.major > 2:
        return t.decode("UTF-8")
    else:
        return t


def extracttext(element):
    txt = element.xpath("string(.)").replace('\xa0', '')
    return txt


def format_as_table(row):

    for tr in row:
        c1, c2 = tr.getchildren()
        # print(c1,c2)
        t1 = extracttext(c1).strip()
        t2 = extracttext(c2)
        t1 = " ".join(t1.split())
        print("{:<55} | {}".format(t1, t2))


def getResults(args, html):
    line = "-" * 10
    data = {"subst":      "Substantive",
            "verb":       "Verbs",
            "adjadv":     "Adjectives/Adverbs",
            # "example":    "Beispiele",
            # "phrase":     "Redewendung",
            }

    # if args.with_defs:
    #   data.update({"definition": "Definitions"})

    if args.with_examples:
        data.update({"example":    "Examples"})

    if args.with_phrases:
        data.update({"phrase":     "Redewendung"})

    found = set()
    div = html.get_element_by_id('centerColumn')
    for section in div.find_class("section")[:5]:
        name = section.attrib.get('data-dz-name')
        if name in data:
            found.add(name)
            print("\n{0} {1} {0}".format(line, data[name]))
            trs = section.xpath(
                "table/tbody/tr[td[@lang='en'] and td[@lang='de']]")
            format_as_table(trs)


if __name__ == "__main__":
    args = parse()
    print("Args={}".format(args))
    URL = URL.format(args.query)
    print("Investigating \"{}\"...".format(URL))
    try:
        HTML = getLeoPage(URL)
        getResults(args, HTML)
    except IOError:
        # Term wasn't found
        print("No translation for {} was found".format(
            args.query), file=sys.stderr)

# EOF
