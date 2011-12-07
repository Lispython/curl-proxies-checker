#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
curl_proxies_checker.checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Checker classes

:copyright: (c) 2011 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
"""

import json
import re
import sys
import uuid

import threading
import multiprocessing
import logging
import traceback
from random import choice

## try:
##     from geventcurl import pycurl
##     print("")
## except Exception, e:
##     print(e)

import pycurl

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from user_agents import USER_AGENTS


__version__ = (0, 0, 2)
__author__ = "Alexandr Lispython ( http://obout.ru )"
__all__ = ('BaseChecker', 'HttpChecker', 'Socks4Checker', 'Socks5Checker', 'SerialTypesChecker',
            'TypeCheckerBase', 'ThreadsTypesChecker', 'ImplementationError',
           'USER_AGENTS', 'PROXIES_TYPES_MAP', 'DEFAULT_TIME_OUT', 'get_checker', 'get_version')

def get_version():
    return ".".join(map(str, __version__))

logger = logging.getLogger('curl_proxies_checker')

SOCKS_VER4 = pycurl.PROXYTYPE_SOCKS4
SOCKS_VER5 = pycurl.PROXYTYPE_SOCKS5
HTTP = 'http'
HTTPS = 'https'

PROXIES_TYPES_MAP = {
    'socks5': pycurl.PROXYTYPE_SOCKS5,
    'socks4': pycurl.PROXYTYPE_SOCKS4,
    'http': pycurl.PROXYTYPE_HTTP,
    'https': pycurl.PROXYTYPE_HTTP}

PROXY_TYPES = [HTTP, HTTPS, SOCKS_VER4, SOCKS_VER5]

socksver4 = [SOCKS_VER4, str(SOCKS_VER4), chr(SOCKS_VER4), 'socks4', 'socksver4',
             'socks ver4', 'socksv4', 'socks v4', "SOCKS4"]
socksver5 = [SOCKS_VER5, str(SOCKS_VER5), chr(SOCKS_VER5), 'socks5', 'socksver5',
             'socks ver5', 'socksv5', 'socks v5', "SOCKS5"]
http = [HTTP, "GET"]
https = [HTTPS, "CONNECT"]
allproxies = [socksver4, socksver5, http, https]


# DEFAULTS
DEFAULT_TIME_OUT = 15
SOCKET_RE = re.compile(r'((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))\s*:\s*(\d{2,5})')


def get_code_by_name(name):
    return PROXIES_TYPES_MAP[name]


def get_name_by_code(code):
    for k, v in PROXIES_TYPES_MAP.items():
        if v == code:
            return k


class ImplementationError(Exception):
    pass


class BaseTester(object):
    """Test page data
    """

    def __init__(self, proxy):
        """Init method
        """
        self._test_url = None
        self._proxy_ip, self._proxy_port = proxy
        self._random_key = uuid.uuid4().get_hex()[:10]
        self._random_value = uuid.uuid4().hex

    @property
    def url(self):
        """Returns test url"""
        if not self._test_url:
            return None
        else:
            return "%s?%s=%s" % (self._test_url, self._random_key, self._random_value)

    def test(self, data=None):
        """Parse self._data for known tokens
        """
        raise ImplementationError

    def __call__(self, proxy=None, *args, **kwargs):
        """If call instance
        """
        if proxy:
            self._proxy_ip, self._proxy_port = proxy
        return self


class HWRTTNTester(BaseTester):
    """Test by http://h.wrttn.me
    """

    def __init__(self, *args, **kwargs):
        """Init
        """
        super(HWRTTNTester, self).__init__(*args, **kwargs)
        self._test_url = "http://h.wrttn.me/get"

    def test(self, data=None):
        """Parse data for known tokens
        """
        if data:
            try:
                json_data = json.loads(data)
                args = json_data.get('args', None)
                if not args:
                    return False
                if args.get(self._random_key)[0] == self._random_value:
                ## if json_data.get('ip') == self._proxy_ip or \
                ##        json_data.get('X-Real-Ip') == self._proxy_ip or \
                ##        json_data.get('X-Forwarded-For') == self._proxy_ip:
                    return True
            except Exception, e:
                logger.warn(" %s | %s " % (self, e))
                return False
            return False
        else:
            return False


class HTTPBinTester(BaseTester):
    """Test by http://httpbin.org
    """

    def __init__(self, *args, **kwargs):
        super(HTTPBinTester, self).__init__(*args, **kwargs)
        self._test_url = "http://httpbin.org/get"

    def test(self, data=None):
        """Parse data for known tokens"""
        if data:
            try:
                json_data = json.loads(data)
                args = json_data.get('args', None)
                if not args:
                    return False
                if args.get(self._random_key) == self._random_value:
                ## if self._proxy_ip in json_data.get('origin')  or \
                ##        self._proxy_ip in json_data.get('X-Real-Ip') or \
                ##        self._proxy_ip in json_data.get('X-Forwarded-For'):
                    return True
            except Exception, e:
                logger.warn("%r | %s " % (self, e))
                return False
            return False
        else:
            return False


class BaseChecker(object):
    """Base class for checkers
    """

    def __init__(self, proxy_addr, time_out=None,
                 user_agent=None, tester=None, opener_base_class=pycurl.Curl):
        """

        Arguments:
        - `proxy_addr`: (ip, port)
        - `time_out`: int
        - `user_agent`: str
        - `tester`: class
        """
        self._proxy_addr = proxy_addr
        self._time_out = time_out or DEFAULT_TIME_OUT
        self._user_agent = user_agent or choice(USER_AGENTS)
        self._proxy_type = None
        self._result = False
        self._opener = None
        self._output = None
        self._use_proxy_ssl = False
        self._tester = tester(self._proxy_addr) if tester \
                       else HWRTTNTester(self._proxy_addr)

        self._opener_base_class = opener_base_class

    def __repr__(self):
        return "<%s: %s:%s [ %s ] [ %s ]>" % (self.__class__.__name__,
                                              self._proxy_addr[0], self._proxy_addr[1],
                                              self._time_out, self._tester.url)

    def get_opener(self):
        """Construct curl opener
        """
        logger.debug("%r | start creating opener")
        opener = self._opener_base_class()
        output = StringIO.StringIO()
        opener.setopt(pycurl.URL, str(self._tester.url))
        opener.setopt(pycurl.WRITEFUNCTION, output.write)
        #opener.setopt(c.HEADERFUNCTION, self.write_headers)
        opener.setopt(pycurl.PROXY, str(self._proxy_addr[0]))
        opener.setopt(pycurl.PROXYPORT, self._proxy_addr[1])

        opener.setopt(pycurl.USERAGENT, choice(self._user_agent))
        if self._use_proxy_ssl:
            # CONNECT tunnel
            opener.setopt(pycurl.HTTPPROXYTUNNEL, 1)
        opener.setopt(pycurl.PROXYTYPE, self._proxy_type)
        opener.setopt(pycurl.FOLLOWLOCATION, 0)
        opener.setopt(pycurl.CONNECTTIMEOUT, self._time_out)
        opener.setopt(pycurl.TIMEOUT, self._time_out)
        opener.setopt(pycurl.NOSIGNAL, 1)

        self._opener = opener
        self._output = output

        logger.debug("%r | opener created" % self)

        opener.perform()

        return opener, output

    def test_result(self):
        """Search known tokens
        """
        if not self._opener and not self._output:
            self.get_opener()
        tester = self._tester
        self._result = tester.test(self._output.getvalue())
        return self._result

    def check(self):
        """Check proxy for type
        """
        try:
            self.get_opener()
            self.test_result()
            logger.debug("%r | output tested" % self)
            self._output.close()
            self._opener.close()
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception, e:
            logger.warn(" %r | %s" % (self, e))
            return False
        else:
            return self._result


class HttpChecker(BaseChecker):
    """Check http proxy
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super(HttpChecker, self).__init__(*args, **kwargs)
        self._proxy_type = pycurl.PROXYTYPE_HTTP


