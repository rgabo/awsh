NAME=awsh

build:
	docker build -t $(NAME) .

dev: build
	docker run -it --cap-add mknod --cap-add sys_admin --device=/dev/fuse --env-file=.env $(NAME)

check:
	###### FLAKE8 #####
	flake8 awsh/*.py
	##### DOC8 ######
	doc8 awsh/*.py
	# Proper docstring conventions according to pep257
	pep257 --add-ignore=D100,D101,D102,D103,D104,D105,D204
	###### PYLINT (errors only) ######
	pylint --rcfile .pylintrc -E awsh

coverage:
	py.test --cov awsh --cov-report term-missing tests/

pylint:
	###### PYLINT ######
	pylint --rcfile .pylintrc awsh

