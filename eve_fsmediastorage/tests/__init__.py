import os
import unittest

import eve
import simplejson as json
from eve_fsmediastorage.tests.test_settings import (MONGO_DBNAME,
                                                    MONGO_HOST,
                                                    MONGO_PASSWORD,
                                                    MONGO_PORT,
                                                    MONGO_USERNAME)
from flask_pymongo import MongoClient


class ValueStack(object):
    """
    Descriptor to store multiple assignments in an attribute.

    Due to the multiple self.app = assignments in tests, it is difficult to
    keep track by hand of the applications created in order to close their
    database connections. This descriptor helps with it.
    """
    def __init__(self, on_delete):
        """
        :param on_delete: Action to execute when the attribute is deleted
        """
        self.elements = []
        self.on_delete = on_delete

    def __set__(self, obj, val):
        self.elements.append(val)

    def __get__(self, obj, objtype):
        return self.elements[-1] if self.elements else None

    def __delete__(self, obj):
        for item in self.elements:
            self.on_delete(item)
        self.elements = []


def close_pymongo_connection(app):
    """
    Close the pymongo connection in an eve/flask app
    """
    if 'pymongo' not in app.extensions:
        return
    del app.extensions['pymongo']
    del app.media


class TestMinimal(unittest.TestCase):
    """ Start the building of the tests for an application
    based on Eve by subclassing this class and provide proper settings
    using :func:`setUp()`
    """
    app = ValueStack(close_pymongo_connection)

    def setUp(self, settings_file=None, url_converters=None):
        """ Prepare the test fixture

        :param settings_file: the name of the settings file.  Defaults
                              to `eve/tests/test_settings.py`.
        """
        self.this_directory = os.path.dirname(os.path.realpath(__file__))
        if settings_file is None:
            # Load the settings file, using a robust path
            settings_file = os.path.join(self.this_directory,
                                         'test_settings.py')

        self.connection = None
        self.setupDB()

        self.settings_file = settings_file
        self.app = eve.Eve(settings=self.settings_file,
                           url_converters=url_converters)

        self.test_client = self.app.test_client()

        self.domain = self.app.config['DOMAIN']

    def tearDown(self):
        del self.app
        self.dropDB()

    def setupDB(self):
        self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
        self.connection.drop_database(MONGO_DBNAME)
        if MONGO_USERNAME:
            self.connection[MONGO_DBNAME].add_user(MONGO_USERNAME,
                                                   MONGO_PASSWORD)
        self.bulk_insert()

    def bulk_insert(self):
        pass

    def get(self, resource, query='', item=None):
        if resource in self.domain:
            resource = self.domain[resource]['url']
        if item:
            request = '/%s/%s%s' % (resource, item, query)
        else:
            request = '/%s%s' % (resource, query)

        r = self.test_client.get(request)
        return self.parse_response(r)

    def post(self, url, data, headers=None, content_type='application/json'):
        if headers is None:
            headers = []
        headers.append(('Content-Type', content_type))
        print(headers)
        print(json.dumps(data))
        r = self.test_client.post(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def parse_response(self, r):
        try:
            v = json.loads(r.get_data())
        except json.JSONDecodeError:
            v = None
        return v, r.status_code

    def dropDB(self):
        self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
        self.connection.drop_database(MONGO_DBNAME)
        self.connection.close()
