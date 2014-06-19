__author__ = 'VadShaytReth'


import Queue
import time
import csv
from threading import Thread

csv_source = '../temp.csv'


def do_work(item):
    print("processing", item)


def source():
    with open(csv_source, 'rb') as csvfile:
        product_row = csv.reader(csvfile)
        for row in product_row:
            yield row[3]
            yield row[4]


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
    for product_row in source():
        print product_row