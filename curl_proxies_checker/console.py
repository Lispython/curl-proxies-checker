#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
curl_proxies_checker.console
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Console util for proxies checking

:copyright: (c) 2011 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
"""

import logging
import time
import os
import sys

from checker import SerialTypesChecker, get_version

logger = logging.getLogger('curl_proxies_checker')


def print_results(addresses, time_result):
    print("Checked %s proxies for %s at %s " % (len(addresses),
                                                    "%s sec" if time_result < 300 else "%s min" % time_result/60.0,
                                                    time.ctime()))


def main():
    t = time.time()
    print("Proxies checker v%s start at %s" % (get_version(), time.ctime(t)))

    print("Use %s as types checker" % SerialTypesChecker.__name__)

    from optparse import OptionParser
    usage = "%prog [options] ip:port ip:port ..."

    parser = OptionParser(usage)

    parser.add_option("-f", "--file", dest="filename",
                      help="proxies file", metavar="FILE")
    parser.add_option("-t", "--timeout", dest="timeout",
                      help="connection timeout", type="int", metavar="TIMEOUT",
                      default=20)
    parser.add_option("-l", "--logging", dest="logging", action="store_true", default=False)

    (options, args) = parser.parse_args()

    if options.logging:
        logger = logging.getLogger("curl_proxies_checker")

        logger.setLevel(logging.DEBUG)

        # Add the log message handler to the logger
        # LOG_FILENAME = os.path.join(os.path.dirname(__file__), "debug.log")
        # handler = logging.handlers.FileHandler(LOG_FILENAME)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s %(asctime)s %(module)s [%(lineno)d] %(process)d %(thread)d | %(message)s ")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    addresses = []
    if args > 0:
        for arg in args[:]:
            try:
                ip, port = [x.strip() for x in arg.split(":")]
                addresses.append((ip, int(port)))
            except Exception, e:
                print(e)
                continue

    if options.filename and os.path.exists(options.filename):
        for line in open(options.filename):
            if line == "\n":
                continue
            try:
                ip, port = [x.strip() for x in line.split(":")]
                addresses.append((ip, int(port)))
            except Exception, e:
                print(e)
                continue


    for proxy in addresses:
        try:
            proxy_result = SerialTypesChecker(proxy, options.timeout).get_types(True)
            print("%s:%s ---> %s" % (proxy[0], proxy[1], proxy_result))
        except KeyboardInterrupt:
            print_results()
            print("Checked %s proxies for %s sec at %s " % (len(addresses),
                                                            (time.time()-t) * 10,
                                                            time.ctime()))
            sys.exit(1)


    print("Checked %s proxies for %s sec at %s " % (len(addresses),
                                                    (time.time()-t) * 10,
                                                    time.ctime()))
    sys.exit(1)




if __name__ == "__main__":
    main()
