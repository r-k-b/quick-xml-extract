__author__ = 'VadShaytReth'


import Queue
import csv
import os
from pprint import pprint as pp
from threading import Thread

q = Queue.Queue(maxsize=0)
csv_source = '../temp.csv'
url_prefix_to_strip = '/images/imp'
url_prefix_to_add = 'http://eangulus.com/bwidubbo/files'
image_drop_folder = '../data/images'


def do_work(item):
    print("processing", item)


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
        q.put( transform_url(item))

    q.join()       # block until all tasks are done


if __name__ == '__main__':
    # Get URLs to work on
    set_of_urls = set()
    for image_url in source():
        set_of_urls.add( transform_url(image_url))

    pp(set_of_urls)

    # TODO: Drop any we already have the file for
    # for image_url in set_of_urls:


    # Fetch & save the rest