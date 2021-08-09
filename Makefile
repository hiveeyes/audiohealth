# ============
# Main targets
# ============


# -------------
# Configuration
# -------------

$(eval venvpath     := .venv)
$(eval pip          := $(venvpath)/bin/pip)
$(eval python       := $(venvpath)/bin/python)


# -----
# Setup
# -----

# Setup Python virtualenv
setup-virtualenv:
	@test -e $(python) || python3 -m venv --system-site-packages $(venvpath)
	$(pip) install --editable=.


# Build OSBH Audio Analyzer
setup-osbh-audio-analyzer:
	cd tools/osbh-audioanalyzer; ./build.sh
