#!/bin/bash
# Store OpenAI API key in macOS Keychain (never written to disk)
# Usage: ./scripts/setup_keychain.sh YOUR_API_KEY

if [ -z "$1" ]; then
    echo "Usage: ./scripts/setup_keychain.sh sk-proj-YOUR_KEY"
    exit 1
fi

security add-generic-password -a "glassbox-ai" -s "OPENAI_API_KEY" -w "$1" -U
echo "✅ API key stored in macOS Keychain under service=OPENAI_API_KEY account=glassbox-ai"
