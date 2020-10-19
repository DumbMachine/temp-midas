import os

from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    TESTING = True
    DATASET_LOCATION = os.path.join(basedir, "storage", "dataset.csv")
    UPLOAD_FOLDER = '/root/uploads'