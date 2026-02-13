#!/bin/bash
# Reads OPENAI_API_KEY from macOS Keychain, then runs the Docker container
export OPENAI_API_KEY=$(security find-generic-password -s "OPENAI_API_KEY" -a "glassbox-ai" -w)
exec docker run --rm -i --platform linux/amd64 -e OPENAI_API_KEY ghcr.io/glassbox-ai-labs/glassbox-ai:latest
