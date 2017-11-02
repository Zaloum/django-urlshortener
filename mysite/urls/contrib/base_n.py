ALPHABET = '23456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
CHAR_MAP = dict((ch, idx) for idx, ch in enumerate(ALPHABET))

def encode(n, alphabet = ALPHABET):
    '''
    Encodes a integer.

    Args:
        n:        the integer to encode
        alphabet: a string of unique characters

    Returns:
        a string representing the integer containing only characters from the alphabet

    Raise:
        TypeError:  if alphabet is None
        ValueError: if alphabet is length 0, or n is < 0
    '''
    base = len(alphabet)
    if base == 0:
        raise ValueError('The base must be at least 1')
    elif n < 0:
        raise ValueError('n must be a positive integer (found: {})'.format(n))
    elif n == 0:
        return alphabet[0]

    encoded_str = ''
    while n != 0:
        encoded_str = alphabet[n % base] + encoded_str
        n //= base
    
    return encoded_str

def decode(encoded_str, char_map = CHAR_MAP):
    """
    Decodes a string. 

    Args:
        encoded_str: the string to decode
        char_map:    A dict of (ch, idx) tuples for each character and index in the encoding
                     alphabet

    Returns:
        an integer representing the decoded string
    
    Raises:
        TypeError:  if encoded_str is empty or None, or char_map is None
        ValueError: if char_map is length 0
        KeyError:   if a character is not in char_map
    """
    base = len(char_map)
    if base == 0:
        raise ValueError('The base must be at least 1')

    n = 0
    for idx, ch in enumerate(reversed(encoded_str)):
        n += (base ** idx) * char_map[ch]

    return n
