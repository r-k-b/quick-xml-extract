import csv
# from pprint import pprint as pp
import elementtree.ElementTree as ETree
from slugify import slugify


namespace = {
    'excerpt': "http://wordpress.org/export/1.2/excerpt/",
    'content': "http://purl.org/rss/1.0/modules/content/",
    'wfw': "http://wellformedweb.org/CommentAPI/",
    'dc': "http://purl.org/dc/elements/1.1/",
    'wp': "http://wordpress.org/export/1.2/"
}


def ns(nspace, tagname):
    # used to match namespaced tags, like <wp:post_type>
    r = "{{{a}}}{b}".format(
        a=namespace[nspace],
        b=tagname
    )
    return r


tree = ETree.parse("data/complete-export-sprinklersystemshop.wordpress.2014-05-14.xml")
docroot = tree.getroot()

# thingy = doc.find('channel')
# print thingy.attrib

objectsCount = 0
unknown_sku_count = 0
default_image_small = 'http://placehold.it/296x316'
default_image_large = 'http://placehold.it/318x415&text='
imported_images_path = '/images/imp/'


def extract_metakeys(targetitem):
    metakey_dict = {}
    for metakey in targetitem.findall(ns('wp', 'postmeta')):
        # ETree.dump(metakey)
        metakey_dict[metakey[0].text] = metakey[1].text
    return metakey_dict


def get_key_val(keyset, keyname, default_val=''):
    try:
        return keyset[keyname]
    except KeyError:
        return default_val


def retrieve_attachment_urls(attachment_docroot=docroot):
    the_list = {}
    for attachment_item in attachment_docroot.findall('channel/item'):
        if attachment_item.find(ns('wp', 'post_type')).text == 'attachment':
            attachment_id = attachment_item.find(ns('wp', 'post_id')).text
            attachment_url = get_key_val(
                extract_metakeys(attachment_item),
                '_wp_attached_file'
            )
            # pp(extract_metakeys(attachment_item))
            the_list[attachment_id] = attachment_url
    return the_list


attachment_url_by_id = retrieve_attachment_urls(docroot)

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
        itemtype = item.find(ns('wp', 'post_type')).text
        link = item.find('link').text
        desc = item.find(ns('content', 'encoded')).text
        # Source might have non-ascii chars, which CSV parsers will choke on
        try:
            desc = desc.encode('ascii', 'ignore')
        except AttributeError:
            desc = ''

        if itemtype == 'wpsc-product':

            categories = ''
            for cat in item.findall('category'):
                categories += '/i/{};'.format(cat.text)

            metakeys = extract_metakeys(item)

            # pp(metakeys)

            # Avoid None values (can't pass in values like AU/; )
            price_regular_raw = get_key_val(metakeys, '_wpsc_price') or '0.00'
            price_regular = 'AU/{};'.format(price_regular_raw)

            price_special_raw = get_key_val(metakeys, '_wpsc_special_price') or '0.00'
            price_special = 'AU/{};'.format(price_special_raw)

            sku = get_key_val(metakeys, '_wpsc_sku')
            try:
                sku_length = len(sku)
            except TypeError:
                sku_length = 0
            if sku_length < 2:
                sku = 'UNKNOWN-{}'.format(unknown_sku_count)
                unknown_sku_count += 1

            # Find product image from <wp:post_type>attachment</wp:post_type> items
            # We've already parsed the XML once to get the list into memory
            # Also, this assumes a product has only one 'thumbnail'...
            img_id = get_key_val(metakeys, '_thumbnail_id')
            if len(img_id) > 0:
                try:
                    product_image_small = imported_images_path + attachment_url_by_id[img_id]
                    product_image_large = imported_images_path + attachment_url_by_id[img_id]
                except KeyError:
                    product_image_small = 'img_id_{}'.format(
                        get_key_val(metakeys, '_thumbnail_id')
                    )
                    product_image_large = product_image_small
            else:  # no thumbnail, so use defaults
                product_image_small = default_image_small
                product_image_large = default_image_large + slugify(title)

            # print price_special, title
            # print desc

            # @formatter:off
            writer.writerow([
                sku,                    # Product Code
                title,                  # Name
                desc,                   # Description
                product_image_small,    # Small Image
                product_image_large,    # Large Image
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
