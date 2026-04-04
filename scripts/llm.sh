export NGC_API_KEY=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
export LOCAL_NIM_CACHE="$HOME/.cache/nim"
mkdir -p "$LOCAL_NIM_CACHE"
echo "$NGC_API_KEY" | docker login nvcr.io \
    --username '$oauthtoken' \
    --password-stdin
docker run -it --rm \
    --shm-size=16GB \
    -e NGC_API_KEY \
    -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
    -u $(id -u) \
    -p 8050:8000 \
    nvcr.io/nim/nvidia/nvidia-nemotron-nano-9b-v2:latest
