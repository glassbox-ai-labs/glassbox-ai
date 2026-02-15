# GlassBox Agent — GitHub Identity

## Architecture

Two-layer setup (industry standard — same pattern used by Claude, Renovate, Codecov):

| Layer | What | Why |
|-------|------|-----|
| **GitHub App** (`glassbox-agent`) | Distributable app with scoped permissions, webhook events | For marketplace, installation on other repos, fine-grained auth |
| **Machine User** (`glassbox-agent`) | Regular GitHub account, member of `agentic-trust-labs` | Enables `@glassbox-agent` autocomplete in comments |

### Why two layers?

GitHub Apps **cannot** appear in `@mention` autocomplete (platform limitation, confirmed since 2023).
Every bot with working autocomplete uses a machine user: `@claude` (User), `@renovate-bot` (User), `@codecov-commenter` (User).

```
┌─────────────────────────────────────────────────┐
│  GitHub Issue                                    │
│  User types: "@glass" → autocomplete suggests    │
│  "@glassbox-agent" → user selects it             │
└──────────────────────┬──────────────────────────┘
                       │ issue_comment event
                       ▼
┌─────────────────────────────────────────────────┐
│  GitHub Actions (agent-fix.yml)                  │
│                                                  │
│  1. Checkout code using BOT_PAT                  │
│  2. Run: python -m scripts.agent.main <issue#>   │
│  3. Agent posts comments using BOT_PAT           │
│     → shows as "glassbox-agent"                  │
└─────────────────────────────────────────────────┘
```

## Current Setup

### Repo Secrets

| Secret | Source | Purpose |
|--------|--------|---------|
| `BOT_PAT` | Machine user PAT | All GitHub API calls (comments, PRs, pushes) |
| `APP_ID` | GitHub App | Available for future webhook/marketplace use |
| `APP_PRIVATE_KEY` | GitHub App | Available for future webhook/marketplace use |

### Machine User Profile

| Field | Value |
|-------|-------|
| **Username** | `glassbox-agent` |
| **Display name** | `GlassBox Agent` |
| **Company** | `@agentic-trust-labs` |
| **Bio** | Autonomous bug fixer with 6-message transparency protocol |
| **Org membership** | Member of `agentic-trust-labs` with push access |

## Files

| File | Purpose |
|------|---------|
| `manifest.json` | GitHub App definition: name, permissions, events |
| `setup.py` | One-time setup: create app via manifest flow, store secrets |
| `.gitignore` | Prevents committing private keys (*.pem) |
| `README.md` | This file |

## Setup (Already Done)

### GitHub App (for distribution/webhooks)
1. `python github-app/setup.py` → creates app via manifest flow
2. Script stores `APP_ID` and `APP_PRIVATE_KEY` as repo secrets
3. Install app on repo via the printed URL

### Machine User (for @mention autocomplete)
1. Create GitHub account `glassbox-agent` with `+alias` email
2. Invite to org: `gh api -X PUT /orgs/agentic-trust-labs/memberships/glassbox-agent -f role=member`
3. Accept invite using machine user's PAT
4. Add as repo collaborator: `gh api -X PUT /repos/agentic-trust-labs/glassbox-ai/collaborators/glassbox-agent -f permission=push`
5. Store PAT: `gh secret set BOT_PAT --repo agentic-trust-labs/glassbox-ai`
6. Post one comment to seed autocomplete

## Security

- **BOT_PAT** stored as GitHub repo secret only, never in code
- **`.gitignore`** prevents accidental commits of `*.pem` files
- **Machine user** has push (not admin) access — minimum required
- **GitHub App** has scoped permissions: `issues:write`, `pull_requests:write`, `contents:write`, `metadata:read`