class HttpsChecker(BaseChecker):
    """Check http proxy
    """

    def __init__(self, *args, **kwargs):
        super(HttpsChecker, self).__init__(*args, **kwargs)
        self._proxy_type = pycurl.PROXYTYPE_HTTP
        self._use_proxy_ssl = True


class Socks4Checker(BaseChecker):
    """Check socks4 proxy
    """

    def __init__(self, *args, **kwargs):
        super(Socks4Checker, self).__init__(*args, **kwargs)
        self._proxy_type = pycurl.PROXYTYPE_SOCKS4


class Socks5Checker(BaseChecker):
    """Check socks5 proxy
    """

    def __init__(self, *args, **kwargs):
        super(Socks5Checker, self).__init__(*args, **kwargs)
        self._proxy_type = pycurl.PROXYTYPE_SOCKS5


class TypesCheckerBase(object):
    """Base class for parallel checker
    """

    def __init__(self, proxy_addr, time_out=None, user_agent=None, tester=None):
        """Class init

        Arguments:
        - `proxy_addr`: (ip, port) tuple
        - `time_out`:
        - `user_agent`:
        - `tester`:
        """
        self._proxy_addr = proxy_addr
        self._tester = tester
        self._time_out = time_out or DEFAULT_TIME_OUT
        self._user_agent = user_agent
        self._types = {
            'socks5': None,
            'socks4': None,
            'GET': None,
            'CONNECT': None}

    def __repr__(self):
        return u"<%s: %s>" % (self.__class__.__name__, self._proxy_addr)

    def get_types(self, is_list=False):
        """Return dictionary or list (if is_list=True) of supporting proxy types.
        - `is_list`: bool
        """
        raise ImplementationError


