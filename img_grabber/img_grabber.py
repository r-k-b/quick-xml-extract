__author__ = 'VadShaytReth'


import Queue
import csv
from threading import Thread

csv_source = '../temp.csv'


def do_work(item):
    print("processing", item)


def source():
    """
    Fetch all the poplet URLs from the CSV file.

    @:return array of strings

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

q = Queue.Queue(maxsize=0)


def grab(urls_to_check=None):
    if not urls_to_check: urls_to_check = []
    for i in range(3):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    for item in urls_to_check:
        q.put(item)

    q.join()       # block until all tasks are done

if __name__ == '__main__':
    for image_url in source():
        print image_url