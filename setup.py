# -*- coding:  utf-8 -*-

"""
curl_proxies_checker.setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

Lib setup

:copyright: (c) 2011 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
"""


import sys
import os
try:
    import subprocess
    has_subprocess = True
except:
    has_subprocess = False

from setuptools import Command, setup

__version__ = (0, 0, 6)


try:
    readme_content = open(sys.path.join(sys.apth.abspath(sys.path.dirname(__file__)), "README.md")).read()
except Exception, e:
    readme_content = __doc__



class run_audit(Command):
    """Audits source code using PyFlakes for following issues:
        - Names which are used but not defined or used before they are defined.
        - Names which are redefined without having been used.
    """
    description = "Audit source code with PyFlakes"
    user_options = []

    def initialize_options(self):
        all = None

    def finalize_options(self):
        pass

    def run(self):
        try:
            import pyflakes.scripts.pyflakes as flakes
        except ImportError:
            print "Audit requires PyFlakes installed in your system."""
            sys.exit(-1)

        dirs = ['curl_proxies_checker']
        # Add example directories
        for dir in []:
            dirs.append(os.path.join('examples', dir))
        # TODO: Add test subdirectories
        warns = 0
        for dir in dirs:
            for filename in os.listdir(dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    warns += flakes.checkPath(os.path.join(dir, filename))
        if warns > 0:
            print ("Audit finished with total %d warnings." % warns)
        else:
            print ("No problems found in sourcecode.")


def run_tests():
    from runtests import suite
    return suite()


setup(
    name="curl_proxies_checker",
    version=".".join(map(str, __version__)),
    description="Lib for check proxies",
    long_description=readme_content,
    author="Alex",
    author_email="alex@obout.ru",
    url="https://github.com/lispython/curl-proxies-checker",
    packages=["curl_proxies_checker"],
    install_requires=[
        'pycurl'
        ],
    license="BSD",
    entry_points=dict(
        console_scripts=['proxies_checker=curl_proxies_checker.console:main']
        ),
    #test_suite="nose.collector",
    classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python"
        ],
    cmdclass={'audit': run_audit},
    test_suite = '__main__.run_tests'
    )
