import elementtree.ElementTree as ETree
from pprint import pprint as pp
import csv

namespace = {
    'excerpt': "http://wordpress.org/export/1.2/excerpt/",
    'content': "http://purl.org/rss/1.0/modules/content/",
    'wfw': "http://wellformedweb.org/CommentAPI/",
    'dc': "http://purl.org/dc/elements/1.1/",
    'wp': "http://wordpress.org/export/1.2/"
}


def ns(nspace, tagname):
    r = "{{{a}}}{b}".format(
        a=namespace[nspace],
        b=tagname
    )
    return r


tree = ETree.parse("data/product_data-sprinklersystemshop.wordpress.2014-05-08.xml")
docroot = tree.getroot()

# thingy = doc.find('channel')
# print thingy.attrib

objectsCount = 0

big_list = []

with open('temp.csv', 'wb') as csvfile:
    writer = csv.writer(
        csvfile,
        delimiter=',',
        quotechar='|',
        quoting=csv.QUOTE_MINIMAL)

    for item in docroot.findall('channel/item'):
        title = item.find('title').text
        desc = item.find(ns('content', 'encoded')).text

        metakeys_raw = item.findall(ns('wp', 'postmeta'))
        metakeys = {}

        for metakey in metakeys_raw:
            # ETree.dump(metakey)
            metakeys[metakey[0].text] = metakey[1].text

        # pp(metakeys)
        def get_key_val(keyname, default_val=''):
            try:
                return metakeys[keyname]
            except KeyError:
                return default_val

        price_regular = get_key_val('_wpsc_price')
        price_special = get_key_val('_wpsc_special_price')

        # print price_special, title
        # print desc

        writer.writerow([
            title,
            price_special,
            price_regular
        ])

        objectsCount += 1

print objectsCount

