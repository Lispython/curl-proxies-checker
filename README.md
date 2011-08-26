# cURL proxies checker


## USAGE


    >>> proxy = ("189.22.186.37", 8080)
    >>> checker = HttpChecker(proxy)
    >>> print(checker.check())
    ... True


## COMMAND LINE USAGE

Install curl_proxies_checker and gevent library


    $ python curl_proxies_checker/checker.py --help
    Proxies checker start at Fri Aug 26 20:21:17 2011
    Use GeventChecker as types checker
    Usage: checker.py [options] ip:port ip:port ...

    Options:
      -h, --help            show this help message and exit
      -f FILE, --file=FILE  proxies file
      -t TIMEOUT, --timeout=TIMEOUT
                            connection timeout

    $ python curl_proxies_checker/checker.py -f proxies_list.txt -t 10

    Proxies checker start at Fri Aug 26 20:21:32 2011
    Use GeventChecker as types checker
    112.233.158.131:8909 ---> []
    203.148.84.178:8080 ---> []
    208.52.90.22:80 ---> []
    116.21.216.156:8909 ---> []
    187.11.229.55:80 ---> []
    202.95.137.5:80 ---> ['GET']
    189.22.186.37:8080 ---> ['GET']
    121.52.155.52:8080 ---> ['GET']
    64.71.138.122:80 ---> []
    ^[[A80.65.109.179:8080 ---> []
    112.233.158.131:8909 ---> []
    116.21.216.156:8909 ---> []
    94.232.65.104:3128 ---> ['GET']
    70.183.199.202:8085 ---> []
    113.227.142.78:8909 ---> []
    203.148.84.178:8080 ---> []
    187.11.229.55:80 ---> ['CONNECT', 'GET']
    173.31.247.160:1174 ---> []
    68.36.0.116:54755 ---> []
    24.0.68.158:1355 ---> []
    76.30.47.78:1097 ---> []
    76.108.68.185:1096 ---> []
    74.111.230.217:1611 ---> []
    98.228.48.194:47191 ---> []
    108.6.58.122:1465 ---> []
    96.255.209.211:1638 ---> []
    24.247.106.78:6877 ---> []
    81.195.98.78:808 ---> []
    83.172.27.133:80 ---> []
    84.204.215.91:3128 ---> []
    82.199.113.2:3128 ---> []
    85.172.119.24:54321 ---> []
    82.193.150.168:3128 ---> []
    83.246.226.42:8080 ---> []
    62.76.46.181:8088 ---> ['CONNECT', 'GET']
    62.148.136.79:80 ---> ['GET']
    83.246.229.11:8080 ---> []
    82.196.84.50:3128 ---> []
    ^[[A83.222.92.253:666 ---> []
    83.142.160.103:3128 ---> []
    Checked 36 proxies for 17552.858541 sec at Fri Aug 26 20:50:47 2011


## INSTALLATION

To use curl_proxies_checker use pip or easy_install:

`pip install curl_proxies_checker`

or

`easy_install curl_proxies_checker`


## TODO

- check connection time
- check X-Real-Ip and X-Forwarded-For for real client ip
