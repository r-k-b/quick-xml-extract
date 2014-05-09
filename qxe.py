import elementtree.ElementTree as ETree
from pprint import pprint as pp
import csv
from slugify import slugify

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
unknown_sku_count = 0

# This csv file will be overwritten each run.
with open('temp.csv', 'wb') as csvfile:
    writer = csv.writer(
        csvfile,
        delimiter=',',
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL)

    # Header row.
    writer.writerow([
        'Product Code',
        'Name',
        'Description',
        'Small Image',
        'Large Image',
        'Catalogue',
        'Sale Price',
        'Retail Price',
        'Tax Code',
        'SEO friendly URL',
        'Grouping Product Codes',
        'Grouping Product Descriptions',
        'Supplier CRM ID',
        'Supplier Commission Percentage',
        'Weighting/Order',
        'Related Products',
        'Weight In KG/Pounds',
        'Product Width (Previously Volume)',
        'Keywords',
        'Unit Type',
        'Min Units',
        'Max Units',
        'In Stock',
        'On Order',
        'Re-order Threshold',
        'Inventory Control',
        'Can Pre-Order',
        'Custom 1',
        'Custom 2',
        'Custom 3',
        'Custom 4',
        'Poplets',
        'Enabled',
        'Capture Details',
        'Limit Download Count',
        'Limit Download IP',
        'On Sale',
        'Hide if Out of Stock',
        'Attributes',
        'Gift Voucher',
        'Drop Shipping',
        'Product Height',
        'Product Depth',
        'Exclude From Search Results',
        'Product Title',
        'Wholesale Sale Price',
        'Tax Code',
        'Cycle Type',
        'Cycle Type Count',
        'Product URL',
        'Product Affiliate URL',
        'Variations Enabled',
        'Variations Code',
        'Variation Options',
        'Role Responsible',
        'Product Meta Description'
    ])

    for item in docroot.findall('channel/item'):
        title = item.find('title').text
        link = item.find('link').text
        desc = item.find(ns('content', 'encoded')).text
        # Source might have non-ascii chars, which CSV parsers will choke on
        try:
            desc = desc.encode('ascii', 'ignore')
        except AttributeError:
            desc = ''

        img_sml = 'http://placehold.it/296x316'
        img_lrg = 'http://placehold.it/318x415&text={}'.format(
            # Would like to have the spaces kept as '+', but slugify's dashes
            # will do for now.
            slugify(title.replace(' ', '+'))
        )

        categories = ''
        for cat in item.findall('category'):
            categories += '/i/{};'.format(cat.text)

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

        # Avoid None values (can't pass in values like AU/; )
        price_regular_raw = get_key_val('_wpsc_price') or '0.00'
        price_regular = 'AU/{};'.format(price_regular_raw)
        price_special_raw = get_key_val('_wpsc_special_price') or '0.00'
        price_special = 'AU/{};'.format(price_special_raw)

        sku = get_key_val('_wpsc_sku')
        try:
            sku_length = len(sku)
        except TypeError:
            sku_length = 0
        if sku_length < 2:
            sku = 'UNKNOWN-{}'.format(unknown_sku_count)
            unknown_sku_count += 1

        # print price_special, title
        # print desc

        # @formatter:off
        writer.writerow([
            sku,                    # Product Code
            title,                  # Name
            desc,                   # Description
            img_sml,                # Small Image
            img_lrg,                # Large Image
            categories,             # Catalogue
            price_special,          # Sale Price
            price_regular,          # Retail Price
            '',                     # Tax Code
            '',                     # SEO friendly URL
            '',                     # Grouping Product Codes
            '',                     # Grouping Product Descriptions
            '',                     # Supplier CRM ID
            '',                     # Supplier Commission Percentage
            '',                     # Weighting/Order
            '',                     # Related Products
            '',                     # Weight In KG/Pounds
            '',                     # Product Width (Previously Volume)
            '',                     # Keywords
            '',                     # Unit Type
            '1',                    # Min Units
            '',                     # Max Units
            '',                     # In Stock
            '0',                    # On Order
            '',                     # Re-order Threshold
            'N',                    # Inventory Control
            'N',                    # Can Pre-Order
            '',                     # Custom 1
            'custom2 text',         # Custom 2
            '',                     # Custom 3
            link,                   # Custom 4
            '',                     # Poplets
            'Y',                    # Enabled
            'N',                    # Capture Details
            '',                     # Limit Download Count
            '',                     # Limit Download IP
            'Y',                    # On Sale
            'N',                    # Hide if Out of Stock
            '',                     # Attributes
            'N',                    # Gift Voucher
            'N',                    # Drop Shipping
            '',                     # Product Height
            '',                     # Product Depth
            'N',                    # Exclude From Search Results
            '',                     # Product Title
            'AU/0.00;',             # Wholesale Sale Price
            '',                     # Tax Code
            '1',                    # Cycle Type
            '',                     # Cycle Type Count
            '',                     # Product URL
            '',                     # Product Affiliate URL
            'N',                    # Variations Enabled
            '',                     # Variations Code
            '',                     # Variation Options
            '',                     # Role Responsible
            ''                      # Product Meta Description
        ])
        # @formatter:on

        objectsCount += 1

print '{} objects processed.'.format(objectsCount)

