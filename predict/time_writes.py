import sqlite3

from time import perf_counter
from random import randint, choice
from os.path import join, isfile
from os import remove, listdir

DIR = "/media/paul/Storage/scratch/test"

unlabeled = list(range(100000))
labeled = list(range(10000))

print("Generating data.")
data = [(choice(labeled),
         choice(unlabeled),
         randint(0, 4294967296))
        for _ in range(5000000)]

def write_to_sqlite(data):
    filename = join(DIR, "test.db")
    if isfile(filename): # Clear old versions of this file
        remove(filename)
    con = sqlite3.connect(filename)
    con.execute("""PRAGMA page_size = 32768""");
    con.execute("""CREATE TABLE lengths
                            (unlabeled integer, labeled integer, shared integer)""")
    con.execute("""CREATE INDEX labeled_index
                            ON lengths (labeled)""")
    con.executemany("INSERT INTO lengths VALUES (?, ?, ?)", data)
    con.commit()
    con.close()
    

def write_to_file(data):
    filename = join(DIR, "test.txt")
    with open(filename, "w") as output_file:
        for line in data:
            output_file.write("\t".join(str(val) for val in line) + "\n")

def write_to_directory(data, labeled):
    directory = join(DIR, "test")
    fds = {label: open(join(directory, str(label)), "a")
           for label in labeled}
    for labeled, unlabeled, value in data:
        fd = fds[labeled]
        fd.write(str(unlabeled))
        fd.write("\t")
        fd.write(str(value) + "\n")
    for fd in fds.values():
        fd.close()

def read_from_directory():
    directory = join(DIR, "test")
    data = []
    for labeled_filename in listdir(directory):
        labeled = int(labeled_filename)
        with open(join(directory, labeled_filename), "r") as labeled_file:
            for line in labeled_file:
                unlabeled, shared = line.split("\t")
                data.append((labeled, int(unlabeled), int(shared)))
    return data
    
print("Testing DB speed.")
start = perf_counter()
write_to_sqlite(data)
stop = perf_counter()
print("DB speed: {}".format(stop - start))


print("Testing raw file speed.")
start = perf_counter()
write_to_file(data)
stop = perf_counter()
print("raw file speed: {}".format(stop - start))

print("Testing write to directory speed.")
start = perf_counter()
write_to_directory(data, labeled)
stop = perf_counter()
print("Write to directory speed: {}".format(stop - start))

print("Testing read from directory speed.")
start = perf_counter()
read_from_directory()
stop = perf_counter()
print("Read directory speed: {}".format(stop - start))
