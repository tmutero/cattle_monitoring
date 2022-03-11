"""
File: tgfileuploader.py
Author: Camilla Buys
Company: Dotxml
Email: camilla at dotxmltech dot com
Github: Not yet
"""

# -*- coding: utf-8 -*-
import os
import json
import subprocess
import hashlib
import uuid
from pkg_resources import resource_filename

import logging
log = logging.getLogger(__name__)

FILENAME = os.path.abspath(resource_filename('radio_rewards', 'public'))
PUBLIC_DIRNAME = os.path.join(FILENAME)
IMAGES_DIRNAME = os.path.join(PUBLIC_DIRNAME, 'img')
UPLOADS_DIRNAME = os.path.join(IMAGES_DIRNAME, 'uploads')

class FileUploader(object):

    def __init__(self, *args, **kwargs):
        self.allowed_extensions = kwargs.get('allowed_extensions', [])
        self.size_limit = kwargs.get('size_limit', 10485760) # 10 MB
        self.upload_dir = kwargs.get('upload_dir', UPLOADS_DIRNAME)
        self.id = kwargs.get('id', None)
        self.request = kwargs
        self.resize = kwargs.get('resize', None)

    def getName(self):
        return self.request['qqfile'].filename

    def handle_file_upload(self, name=None, *args, **kwargs):
        # Check dir is accessible.
        print('self.upload_dir', self.upload_dir)
        ensure_dir(self.upload_dir)
        if not os.access(self.upload_dir, os.W_OK):
            log.warning('handle_file_upload: Upload directory is not writable or executable.')
            return json.dumps({'error':'Server error. Upload directory is not writable or executable.'})

        # Get the file object
        # qqfile is for old way
        # file is for new way
        fileobj = self.request.get('qqfile', None)
        if not fileobj: fileobj = self.request.get('file')

        # Check file size is allowed.
        filesize = int(self.request.get('qqtotalfilesize', 0))
        if filesize == 0:
            filesize = os.fstat(fileobj.file.fileno()).st_size
        if filesize == 0:
            log.warning('handle_file_upload: file_size is 0')
            return json.dumps({'error':'File is empty.'})
        if filesize > self.size_limit:
            log.warning('handle_file_upload: file is too big')
            return json.dumps({'error':'File is too large.'})

        # Check unique identifier exists.
        fileuuid = self.request.get('qquuid', None)
        if not fileuuid:
            fileuuid = hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()

        # Create filename and confirm userdir is accessible.
        userdir = self.upload_dir
        if not name:
            name = '{0}_{1}'.format(fileuuid, fileobj.filename)

        # Check extension is allowed.
        ext = get_extension_from_filename(name)
        print('ext', ext)
        print('self.allowed_extensions', self.allowed_extensions)
        if not (ext in self.allowed_extensions or '.*' not in self.allowed_extensions):
            allowed = ', '.join(self.allowed_extensions)
            log.warning('handle_file_upload: Invalid file extension')
            return json.dumps({'error':'File has invalid extension. It should be one of {0}.'.format(allowed)})

        # Check filepath is accessible and write the file.
        filepath = os.path.join(self.upload_dir, name)
        if filepath:
            uploadname = os.path.basename(filepath)
            with open(filepath, 'wb+') as openfile:
                openfile.write(fileobj.value)
            openfile.close()
            if self.resize: getthumbnail(filepath, filepath)
            return json.dumps({'error':None, 'success':True, 'name':name})
        return json.dumps({'error':'Could not save uploaded file.'})

def getthumbnail(inpath, outpath):
    subprocess.call(['convert', inpath, '-resize', '50!x50!', outpath])

def ensure_dir(filename):
    # dirname = os.path.dirname(filename)
    if not os.path.exists(filename):
        os.makedirs(filename)

def get_extension_from_filename(fileName):
    filename, extension = os.path.splitext(fileName)
    return extension.lower()

