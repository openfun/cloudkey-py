try:
    import unittest2 as unittest
except ImportError, e:
    import unittest

from urllib import urlencode

from mock import patch, Mock

import cloudkey


def no_sign_url(*args, **kwargs):
    '''Mock the sign_url function, and return the url unmodified.
    '''
    return args[0]


class GetStreamUrl(unittest.TestCase):

    def setUp(self):
        self.client = Mock()
        self.client._user_id = '1' * 24
        self.client._api_key = '9' * 42

        self.media = cloudkey.MediaObject(self.client, 'name')
        self.id = '2' * 24
        self.cdn_url = 'http://cdn.dmcloud.net'
        self.static_url = 'http://static.dmcloud.net'

    def test_get_stream_url_static(self):
        asset_name = 'jpeg_thumbnail_medium'
        extension = 'jpeg'
        cdn_url = 'http://cdn.dmcloud.net'

        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_stream_url(self.id, asset_name=asset_name, cdn_url=self.cdn_url)

        self.assertEquals(res, '%s/%s/%s/%s.%s' % (self.static_url, self.client._user_id, self.id, asset_name, extension))
        self.assertFalse(sign_url_mock.called)

    def test_get_stream_url_sign(self):
        asset_name = 'mp4_h264_aac'
        extension = 'mp4'

        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_stream_url(self.id, asset_name=asset_name, cdn_url=self.cdn_url)

        self.assertEquals(res, '%s/route/%s/%s/%s.%s' % (self.cdn_url, self.client._user_id, self.id, asset_name, extension))
        self.assertEquals(sign_url_mock.call_args[0], (res, self.client._api_key))

    def test_get_stream_url_version(self):
        asset_name = 'mp4_h264_aac'
        extension = 'mp4'
        version = 123456

        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_stream_url(self.id, asset_name=asset_name, version=version, cdn_url=self.cdn_url)

        self.assertEquals(res, '%s/route/%s/%s/%s-%s.%s' % (self.cdn_url, self.client._user_id, self.id, asset_name, version, extension))
        self.assertTrue(sign_url_mock.called)

    def test_get_stream_url_timestamp_not_static(self):
        asset_name = 'mp4_h264_aac'
        extension = 'mp4'
        expires = '123456'

        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_stream_url(self.id, asset_name=asset_name, expires=expires, cdn_url=self.cdn_url)

        self.assertEquals(res, '%s/route/%s/%s/%s.%s' % (self.cdn_url, self.client._user_id, self.id, asset_name, extension))
        self.assertTrue(sign_url_mock.called)

    def test_get_stream_url_timestamp_static(self):
        asset_name = 'jpeg_thumbnail_medium'
        extension = 'jpeg'
        expires = '123456'

        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_stream_url(self.id, asset_name=asset_name, expires=expires, cdn_url=self.cdn_url)

        self.assertEquals(res, '%s/%s/%s/%s-%s.%s' % (self.static_url, self.client._user_id, self.id, asset_name, expires, extension))
        self.assertFalse(sign_url_mock.called)

    def test_get_stream_url_download_no_filename(self):
        asset_name = 'mp4_h264_aac'
        extension = 'mp4'
        download = True
        filename = None

        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_stream_url(self.id, asset_name=asset_name, download=download, filename=filename, cdn_url=self.cdn_url)

        self.assertEquals(res, '%s/route/http/%s/%s/%s.%s' % (self.cdn_url, self.client._user_id, self.id, asset_name, extension))
        self.assertTrue(sign_url_mock.called)

    def test_get_stream_url_filename_no_download(self):
        asset_name = 'mp4_h264_aac'
        extension = 'mp4'
        download = False
        filename = 'test_&!filename.mp4'

        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_stream_url(self.id, asset_name=asset_name, download=download, filename=filename, cdn_url=self.cdn_url)

        self.assertEquals(res, '%s/route/http/%s/%s/%s.%s?%s' % (self.cdn_url, self.client._user_id, self.id, asset_name, extension, urlencode({'filename': filename.encode('utf-8', 'ignore')})))
        self.assertTrue(sign_url_mock.called)

    def test_get_stream_url_bad_protocol(self):
        asset_name = 'mp4_h264_aac'
        extension = 'mp4'
        protocol = 'bad'

        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            self.assertRaises(cloudkey.InvalidParameter, self.media.get_stream_url, self.id, asset_name=asset_name, protocol=protocol, cdn_url=self.cdn_url)

    def test_get_stream_url_protocol_http(self):
        asset_name = 'mp4_h264_aac'
        extension = 'mp4'
        protocol = 'http'

        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_stream_url(self.id, asset_name=asset_name, protocol=protocol, cdn_url=self.cdn_url)

        self.assertEquals(res, '%s/route/%s/%s/%s/%s.%s' % (self.cdn_url, protocol, self.client._user_id, self.id, asset_name, extension))
        self.assertTrue(sign_url_mock.called)


class GetEmbedUrl(unittest.TestCase):

    def setUp(self):
        self.client = Mock()
        self.client._user_id = '1' * 24
        self.client._api_key = '9' * 42
        self.client._base_url = 'http://base.url'
        self.client._secure_base_url = 'https://base.url'

        self.media = cloudkey.MediaObject(self.client, 'name')
        self.id = '2' * 24

    def test_get_embed_url(self):
        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_embed_url(self.id)

        self.assertEquals(res, '%s/embed/%s/%s' % (self.client._base_url, self.client._user_id, self.id))
        self.assertEquals(sign_url_mock.call_args[0], (res, self.client._api_key))

    def test_get_embed_url_https(self):
        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_embed_url(self.id, secure=True)

        self.assertEquals(res, '%s/embed/%s/%s' % (self.client._secure_base_url, self.client._user_id, self.id))
        self.assertEquals(sign_url_mock.call_args[0], (res, self.client._api_key))


class GetQtrefUrl(unittest.TestCase):

    def setUp(self):
        self.client = Mock()
        self.client._user_id = '1' * 24
        self.client._api_key = '9' * 42
        self.client._base_url = 'http://base.url'

        self.media = cloudkey.MediaObject(self.client, 'name')
        self.id = '2' * 24

    def test_get_embed_url(self):
        with patch.object(cloudkey, 'sign_url') as sign_url_mock:
            sign_url_mock.side_effect = no_sign_url
            res = self.media.get_qtref_url(self.id)

        self.assertEquals(res, '%s/stream/%s/%s.mov' % (self.client._base_url, self.client._user_id, self.id))
        self.assertEquals(sign_url_mock.call_args[0], (res, self.client._api_key))
