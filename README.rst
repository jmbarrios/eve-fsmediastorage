Eve FileSystemStorage
=====================

Eve ``FileSystemStorage`` class is a helper class to store uploaded files on the
server filesystem.

The class was inspired on the implemented `GridFS MediaStorage`_.

Using Eve FileSystemMediaStorage class
---------------------------------
.. code-block:: python

    from eve import Eve
    from eve_fsmediastorage import FileSystemMediaStorage

    app = Eve(media=FileSystemMediaStorage)
    app.run()

The variable ``MEDIA_PATH`` must be declared on the ``settings.py`` file, and 
it is assume that the related endpoint schema is like:

.. code-block:: python

    accounts_schema = {
        ...
        'pic': {'type': 'media'},
        ...
    }

Then you can upload a file to the API with a ``POST`` request encoding the body
form data as ``multipart/form-data``. Using ``curl`` this can be done as:

.. code:: console
    
    $ curl -F "pic=@profile.jpg;type=image/jpeg" http://example.com/accounts

As in the GridFS, ``EXTENDED_MEDIA_INFO`` can be used to provide extra 
information on the file response. Supported values are ``content_type``, 
``length``, ``md5``, ``name``, ``original_filename``, and ``upload_date``.

Eve is thoroughly tested under Python 2.6, 2.7, 3.3, 3.4 and PyPy.

`Check out the Eve Website <http://python-eve.org/>`_

.. _GridFS MediaStorage: http://python-eve.org/features.html#file-storage
