#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
curl_proxies_checker.gevent_checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check proxies by parallel greenlets

:copyright: (c) 2011 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
"""

from gevent import monkey; monkey.patch_all()
import sys
import traceback
import gevent
from gevent.pool import Pool
from logging import getLogger
from checker import (HttpChecker, Socks4Checker, Socks5Checker, HttpsChecker,
                      HWRTTNTester, HTTPBinTester, get_checker, TypesCheckerBase)

logger = getLogger("curl_proxies_checker")

def check_type(proxy_type, proxy_addr, timeout, tester):
    try:
        checker = get_checker(proxy_type)
        result = checker(proxy_addr=proxy_addr, time_out=timeout,
                         tester=tester).check()
        return result
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception, e:
        print(e)
        logger.warn("Unknown error [ %s ]" % e)
        traceback.print_exc(file=sys.stdout)
        return False


class GeventCheckerManager(object):
    """
    """
    def __init__(self, proxies, time_out=None, tester=None, pool_limit=100):
        self._proxies = proxies
        self._pool_limit = pool_limit if pool_limit < len(proxies) else len(proxies)
        self._result_queue = gevent.queue.Queue(len(proxies)/2)
        self._input_queue = gevent.queue.Queue(len(proxies)/2)
        self._checkers_pool = []
        self._time_out = timeout
        self._tester = tester


    def check(self):
        for x in xrange(self._pool_limit):
            c = CheckerGreenlet(self._input_queue, self._result_queue,
                                                       self._time_out, self._tester)
            c.start()
            self._checkers_pool.append(c)

        for proxy_addr in self._proxies:
            for proxy_type in ('socks5', 'socks4', 'GET', 'CONNECT'):
                self._input_queue.put((proxy_addr, proxy_type))

        self._input_queue.join()
        self._output_queue.join()


class CheckerGreenlet(gevent.Greenlet):
    def __init__(self, input_queue, output_queue, time_out=None, tester=None):
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._time_out = time_out
        self._tester = tester
        self._finished = False

    def _run(self):
        while not self._finished:
            try:
                proxy_addr, proxy_type = self._input_queue.get()
            except Exception, e:
                continue

            try:
                result = check_type(proxy_type, proxy_addr, self._time_out, self._tester)
            except Exception, e:
                result = False

            self._output_queue.put((proxy_addr, proxy_type, result))
            gevent.sleep(0.8)


    def stop(self):
        self._finished = True




class GeventChecker(TypesCheckerBase):
    """Parallel check proxies with gevent library
    """

    def __init__(self, proxy_addr, time_out=None, tester=None):
        """Class init

        Arguments:
        - `proxy_addr`: (ip, port) tuple
        - `time_out`:
        - ``
        """
        super(GeventChecker, self).__init__(proxy_addr, time_out, tester)

    def get_types(self, is_list=False):
        """Return dict of proxy types.

        - `is_list`: if True return types list
        """

        def check_type(proxy_type, proxy_addr):
            try:
                checker = get_checker(proxy_type)
                result = checker(proxy_addr=proxy_addr, time_out=self._time_out,
                                 tester=self._tester).check()
                return (proxy_type, result)
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception, e:
                print(e)
                logger.warn("Unknown error [ %s ]" % e)
                traceback.print_exc(file=sys.stdout)
                return (proxy_type, False)

        try:
            types = [gevent.spawn(check_type, t, self._proxy_addr)
                     for t in self._types.keys()]
            logger.debug("Wait until types joining")
            print("Wait until types joining")
            gevent.joinall(types)
            logger.debug(" [ %s ]" % [x.value for x in types])
            self._types = dict((x.value for x in types))
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            logger.warn("Unknown error [ %s ]" % e)

        if is_list:
            return [k for k, v in self._types.items() if v is True]
        return dict([(k, v if v else False) for k, v  in self._types.items()])

