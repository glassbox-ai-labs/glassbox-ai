# GlassBox Agent — GitHub App

## What This Is

A GitHub App that gives the GlassBox Agent a real bot identity on GitHub:
- **`@glassbox-agent`** auto-suggests in issue comments
- Comments appear as **"glassbox-agent [bot]"** with its own avatar
- Scoped permissions (only what the agent needs, not broad org access)

## Architecture

```
┌─────────────────────────────────────────────────┐
│  GitHub Issue                                    │
│  User comments: "@glassbox-agent fix this"       │
└──────────────────────┬──────────────────────────┘
                       │ issue_comment event
                       ▼
┌─────────────────────────────────────────────────┐
│  GitHub Actions (agent-fix.yml)                  │
│                                                  │
│  1. Generate installation token from APP_ID +    │
│     APP_PRIVATE_KEY (repo secrets)               │
│  2. Checkout latest code from main               │
│  3. Run: python -m scripts.agent.main <issue#>   │
│  4. Agent posts comments using app token         │
│     → shows as "glassbox-agent [bot]"            │
└─────────────────────────────────────────────────┘
```

**Auto-sync:** The app is just credentials. The agent logic lives in `scripts/agent/`.
When we improve the engine, the next trigger automatically runs the latest code.
No manual app updates needed.

## Files

| File | Purpose |
|------|---------|
| `manifest.json` | App definition: name, permissions, events, description |
| `setup.py` | One-time setup: create app via manifest flow, store secrets |
| `.gitignore` | Prevents committing private keys (*.pem) |
| `README.md` | This file |

## One-Time Setup

### Prerequisites
- `gh` CLI authenticated with org admin access
- Port 3456 available on localhost

### Steps

```bash
# 1. Run the setup script
python github-app/setup.py

# 2. Click "Create GitHub App" in the browser
#    → Script handles the rest (secrets, credentials)

# 3. Install the app on the repo
#    → Link printed by the script

# 4. Clean up
rm github-app/glassbox-agent.pem   # already stored as secret
```

### What the setup script does
1. Reads `manifest.json` for app definition
2. Opens browser → auto-submits manifest to GitHub
3. You click "Create GitHub App"
4. GitHub redirects back with a code
5. Script exchanges code for credentials (App ID + private key)
6. Stores `APP_ID` and `APP_PRIVATE_KEY` as repo secrets via `gh secret set`
7. Prints the installation URL

### After setup
- The workflow (`agent-fix.yml`) generates a fresh installation token on every run
- All GitHub API calls use this token → comments appear as the bot
- The app never needs updating unless permissions change

## Updating Permissions

If the agent needs new GitHub permissions later:

1. Edit `manifest.json` with the new permissions
2. Go to https://github.com/organizations/agentic-trust-labs/settings/apps
3. Edit the app settings manually to match

Or delete the app and re-run `setup.py` (secrets will be overwritten).

## Security

- **Private key** is stored ONLY as a GitHub repo secret (`APP_PRIVATE_KEY`)
- **`.gitignore`** prevents accidental commits of `*.pem` files
- **Installation tokens** expire after 1 hour (generated fresh each workflow run)
- **Scoped permissions**: only `issues:write`, `pull_requests:write`, `contents:write`, `metadata:read`
