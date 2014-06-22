# coding=utf-8
__author__ = 'VadShaytReth'


import Queue
import csv
import os
import urllib2
from threading import Thread
# noinspection PyUnresolvedReferences
from pprint import pprint as pp

q = Queue.Queue(maxsize=0)
csv_source = '../temp.csv'
url_prefix_to_strip = '/images/imp'
url_prefix_to_add = 'http://eangulus.com/bwidubbo/files'
image_drop_folder = '../data/images'


def do_work(item):
    """
    Downloads a file from the provided URL, and saves it to a folder.
    Preserves some parent folders.

    :param item: Complete URL
    :return: nothing
    """
    image_data = urllib2.urlopen(item)
    image_file_path = get_image_local_path(item)
    print('Saving: {0} to {1}'.format(item,image_file_path))

    # We may need to create several parent folders for the image file
    try:
        os.makedirs(os.path.split(image_file_path)[0])
    except WindowsError:
        # folder(s) already exist.
        pass

    with open(image_file_path, 'wb') as image_file:
        image_file.write(image_data.read())
    print('Done.')


def source():
    """
    Fetch all the poplet URLs from the CSV file.

    :rtype : iterable
    :returns array of strings

    """
    with open(csv_source, 'rb') as csvfile:
        product_row = csv.reader(csvfile)
        for row in product_row:
            if ';' in row[31]:
                for url in row[31].split(';'):
                    if len(url) > 1:
                        yield url


def worker():
    while True:
        item = q.get()
        do_work(item)
        q.task_done()


def transform_url(url=''):
    de_prefixed = url.split(url_prefix_to_strip)[1]
    re_prefixed = url_prefix_to_add + de_prefixed
    return re_prefixed


def get_image_local_path(url=''):
    """
    Map the remote URL with the path we'll be saving the images to.

    'http://eangulus.com/bwidubbo/files/2013/10/tee.jpg' → '../data/images/2013/10/tee.jpg'

    :param url: string
    :return: file path
    :rtype: str or unicode
    """
    de_prefixed = url.split(url_prefix_to_add)[1]
    re_prefixed = image_drop_folder + de_prefixed
    return re_prefixed


def grab(urls_to_grab=None):
    """
    Download images from a defined location.

    :param urls_to_grab: (array|set) of string
    """
    for i in range(3):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    for item in urls_to_grab:
        q.put(item)

    q.join()       # block until all tasks are done


if __name__ == '__main__':
    # Get URLs to work on
    set_of_urls = set()
    for image_url in source():
        set_of_urls.add(transform_url(image_url))

    # TODO: Drop any we already have the file for
    clean_set_of_urls = set()
    for image_url in set_of_urls:
        if not os.path.isfile(get_image_local_path(image_url)):
            clean_set_of_urls.add(image_url)
        else:
            print('Already got: {}'.format(image_url))

    print('Original set length: {}'.format(len(set_of_urls)))
    print('Cleaned set length: {}'.format(len(clean_set_of_urls)))

    # Fetch & save the rest
    grab(clean_set_of_urls)