# -*- coding: utf-8 -*-

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USERNAME = MONGO1_USERNAME = 'test_user'
MONGO_PASSWORD = MONGO1_PASSWORD = 'test_pw'
MONGO_DBNAME = 'eve_test'

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE', 'PUT']

files = {
    'url': 'arbitraryurl',
    'item_title': 'files',
    'schema': {
        'ref': {
            'type': 'string',
            'minlength': 25,
            'maxlength': 25,
            'required': True,
            'unique': True,
        },
        'media': {
            'type': 'media'
        }
    }
}

DOMAIN = {
    'files': files
}
