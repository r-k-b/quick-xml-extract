import csv
from pprint import pprint as pp
import elementtree.ElementTree as ETree
from slugify import slugify
from urlparse import urlparse


namespace = {
    'excerpt': "http://wordpress.org/export/1.2/excerpt/",
    'content': "http://purl.org/rss/1.0/modules/content/",
    'wfw': "http://wellformedweb.org/CommentAPI/",
    'dc': "http://purl.org/dc/elements/1.1/",
    'wp': "http://wordpress.org/export/1.2/"
}


def ns(nspace, tagname):
    """
    used to match namespaced tags, like <wp:post_type>

    :param nspace:
    :param tagname:
    :return:
    """
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
default_image_small = 'http://placehold.it/296x316&text=Image+Coming+Soon'
default_image_large = 'http://placehold.it/318x415&text='
imported_images_path = '/images/imp/'


def map_imported_image_url(original_image_url):
    """
    Map the imported image URLs to their new home. E.g.:

    'http://sprinklersystemshop.com.au/files/2012/06/Xcore-outdoor.jpg'

    becomes

    '/images/imp/2012/06/Xcore-outdoor.jpg'

    :param original_image_url: string
    :return: string
    """
    orig = urlparse(original_image_url).path

    # Remove the trailing slash from the imported_images_path
    return orig.replace('/files', imported_images_path[:-1])


def extract_metakeys(targetitem):
    """
    Turn the <wp:...> tags into a dict.

    Sample XML:
        <wp:postmeta>
            <wp:meta_key>_wpsc_custom_thumb_w</wp:meta_key>
            <wp:meta_value><![CDATA[foo]]></wp:meta_value>
        </wp:postmeta>
        <wp:postmeta>
            <wp:meta_key>_wpsc_custom_thumb_h</wp:meta_key>
            <wp:meta_value><![CDATA[bar]]></wp:meta_value>
        </wp:postmeta>

    :param targetitem:
    :return: dict, like:
    {
        _wpsc_custom_thumb_w: 'foo',
        _wpsc_custom_thumb_h: 'bar'
    }
    """
    metakey_dict = {}
    for metakey in targetitem.findall(ns('wp', 'postmeta')):
        # ETree.dump(metakey)
        metakey_dict[metakey[0].text] = metakey[1].text
    return metakey_dict


def get_key_val(keyset, keyname, default_val=''):
    """
    Safely get key values, returns a default value if key is not present.

    :param keyset:
    :param keyname:
    :param default_val:
    :return:
    """
    try:
        return keyset[keyname]
    except KeyError:
        return default_val


def retrieve_attachment_urls(attachment_docroot=docroot):
    """
    Iterate once over the whole XML, create list to match attachment id (wp:post_id) to image URL
    :param attachment_docroot:
    :return:
    """
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


def retrieve_attachment_urls_for_all_postids(attachment_docroot=docroot):
    """
    Iterate once over the whole XML, create a lookup of all images that reference a particular parent post.

    A parent post may have zero or more image URLs.

    :param attachment_docroot:
    :return: dict of arrays, like:
    {
        123: ['/img/a.jpg', '/img/b.jpg'],
        ...
    }
    """
    the_list = {}
    for attachment_item in attachment_docroot.findall('channel/item'):
        if attachment_item.find(ns('wp', 'post_type')).text == 'attachment':
            post_parent = attachment_item.find(ns('wp', 'post_parent')).text
            attachment_url = map_imported_image_url(
                attachment_item.find(ns('wp', 'attachment_url')).text
            )

            # Values are always either undefined or lists
            try:
                the_list[post_parent].append(attachment_url)
            except KeyError:
                the_list[post_parent] = [attachment_url]

    # pp(the_list)
    return the_list


attachment_url_by_id = retrieve_attachment_urls(docroot)
attachment_images_by_parent_postid = retrieve_attachment_urls_for_all_postids(docroot)

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

            # Fill poplet image field, and overwrite the 'thumbnail' image if we can.
            poplet_images = ''
            try:
                for imgurl in attachment_images_by_parent_postid[item.find(ns('wp', 'post_id')).text]:
                    poplet_images += imgurl + ';'

                    # Just keep the latest image URL, for simplicity.
                    # TODO: which image should we use for the primary? The largest?
                    product_image_small = imgurl
                    product_image_large = imgurl
            except KeyError:
                # No images associated with this wp:post_id.
                pass

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
                poplet_images,          # Poplets
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
