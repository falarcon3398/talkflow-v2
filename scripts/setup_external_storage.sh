#!/usr/bin/env bash
set -euo pipefail
EXTERNAL_ROOT="${EXTERNAL_ROOT:-/mnt/external/1001-video-avatar}"

echo "Using EXTERNAL_ROOT=$EXTERNAL_ROOT"
mkdir -p "$EXTERNAL_ROOT"/{models,outputs,caches,logs,avatars,hf_cache,torch_cache,pip_cache,npm_cache}

export HF_HOME="$EXTERNAL_ROOT/hf_cache"
export TRANSFORMERS_CACHE="$EXTERNAL_ROOT/hf_cache"
export TORCH_HOME="$EXTERNAL_ROOT/torch_cache"
export XDG_CACHE_HOME="$EXTERNAL_ROOT/caches"
export PIP_CACHE_DIR="$EXTERNAL_ROOT/pip_cache"
export npm_config_cache="$EXTERNAL_ROOT/npm_cache"

echo "Set these env vars in your shell or .env:"
echo "EXTERNAL_ROOT=$EXTERNAL_ROOT"
echo "HF_HOME=$HF_HOME"
echo "TRANSFORMERS_CACHE=$TRANSFORMERS_CACHE"
echo "TORCH_HOME=$TORCH_HOME"
echo "XDG_CACHE_HOME=$XDG_CACHE_HOME"
echo "PIP_CACHE_DIR=$PIP_CACHE_DIR"
echo "npm_config_cache=$npm_config_cache"
echo "Done."
