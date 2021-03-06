all: clean-pyc test

test:
	. ../venv/bin/activate
	python setup.py nosetests --stop --tests tests.py


coverage:
	. ../venv/bin/activate
	python setup.py nosetests  --with-coverage --cover-package=curl_proxies_checker --cover-html --cover-html-dir=coverage_out coverage


shell:
	../venv/bin/ipython

audit:
	. ../venv/bin/activate
	python setup.py autdit

release:
	. ../venv/bin/activate
	python setup.py sdist upload

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

find-print:
	grep -r --include=*.py --exclude-dir=venv --exclude=fabfile* --exclude=tests.py --exclude-dir=tests --exclude-dir=commands 'print' ./