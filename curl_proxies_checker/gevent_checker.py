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
from logging import getLogger
from checker import (HttpChecker, Socks4Checker, Socks5Checker, HttpsChecker,
                      HWRTTNTester, HTTPBinTester, get_checker, TypesCheckerBase)

logger = getLogger("curl_proxies_checker")

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


class GeventPoolChecker(object):
    """Check many proxies in gevent.Pool
    """

    def __init__(self, proxies, pool_size=20, time_out = None, user_agent = None, tester = None):
        """GegentPoolChecker init

        Arguments:
        - `proxies`:
        - `time_out`:
        - `user_agent`:
        - `tester`:
        """
        self._proxies = proxies
        self._time_out = time_out
        self._user_agent = user_agent
        self._tester = tester
        self._pool = gevent.Pool(pool_size)

    def check(self):
        """Check proxies list
        """
        for proxy in self._proxies:
            pool.spawn(job, '%s.com' % x)
        pool.join()

