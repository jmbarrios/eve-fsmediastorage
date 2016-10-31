from tempfile import mkdtemp
from shutil import rmtree
from io import BytesIO
from eve_fsmediastorage import FileSystemMediaStorage
from eve_fsmediastorage.tests import TestMinimal
from eve import STATUS_OK, STATUS, STATUS_ERR, ISSUES
import base64


class TestFileSystemMediaStorage(TestMinimal):
    def setUp(self):
        super(TestFileSystemMediaStorage, self).setUp()
        # config app to use eve_fsstorage
        self.upload_directory = mkdtemp()
        self.app.config['MEDIA_PATH'] = self.upload_directory
        self.app.media = FileSystemMediaStorage(self.app)
        self.resource = 'files'
        self.url = ('%s' %
                    self.domain[self.resource]['url'])
        self.headers = [('Content-Type', 'multipart/form-data')]
        self.id_field = '_id'
        self.test_field, self.test_value = 'ref', "1234567890123456789054321"
        # we want an explicit binary as Py3 encodestring() expects binaries.
        self.clean = b'my file contents'
        # encodedstring will raise a DeprecationWarning under Python3.3, but
        # the alternative encodebytes is not available in Python 2.
        self.encoded = base64.encodestring(self.clean).decode('utf-8')

    def tearDown(self):
        rmtree(self.upload_directory)
        super(TestFileSystemMediaStorage, self).tearDown()

    def test_filesystem_media_storage_post(self):
        # send something different than a file and get an error back
        data = {'media': 'not a file'}
        r, s = self.parse_response(
            self.test_client.post(self.url, data=data, headers=self.headers))
        self.assertEqual(STATUS_ERR, r[STATUS])

        # validates media fields
        self.assertTrue('file was expected' in r[ISSUES]['media'])
        # also validates ordinary fields
        self.assertTrue('required' in r[ISSUES][self.test_field])

        r, s = self._post()
        self.assertEqual(STATUS_OK, r[STATUS])

        # compare original and returned data
        _id = r[self.id_field]
        self.assertMediaField(_id, self.encoded, self.clean)

        # GET the file at the resource endpoint
        where = 'where={"%s": "%s"}' % (self.id_field, _id)
        r, s = self.parse_response(
            self.test_client.get('%s?%s' % (self.url, where)))
        self.assertEqual(len(r['_items']), 1)
        returned = r['_items'][0]['media']

        # returned value is a base64 encoded string
        self.assertEqual(returned, self.encoded)

        # which decodes to the original clean
        self.assertEqual(base64.decodestring(returned.encode()), self.clean)

    def test_filesystem_media_storage_post_excluded_file_in_result(self):
        # send something different than a file and get an error back
        data = {'media': 'not a file'}
        r, s = self.parse_response(
            self.test_client.post(self.url, data=data, headers=self.headers))
        self.assertEqual(STATUS_ERR, r[STATUS])

        # validates media fields
        self.assertTrue('file was expected' in r[ISSUES]['media'])
        # also validates ordinary fields
        self.assertTrue('required' in r[ISSUES][self.test_field])

        r, s = self._post()
        self.assertEqual(STATUS_OK, r[STATUS])

        self.app.config['RETURN_MEDIA_AS_BASE64_STRING'] = False
        # compare original and returned data
        _id = r[self.id_field]

        # GET the file at the resource endpoint
        where = 'where={"%s": "%s"}' % (self.id_field, _id)
        r, s = self.parse_response(
            self.test_client.get('%s?%s' % (self.url, where)))
        self.assertEqual(len(r['_items']), 1)
        returned = r['_items'][0]['media']

        # returned value is a base64 encoded string
        self.assertEqual(returned, None)

    def test_filesystem_media_storage_post_extended(self):
        r, s = self._post()
        self.assertEqual(STATUS_OK, r[STATUS])

        # request extended format file response
        self.app.config['EXTENDED_MEDIA_INFO'] = ['content_type', 'length']

        # compare original and returned data
        _id = r[self.id_field]
        self.assertMediaFieldExtended(_id, self.encoded, self.clean)

        # GET the file at the resource endpoint
        where = 'where={"%s": "%s"}' % (self.id_field, _id)
        r, s = self.parse_response(
            self.test_client.get('%s?%s' % (self.url, where)))
        self.assertEqual(len(r['_items']), 1)
        returned = r['_items'][0]['media']

        # returned value is a base64 encoded string
        self.assertEqual(returned['file'], self.encoded)

        # which decodes to the original clean
        self.assertEqual(base64.decodestring(returned['file'].encode()),
                         self.clean)

        # also verify our extended fields
        self.assertEqual(returned['content_type'], 'text/plain')
        self.assertEqual(returned['length'], 16)

    def test_fs_media_storage_post_extended_excluded_file_in_result(self):
        r, s = self._post()
        self.assertEqual(STATUS_OK, r[STATUS])

        # request extended format file response
        self.app.config['EXTENDED_MEDIA_INFO'] = ['content_type', 'length']
        self.app.config['RETURN_MEDIA_AS_BASE64_STRING'] = False
        # compare original and returned data
        _id = r[self.id_field]

        # GET the file at the resource endpoint
        where = 'where={"%s": "%s"}' % (self.id_field, _id)
        r, s = self.parse_response(
            self.test_client.get('%s?%s' % (self.url, where)))
        self.assertEqual(len(r['_items']), 1)
        returned = r['_items'][0]['media']

        # returned value is None
        self.assertEqual(returned['file'], None)

        # also verify our extended fields
        self.assertEqual(returned['content_type'], 'text/plain')
        self.assertEqual(returned['length'], 16)

    def assertMediaField(self, _id, encoded, clean):
        # GET the file at the item endpoint
        r, s = self.parse_response(self.test_client.get('%s/%s' % (self.url,
                                                                   _id)))
        returned = r['media']
        # returned value is a base64 encoded string
        self.assertEqual(returned, encoded)
        # which decodes to the original file clean
        self.assertEqual(base64.decodestring(returned.encode()), clean)
        return r, s

    def assertMediaFieldExtended(self, _id, encoded, clean):
        # GET the file at the item endpoint
        r, s = self.parse_response(self.test_client.get('%s/%s' % (self.url,
                                                                   _id)))
        returned = r['media']['file']
        # returned value is a base64 encoded string
        self.assertEqual(returned, encoded)
        # which decodes to the original file clean
        self.assertEqual(base64.decodestring(returned.encode()), clean)
        return r, s

    def _post(self):
        # send a file and a required, ordinary field with no issues
        data = {'media': (BytesIO(self.clean), 'test.txt'), self.test_field:
                self.test_value}
        return self.parse_response(self.test_client.post(
            self.url, data=data, headers=self.headers))
