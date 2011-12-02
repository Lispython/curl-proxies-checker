#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
curl_proxies_checker.tests
~~~~~~~~~~~~~~~~~~~~~~~~~~

Unittests for curl_proxies_checker

:copyright: (c) 2011 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement

import os
import time
import pycurl
import cookielib
from Cookie import Morsel
import json
import uuid
from random import randint
import logging
from urlparse import urljoin
import unittest

from curl_proxies_checker.checker import SerialTypesChecker, TypesCheckerBase, PROXIES_TYPES_MAP, get_checker
from curl_proxies_checker.geventcurl import Curl as GeventCurl

logger = logging.getLogger("curl_proxies_checker")

class CheckerTestCase(unittest.TestCase):

    def setUp(self):
        self.proxies = []
        with open("./proxies_list.txt") as f:
            for line in f:
                if line == "\n": continue
                try:
                    ip, port = line.split(":")
                    self.proxies.append((ip, int(port)))
                except Exception, e:
                    pass

    def test_build_url(self):
        self.assertEquals(1, 1)

    def test_types_checker_base(self):
        checker = TypesCheckerBase(self.proxies[0])

    def test_serial_types_checker(self):
        checker = SerialTypesChecker(self.proxies[0])
        self.assertEquals(len(checker.get_types()), 4)

    def test_checker_opener(self):
        for proxy_type in PROXIES_TYPES_MAP.keys():
            checker = get_checker(proxy_type)
            checker_instance = checker(self.proxies[0], opener_base_class=GeventCurl)
            self.assertEquals(checker_instance._opener_base_class, GeventCurl)

            try:
                opener, output = checker_instance.get_opener()
            except Exception, e:
                logger.debug(e)

            self.assertTrue(isinstance(checker_instance._opener, GeventCurl))
            self.assertTrue(isinstance(checker_instance._opener, GeventCurl))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CheckerTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")
