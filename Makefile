# Shortcuts for various tasks (UNIX only).
# To use a specific Python version run:
# $ make install PYTHON=python3.3

PYTHON=python

clean:
	rm -rf dict/
	rm -rf log/
	rm -rf *.pyc
	rm -rf __pycache__

setup:
	$(PYTHON) -m pip install -r --user --upgrade requirements.txt
