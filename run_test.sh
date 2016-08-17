#!/usr/bin/env bash

set -e  # 若指令传回值不等于 0，则立即退出 shell

export PATH="$HOME/miniconda/bin:$PATH"
export PYTHONPATH="$DIR/..:$PYTHONPATH"
export CERES_APP_CONFIG="ceres.config.test_config"

# Activate Python environment

source activate ceres

py.test -s

[ -e db/test.db ] && rm db/test.db
