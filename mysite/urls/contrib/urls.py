from django.utils.translation import ugettext as _

from w3lib.url import canonicalize_url
from urllib3 import exceptions as ex

import certifi
import urllib3

allowed_schema = [ 'http', 'https' ]
pool = urllib3.PoolManager(
        cert_reqs = 'CERT_REQUIRED', 
        ca_certs = certifi.where())

basic_error_msgs = {
        ex.NewConnectionError: 'We could not establish a connection to that site',
        ex.SSLError: 'There was a problem with the site\'s SSL certificate', 
        ex.MaxRetryError: 'The maximum number of retries was exceeded while trying to connect', 
        ex.EmptyPoolError: 'Please try again later', 
}

class ValidationError(Exception):
    
    def __init__(self, message):
        self.message = message

def validate_url(url, allowed_schema = allowed_schema, timeout = 2.0):
    """
    Validates a url. 

    Args:
        url:            the url as parsed by urllib.parse
        allowed_schema: a collection of allowed schemas (ex: [ 'http', 'https' ])

    Raises:
        ValidationError: with a descriptive message where possible, if the url was invalid
    """
    indexof = url.find('://')
    if indexof == -1 or url[0:indexof] not in allowed_schema:
        raise ValidationError(_('The scheme must be http or https'))

    str = None
    try:
        response = pool.request('HEAD', url, timeout = timeout)

        if response.status == 404:
            str = _('The webpage could not be found')
        elif response.status != 200:
            str = _('The site returned the error code "') + str(response.status) + '"'
    except urllib3.exceptions.MaxRetryError as e:
        t = type(e.reason)
        str = basic_error_msgs.get(t)
        if not str:
            if t == ex.ResponseError and str(e.reason) == 'too many redirects':
                str = _('The maximum number of retries was exceeded while trying to connect')
            else:
                str = _('A problem occured, please try a different url')
    if str:
        raise ValidationError(str)

def canonicalize(url, default_scheme = 'http'):
    """
    Canonicalize the given url by applying the following procedures:

    * Sort query arguments, first by key, then by value
    * Percent encode paths ; non-ASCII characters are percent-encoded using UTF-8 (RFC-3986)
    * Percent encode query arguments ; non-ASCII characters are percent-encoded using UTF-8 
    * Normalize all spaces (in query arguments) ‘+’ (plus symbol)
    * Normalize percent encodings case (%2f -> %2F)
    * Remove query arguments with blank values
    * Keeps fragments

    If the url does not have a scheme the default scheme is joined with the url.

    See:
       http://w3lib.readthedocs.io/en/latest/w3lib.html#w3lib.url.canonicalize_url 

    Args:
        url: the url as a string
        default_scheme: if a scheme is not present

    Returns:
        the canonicalized url
    """
    if url.find('://') == -1:
        url = default_scheme + '://' + url
    return canonicalize_url(url, keep_fragments = True)

def hostname(url):
    """
    Attempts to extract the hostname from the url.

    Args:
        url: the url

    Returns:
        the hostname
    """
    start = url.find('://')
    start = start + 3 if start != -1 else 0
    end = url.find('/', start) 
    end = end if end != -1 else start
    url = url[start:end]
    parts = url.split('.')
    return ' '.join(part.title() for part in reversed(parts) if len(part) > 3)
