# -*- coding:  utf-8 -*-
"""
curl_proxies_checker.tests
~~~~~~~~~~~~~~~~~~~~~~~~~~

Unittests for curl_proxies_checker classes

:copyright: (c) 2011 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
"""

import time
import pycurl
import unittest
from cStringIO import StringIO
import os.path
from curl_proxies_checker import (BaseChecker, HttpChecker, HttpsChecker,
                                  Socks4Checker, Socks5Checker, BaseTester,
                                  HWRTTNTester, HTTPBinTester, ImplementationError,
                                  USER_AGENTS, get_checker)

TEST_PROXIES = (
    ('HttpChecker', HttpChecker, ('62.76.46.181', 8088)),
    ## ('HttpChecker', HttpChecker, ('189.22.186.37', 8080)),
    ('HttpsChecker', HttpsChecker, ('62.76.46.181', 8088)),
    ('Socks4Checker', Socks4Checker, ('109.69.1.254', 8741)),
    ('Socks5Checker', Socks5Checker, ('67.82.45.157', 1291))
    )


PRIVOXY_HTTP = ("127.0.0.1", 8118)
PRIVOXY_SOCKS = ("127.0.0.1", 9050)

class TestersTestCase(unittest.TestCase):
    def test_base(self):
        tester = BaseTester(TEST_PROXIES[0][2])
        self.assertEquals(tester.url, None)
        self.assertRaises(ImplementationError, tester.test, "fwefe")
        self.assertEquals(tester._proxy_ip, TEST_PROXIES[0][2][0])
        self.assertEquals(tester._proxy_port, TEST_PROXIES[0][2][1])


    def test_hwrttntester(self):
        tester = HWRTTNTester(TEST_PROXIES[0][2])
        self.assertEquals(tester.url, "http://h.wrttn.me/get?%s=%s" % (tester._random_key, tester._random_value))
        self.assertEquals(tester._proxy_ip, TEST_PROXIES[0][2][0])
        self.assertEquals(tester._proxy_port, TEST_PROXIES[0][2][1])
        opener = pycurl.Curl()
        output = StringIO()
        opener.setopt(pycurl.URL, str(tester.url))
        opener.setopt(pycurl.WRITEFUNCTION, output.write)
        opener.setopt(pycurl.PROXY, str(TEST_PROXIES[0][2][0]))
        opener.setopt(pycurl.PROXYPORT, TEST_PROXIES[0][2][1])
        opener.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
        opener.setopt(pycurl.CONNECTTIMEOUT, 15)
        opener.setopt(pycurl.TIMEOUT, 15)
        opener.perform()
        opener.close()
        o = output.getvalue()
        self.assertTrue(tester.test(o))

    def test_httpbintester(self):
        tester = HTTPBinTester(TEST_PROXIES[0][2])
        self.assertEquals(tester.url, "http://httpbin.org/get?%s=%s" % (tester._random_key, tester._random_value))
        self.assertEquals(tester._proxy_ip, TEST_PROXIES[0][2][0])
        self.assertEquals(tester._proxy_port, TEST_PROXIES[0][2][1])
        opener = pycurl.Curl()
        output = StringIO()
        opener.setopt(pycurl.URL, str(tester.url))
        opener.setopt(pycurl.WRITEFUNCTION, output.write)
        opener.setopt(pycurl.PROXY, str(TEST_PROXIES[0][2][0]))
        opener.setopt(pycurl.PROXYPORT, TEST_PROXIES[0][2][1])
        opener.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
        opener.setopt(pycurl.CONNECTTIMEOUT, 15)
        opener.setopt(pycurl.TIMEOUT, 15)
        opener.perform()
        opener.close()
        o = output.getvalue()
        self.assertTrue(tester.test(o))


class CheckersTestCase(unittest.TestCase):
    def setUp(self):
        self.tester = HWRTTNTester
        self.timeout = 15
        self.user_agent = USER_AGENTS[1]
        self.checkers = {
            'HttpChecker': HttpChecker,
            'HttpsChecker': HttpsChecker,
            'Socks4Checker': Socks4Checker,
            'Socks5Checker': Socks5Checker
            }

    def teadDown(self):
        pass

    def test_creating(self):
        for name, checker, proxy_addr in TEST_PROXIES:
            tester = self.tester(proxy_addr)
            checker_inst = checker(proxy_addr, self.timeout, self.user_agent, tester)
            self.assertEqual(repr(checker_inst), "<%s: %s:%s [ %s ] [ %s ]>"%
                             (name, proxy_addr[0], proxy_addr[1],
                              self.timeout, tester(proxy_addr).url))

            self.assertEquals(checker_inst._proxy_addr, proxy_addr)
            self.assertEquals(checker_inst._time_out, self.timeout)
            self.assertEquals(checker_inst._user_agent, self.user_agent)
            self.assertEquals(checker_inst._result, False)
            self.assertEquals(checker_inst._tester, tester(proxy_addr))
            check_result = checker_inst.check()
            if not check_result:
                print("Check error", proxy_addr, name, checker)
            self.assertTrue(check_result)


    def test_get_checker(self):
        checkers = {
            HttpChecker: ['http', 'GET'],
            HttpsChecker: ['https', 'CONNECT'],
            Socks4Checker: [4, 'socks4', 'socksver4', 'SOCKS4'],
            Socks5Checker: [5, 'socks5', 'socksver5', 'SOCKS5']
            }
        for checker, types in checkers.items():
            for proxy_type in types:
                self.assertEquals(get_checker(proxy_type), checker)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestersTestCase))
    suite.addTest(unittest.makeSuite(CheckersTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest = "suite")
