test:
	tox

clean:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete

distclean: clean
	rm -rf *.egg
	rm -rf *.egg-info

maintainer-clean: distclean
	rm -rf build
	rm -rf dist
	rm -rf .tox
