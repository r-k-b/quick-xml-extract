import elementtree.ElementTree as ETree

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

for item in docroot.findall('channel/item'):
    title = item.find('title').text
    desc = item.find(ns('content', 'encoded')).text
    metakeys = item.findall(ns('wp', 'postmeta'))

    if 'DDCWP 2' in title:
        print title
        for metakey in metakeys:
            ETree.dump(metakey)
            # if metakey[0].text

    # print title
    # print desc

    objectsCount += 1

print objectsCount