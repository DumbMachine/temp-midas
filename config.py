import os

from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    TESTING = True
    if TESTING:
        UPLOAD_FOLDER = os.path.join(basedir, "storage")
    else:
        UPLOAD_FOLDER = '/root/uploads'
    
    DATASET_LOCATION = os.path.join(basedir, "storage", "dataset.csv")