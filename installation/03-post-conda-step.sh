#!/bin/bash

## run post-conda steps
BASEDIR="$(dirname "$0")"

ENV="terra_sync"

echo BASEDIR="$BASEDIR"
echo RUNNING post-conda steps

# shellcheck source=/dev/null
set +e \
  && PS1='$$$ ' \
  && . "$(conda info --base)"/etc/profile.d/conda.sh \
  && conda activate "${ENV}"

set -euo pipefail

conda info 
conda list
