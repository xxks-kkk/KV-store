# Shortcuts for various tasks (UNIX only).
# To use a specific Python version run:
# $ make install PYTHON=python3.3

PYTHON=python

# suppress the core dump error raised from installing server_identity package
define EXPECTED_FAIL
if ! { $1 ; } 2>$@.temp; then \
    echo EXPECTED FAILURE: ; cat $@.temp; \
fi
endef


clean:
	rm -rf dict/
	rm -rf log/
	rm -rf *.pyc
	rm -rf __pycache__
	rm -rf server_log

install:
	$(call EXPECTED_FAIL, $(PYTHON) -m pip install -r requirements.txt)
	mkdir server_log
	@echo "Generating large test cases ..."
	$(PYTHON) commandGen.py

# Change the configuration to the single machine test scenario
single:
	@patch < single.patch

# Change the configuration to the multiple machines test scenario
multiple:
	@patch < multiple.patch
