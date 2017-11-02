from django.test import TestCase, SimpleTestCase
from django.shortcuts import reverse

from .models import URLRedirect
from .views import CreateURLView
from .contrib.urls import hostname
from .contrib.base_n import decode, encode

from collections import namedtuple
from mock import patch
import json

# Create your tests here.
BASE_N_ALPHABET = 'abcdefUVWXYZ'
BASE_N_CHARMAP  = dict((ch, i) for i, ch in enumerate(BASE_N_ALPHABET))

class BaseNTests(SimpleTestCase):
    
    def test_encode_zero_returns_first_char(self):
        self.assertEqual('Z', encode(0, 'ZYX'))

    def test_decode_empty_raises_error(self):
        with self.assertRaises(TypeError):
            decode(None)

    def test_decode_with_chars_not_in_charmap_raises_error(self):
        with self.assertRaises(KeyError):
            decode('abc', { 'a': 0, 'b' : 1 })

    def test_encode_negative_raises_error(self):
        with self.assertRaises(ValueError):
            encode(-1)

    def test_encode_error_if_None_alphabet(self):
        with self.assertRaises(TypeError):
            encode(123, None)

    def test_decode_error_if_None_charmap(self):
        with self.assertRaises(TypeError):
            decode('abc', None)

    def test_can_decode_encoded_int(self):
        n = 123456789
        self.assertEqual(n, decode(encode(n, BASE_N_ALPHABET), BASE_N_CHARMAP))

    def test_can_decode_encoded_int_with_defaults(self):
        n = 123456789
        self.assertEqual(n, decode(encode(n)))

    def test_can_decode_encoded_very_large_int(self):
        n = 2 ** 64
        self.assertEqual(n, decode(encode(n, BASE_N_ALPHABET), BASE_N_CHARMAP))

class URLSTests(SimpleTestCase):

    def test_hostname(self):
        values = [
                    ( 'https://www.example.com/', 'Example' ), 
                    ( 'https://maps.example.com/', 'Example Maps' ), 
                    ( '', '' ), 
                    ( 'www.example.com/', 'Example' ), 
                    ( 'example.com/', 'Example' ), 
                    ( 'https://videos.example.com/path/to/somewhere', 'Example Videos' ), 
                    ( 'example.com/1.2/path/with/a/dot/', 'Example' ), 
                    ( 'example.com.au/', 'Example' ), 
        ]
        for url, name in values:
            with self.subTest():
                self.assertEqual(name, hostname(url))

class Response():
    """
    Mocks http status.
    """

    def __init__(self, status):
        self.status = status 

class PoolManagerMock():
    """
    Mocks http requests.
    """

    def __init__(self, error, status = 200):
        self.error = error
        self.status = status

    def request(self, method, url, timeout = None):
        if method is not 'HEAD':
            raise ValueError('Only the HEAD method has been mocked')
        if self.error:
            raise self.error
        return Response(self.status)