class SerialTypesChecker(TypesCheckerBase):
    """Check proxies with serial requests
    """
    def __init__(self, proxy_addr, time_out=None, user_agent=None,
                 tester=None, *args, **kwargs):
        super(SerialTypesChecker, self).__init__(proxy_addr, time_out, user_agent,
                                           tester, *args, **kwargs)

    def get_types(self, is_list=False):
        """Return dictionary or list (if is_list=True) of supporting proxy types.
        - `is_list`: bool
        """
        for proxy_type in self._types.keys():
            checker = get_checker(proxy_type)
            try:
                self._types[proxy_type] = checker(self._proxy_addr, time_out=self._time_out,
                                              user_agent=self._user_agent,
                                              tester=self._tester).check()
            except Exception, e:
                logger.warn("%r | %s" % (self, e))
                continue

        if is_list:
            return [k for k, v in self._types.items() if v is True]
        return dict([(k, v if v else False) for k, v  in self._types.items()])


class ThreadsTypesChecker(TypesCheckerBase):
    """Parallel check types by threading module
    """
    def __init__(self, proxy_addr, time_out=None, user_agent=None,
                 tester=None, *args, **kwargs):
        super(ThreadsTypesChecker, self).__init__(proxy_addr, time_out, user_agent,
                                           tester, *args, **kwargs)
        self._threads = []

    def get_types(self, is_list=False):
        """Return dictionary or list (if is_list=True) of supporting proxy types.
        - `is_list`: bool
        """
        for proxy_type in self._types.keys():
            try:
                t = TypesCheckerThread(self, self._proxy_addr, proxy_type,
                                       self._time_out, self._user_agent, self._tester)
                self._threads.append(t)
            except Exception, e:
                logger.warn("%r | %s" % (self, e))

        # start all threads
        for t in self._threads:
            t.start()

        # wait until threads done work
        for t in self._threads:
            t.join()

        if is_list:
            return [k for k, v in self._types.items() if v is True]
        return dict([(k, v if v else False) for k, v  in self._types.items()])


