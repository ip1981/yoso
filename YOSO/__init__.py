from PyQt5.QtWidgets import QApplication
from YOSO.MainWindow import MainWindow
import os
import re
import sys


IMAGE_FILE_TEMPLATES = ['*.png', '*.jpg', '*.jpeg']

def imagesDir(datadir):
    return os.path.join(datadir, 'images')

def labelsDir(datadir):
    return os.path.join(datadir, 'labels')

def classesDir(datadir):
    return os.path.join(datadir, 'classes')

# e. g. "012 - Midi skirt.jpg":
CLASSES_RE = re.compile(r'^0*(?P<cls>\d+)\s*-\s*(?P<name>[^.]+).*$')

# e. g. "1 0.57 0.42 0.17 0.6654"
BBOX_RE = re.compile(
    r'^\s*(?P<cls>\d+)\s+(?P<x>{float})\s+(?P<y>{float})\s+(?P<w>{float})\s+(?P<h>{float}).*$'.format(
        float=r'([0-9]*[.])?[0-9]+'))


def main():
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())