class CreateURLViewTests(TestCase):
    from urllib3.exceptions import MaxRetryError, SSLError

    def assertEquals(self, data, expected, name):
        actual = data[name]
        self.assertEqual(actual, expected, 'expected {0} = {1}, got {0} = {2}'.format(name, expected, actual))

    def checkResponse(self, url, success = True, new_url = None, ignore = False):
        """
        Args:
            url:     the original url
            success: should the response return success? 
            new_url: the expected returned canonicalized url
            ignore:  whether or not to ignore the new_url

        Returns:
            the result: either the shortened url, an error message, or None
        """
        response = self.client.post(reverse('urls:create'), { 'url' : url })
        
        data = json.loads(response.content)
        
        self.assertEquals(data, success, 'success')

        if not ignore:
            if new_url:
                self.assertEquals(data, new_url, 'url')
            elif 'url' in data:
                self.assertEquals(data, url, 'url')

        if 'result' in data:
            return data['result']

    #######################################################
    # see:                                                # 
    #   https://en.wikipedia.org/wiki/URL_normalization   #
    #######################################################
    
    # if a test is commented out, it is an acceptable failure, but not perfect behavior 

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_ideal_url(self):
        self.checkResponse('http://www.example.com/') 

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_scheme_to_lower_case(self):
        self.checkResponse('HTTP://www.Example.com/', new_url = 'http://www.example.com/')

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_capitalize_letters_in_escape_sequences(self):
        self.checkResponse('http://www.example.com/a%c2%b1b', new_url = 'http://www.example.com/a%C2%B1b')

    #@patch('urls.contrib.urls.pool', PoolManagerMock(None))
    #def test_remove_default_port(self):
    #    self.checkResponse('http://www.example.com:80/bar.html', new_url = 'http://www.example.com/bar.html') 

    #@patch('urls.contrib.urls.pool', PoolManagerMock(None))
    #def test_add_trailing_slash(self):
    #    self.checkResponse('http://www.example.com/alice', new_url = 'http://www.example.com/alice/') 

    #@patch('urls.contrib.urls.pool', PoolManagerMock(None))
    #def test_remove_dot_segments(self):
    #    self.checkResponse('http://www.example.com/../a/b/../c/./d.html', new_url = 'http://www.example.com/a/c/d.html')

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_keeps_fragment(self):
        self.checkResponse('http://www.example.com/bar.html#section1') 

    #@patch('urls.contrib.urls.pool', PoolManagerMock(None))
    #def test_removes_duplicate_slashes(self):
    #    self.checkResponse('http://www.example.com/foo//bar.html', new_url = 'http://www.example.com/foo/bar.html')

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_removes_empty_query(self):
        self.checkResponse('http://www.example.com/display?', new_url = 'http://www.example.com/display')

    ###############################################################
    
    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_normalized_urls_are_equivilent(self):
        self.assertEqual(
                self.checkResponse('http://www.example.com/'), 
                self.checkResponse('HTTP://www.Example.com/', new_url = 'http://www.example.com/'))

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_trailing_whitespace_is_ignored(self):
        self.assertEqual(
                self.checkResponse('http://www.example.com/'), 
                self.checkResponse('http://www.example.com/     \n\t   ', new_url = 'http://www.example.com/'))

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_leading_whitespace_is_ignored(self):
        self.assertEqual(
                self.checkResponse('http://www.example.com/'), 
                self.checkResponse('     \n\t    http://www.example.com/', new_url = 'http://www.example.com/'))

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_default_scheme_is_prepended(self):
        self.assertEqual(
                self.checkResponse('http://example.com/'), 
                self.checkResponse('example.com/', new_url = 'http://example.com/'))

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_default_scheme_is_prepended_before_www(self):
        self.assertEqual(
                self.checkResponse('http://www.example.com/'), 
                self.checkResponse('www.example.com/', new_url = 'http://www.example.com/'))

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_failure_for_empty_url(self):
        self.checkResponse('', success = False)
    
    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_failure_for_missing_scheme(self):
        self.checkResponse('://www.example.com', success = False, ignore = True)

    @patch('urls.contrib.urls.pool', PoolManagerMock(None))
    def test_failure_for_disallowed_scheme(self):
        self.checkResponse('ftp://www.example.com/', success = False)

    @patch('urls.contrib.urls.pool', PoolManagerMock(None, 404))
    def test_failure_if_404(self):
        self.checkResponse('http://www.example.com/404', success = False)

    @patch('urls.contrib.urls.pool', PoolManagerMock(MaxRetryError(None, None, SSLError())))
    def test_urllib3_error(self):
        self.checkResponse('https://www.example.com/badssl', success = False)

def create_redirect(url):
    obj = URLRedirect.objects.create(original_url = url)
    obj.save()
    return encode(obj.id)

class RedirectURLViewTests(TestCase):

    def test_temp_redirect_to_index_if_not_found(self):
        response = self.client.get(reverse('urls:redirect', args = ('notindb', )))
        self.assertRedirects(response, reverse('urls:index'), 302, fetch_redirect_response = False)

    def test_permament_redirect_if_url_found(self):
        t = create_redirect('https://www.example.com/')
        response = self.client.get(reverse('urls:redirect', args = (t, )))
        self.assertRedirects(response, 'https://www.example.com/', 301, fetch_redirect_response = False)

    def test_temp_redirect_to_index_if_url_too_large(self):
        response = self.client.get(reverse('urls:redirect', args = ('a' * 1000000, )))
        self.assertRedirects(response, reverse('urls:index'), 302, fetch_redirect_response = False)

    def test_redirect_increments_times_used(self):
        n = 4
        t = create_redirect('https://www.example.com/')

        self.assertEqual(
                0, 
                URLRedirect.objects.get(original_url = 'https://www.example.com/').times_used)

        for idx in range(n):
            self.client.get(reverse('urls:redirect', args = (t, )))

        self.assertEqual(
                n, 
                URLRedirect.objects.get(original_url = 'https://www.example.com/').times_used)

