#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# Need to replace the absolute path with a relative path
source ${METRICS_POETRY_INTERPRETER}/bin/activate # Activate the virtual environment
python ${DIR}/src/cli/entry.py "$@"  # Run your Python script
deactivate  # Deactivate the virtual environment
