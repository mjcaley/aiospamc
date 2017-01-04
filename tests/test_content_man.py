#!/usr/bin/env python3

import zlib

import pytest

from aiospamc.content_man import BodyHeaderManager
from aiospamc.headers import Compress, ContentLength


class TestBodyHeaderManager:
    def test_instantiates_default(self):
        man = BodyHeaderManager()
        assert 'man' in locals()

    def test_instantiates_with_body(self):
        man = BodyHeaderManager(body='Test body\n')
        assert hasattr(man, '_body')

    def test_instantiates_with_header(self):
        man = BodyHeaderManager(None, ContentLength(length=0))
        assert man._headers['Content-length']

    def test_content_length_added(self):
        man = BodyHeaderManager()
        man.body = 'Test body\n'
        assert man._headers['Content-length']

    def test_compressed_when_header_added(self):
        man = BodyHeaderManager('Test body\n')
        man.add_header(Compress())
        assert zlib.decompress(man._body) == b'Test body\n'

    def test_decompress_when_header_removed(self):
        man = BodyHeaderManager('Test body\n', Compress())
        man.delete_header('Compress')
        assert man._body == b'Test body\n'

    def test_delete_body_deleted_content_length(self):
        man = BodyHeaderManager(body='Test body\n')
        del man.body
        assert 'Content-length' not in man._headers

    def test_add_header(self):
        man = BodyHeaderManager()
        man.add_header(ContentLength(length=0))
        assert man._headers['Content-length']

    def test_get_header(self):
        man = BodyHeaderManager()
        man.add_header(ContentLength(length=0))
        assert isinstance(man.get_header('Content-length'), ContentLength)

    def test_get_header_doesnt_exist(self):
        man = BodyHeaderManager()
        with pytest.raises(KeyError):
            man.get_header('FakeHeader')

    def test_delete_header(self):
        man = BodyHeaderManager(None, ContentLength(length=0))
        man.delete_header('Content-length')
        assert 'Content-length' not in man._headers.keys()
