# -*- coding: utf-8 -*-
'''
Packet with classes for checking proxy servers for types

Библиотека для проверки прокси серверов на поддержку протоколов:
socks: 4 or 5
http: GET or CONNECT


'''

from checkers import *

__version__ = (0, 0, 3)
__author__ = "Alexandr ( http://obout.ru )"
__all__ = ('get_version', 'checkers', 'get_checker', 'BaseChecker', 'SocksChecker', 'HttpChecker', 'ConnectionError', 'RequestError', 'ResponseError', 'ResultError', 'http', 'socksver4', 'socksver5', 'https', 'TypesConsecutiveChecker')


def get_version():
    '''
    get_version() --> lib version
    '''
    import string
    return string.join(map(str, __version__), ".")
    