class TypesCheckerThread(threading.Thread):
    """Check proxy from types_queue fro given type
    """
    def __init__(self, parent, proxy_addr, proxy_type, time_out=None,
                 user_agent=None, tester=None, *args, **kwargs):
        """TypesCheclerThread init

        Arguments
        - `parent`:
        - `proxy_addr`:
        - `proxy_type`:
        - `time_out`:
        - `user_agent`:
        - `tester`:
        """
        super(TypesCheckerThread, self).__init__(*args,  **kwargs)
        self._parent = parent
        self._proxy_type = proxy_type
        self._proxy_addr = proxy_addr
        self._tester = tester
        self._time_out = time_out
        self._types_blocker = threading.Lock()

    def __repr__(self):
        return u"<%s: %s> " % (self.__class__.__name__, self._proxy_type)

    def run(self):
        """Starts when self.start() execute
        """
        checker = get_checker(self._proxy_type)
        try:
            self._types_blocker.acquire()
            self._parent._types[self._proxy_type] = checker(proxy_addr=self._proxy_addr,
                                                      time_out=self._time_out,
                                                      tester=self._tester).check()
        except Exception, e:
            logger.warn("%r | %s" % (self, e))
            traceback.print_exc(file=sys.stdout)
        finally:
            self._types_blocker.release()


class TypesCheckerProcessesManager(TypesCheckerBase):
    """Check proxies with multiprocessing
    """
    def __init__(self, input_queue, output_queue, time_out=None, user_agent=None,
                 tester=None,  poll_limit=4, *args, **kwargs):
        self._tester = tester
        self._time_out = time_out or DEFAULT_TIME_OUT
        self._user_agent = user_agent
        self._types = {
            'socks5': None,
            'socks4': None,
            'GET': None,
            'CONNECT': None}
        self._processes_poll = []
        self._poll_limit = poll_limit


    def check_all(self):
        """Return dictionary or list (if is_list=True) of supporting proxy types.
        - `is_list`: bool
        """
        for x in xrange(self._poll_limit):
            try:
                t = TypesCheckerProcess(self._input_queue, self._output_queue, self._time_out,
                                        self._user_agent, self._tester)
                self._processes_poll.append(t)
            except Exception, e:
                logger.warn("%r | %s" % (self, e))

        # start all threads
        for t in self._processes_poll:
            t.start()

        # wait until threads done work
        for t in self._processes_poll:
            t.join()


class TypesCheckerProcess(multiprocessing.Process):
    """Check proxy from types_queue for given type
    """
    def __init__(self, input_queue, output_queue, proxy_addr, time_out=None,
                 user_agent=None, tester=None, *args, **kwargs):
        """TypesCheclerThread init

        Arguments
        - `input_queue`:
        - `output_queue`:
        - `proxy_addr`:
        - `time_out`:
        - `user_agent`:
        - `tester`:
        """
        super(TypesCheckerProcess, self).__init__(*args,  **kwargs)
        self._tester = tester
        self._time_out = time_out
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._types = {
            'socks5': None,
            'socks4': None,
            'GET': None,
            'CONNECT': None}


    def __repr__(self):
        return u"<%s: > " % self.__class__.__name__

    def run(self):
        """Starts when self.start() execute
        """
        logger.debug("%r start work" % self)
        while True:
            proxy_addr = self._input_queue.get(True)

            if proxy_addr is 0:
                break

            for proxy_type in PROXY_TYPES:
                checker = get_checker(self._proxy_type)
                try:
                    self._types[proxy_type] = checker(proxy_addr=proxy_addr,
                                                      time_out=self._time_out,
                                                      tester=self._tester).check()
                except Exception, e:
                    print(e)
                    logger.warn("%r | %s" % (self, e))
                    traceback.print_exc(file=sys.stderr)
                    continue
            self._input_queue.task_done()
            self._output_queue.put(self._types)
        logger.debug("%r finished work" % self)


def get_checker(proxy_type):
    """Get handler for given proxy type

    Arguments:
    - `proxy_type`: string
    """
    if proxy_type in http:
        return HttpChecker
    elif proxy_type in https:
        return HttpsChecker
    elif proxy_type in socksver4:
        return Socks4Checker
    elif proxy_type in socksver5:
        return Socks5Checker
    else:
        raise RuntimeError("Unknown proxy type")
