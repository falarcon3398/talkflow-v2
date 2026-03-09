#!/usr/bin/env bash
set -euo pipefail
EXTERNAL_ROOT="${EXTERNAL_ROOT:-/Volumes/FREDDY FILES/ANTIGRAVITY/1001-VIDEO AVATAR/_external}"

echo "Using EXTERNAL_ROOT=$EXTERNAL_ROOT"
mkdir -p "$EXTERNAL_ROOT"/{models,outputs,caches,logs,avatars,hf_cache,torch_cache,pip_cache,npm_cache}

# Create a symlink to models if it doesn't exist
if [ ! -L "api_server/models" ] && [ ! -d "api_server/models" ]; then
    ln -s "$EXTERNAL_ROOT/models" "api_server/models"
fi

echo "Set these env vars in your shell or .env:"
echo "EXTERNAL_ROOT=$EXTERNAL_ROOT"
echo "HF_HOME=$EXTERNAL_ROOT/hf_cache"
echo "TRANSFORMERS_CACHE=$EXTERNAL_ROOT/hf_cache"
echo "TORCH_HOME=$EXTERNAL_ROOT/torch_cache"
echo "XDG_CACHE_HOME=$EXTERNAL_ROOT/caches"
echo "PIP_CACHE_DIR=$EXTERNAL_ROOT/pip_cache"
echo "npm_config_cache=$EXTERNAL_ROOT/npm_cache"
echo "Done."
