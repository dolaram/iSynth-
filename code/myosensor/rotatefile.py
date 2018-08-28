import os
import sys
import datetime

MAXFILESIZE=65536

class RotatingFile(object):
    def __init__(self, directory='', filename='foo', max_files=1024,
        max_file_size=MAXFILESIZE):
        self.ii = 1
        self.directory, self.filename      = directory, filename
        self.max_file_size, self.max_files = max_file_size, max_files
        self.finished, self.fh             = False, None
        self.open()

    def rotate(self):
        """Rotate the file, if necessary"""
        if (os.stat(self.filename_template).st_size>self.max_file_size):
            self.close()
            self.ii += 1
            if (self.ii<=self.max_files):
                self.open()
            else:
                self.close()
                self.finished = True

    def open(self):
        #self.fh = open(self.filename_template, 'w')
        self.fh = open(self.filename_template, 'a+')

    def write(self, text=""):
        try:
            self.fh.write(text)
            self.fh.flush()
            self.rotate()
        except:
            self.open()
            self.write(text)

    def close(self):
        self.fh.close()

    @property
    def filename_template(self):
        #return self.directory + self.filename + "_%0.2d" % self.ii
        return self.directory + self.filename + str(datetime.date.today()) + "_%0.2d" % self.ii + ".txt"

