#!/bin/bash
# Reads OPENAI_API_KEY from macOS Keychain, runs MCP server with hot-reload (mcp-hmr)
export OPENAI_API_KEY=$(security find-generic-password -s "OPENAI_API_KEY" -a "glassbox-ai" -w)
exec /Users/sourabh/opt/anaconda3/envs/glassbox_312/bin/mcp-hmr /Users/sourabh/Documents/projects/glassbox-ai/src/glassbox/server.py:mcp
