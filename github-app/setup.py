#!/usr/bin/env python3
"""GlassBox Agent GitHub App — one-time setup.

Creates the GitHub App from manifest.json, stores credentials as repo secrets,
and provides the installation URL.

Usage:
    python github-app/setup.py

Prerequisites:
    - gh CLI authenticated with org admin access
    - Port 3456 available on localhost

What it does:
    1. Reads manifest.json from this directory
    2. Opens browser → you click "Create GitHub App" on GitHub
    3. GitHub redirects back with a code
    4. Script exchanges code for app credentials (ID + private key)
    5. Stores APP_ID and APP_PRIVATE_KEY as repo secrets via gh CLI
    6. Prints the installation URL (you install on the repo manually)

After setup:
    - Delete the .pem file (it's already in GitHub Secrets)
    - The workflow uses these secrets to authenticate as the bot
    - Never run this script again unless recreating the app
"""

import json
import http.server
import os
import subprocess
import sys
import urllib.parse
import webbrowser

# -- Constants (from manifest.json) --

_DIR = os.path.dirname(os.path.abspath(__file__))
_MANIFEST_PATH = os.path.join(_DIR, "manifest.json")
_ORG = "agentic-trust-labs"
_REPO = "agentic-trust-labs/glassbox-ai"
_PORT = 3456


def _load_manifest() -> dict:
    """Load and validate manifest.json."""
    if not os.path.exists(_MANIFEST_PATH):
        print(f"ERROR: {_MANIFEST_PATH} not found")
        sys.exit(1)
    with open(_MANIFEST_PATH) as f:
        manifest = json.load(f)
    # Inject redirect_url (must point to our local callback)
    manifest["redirect_url"] = f"http://localhost:{_PORT}/callback"
    return manifest


def _set_secret(name: str, value: str) -> bool:
    """Set a GitHub repo secret via gh CLI. Returns True on success."""
    proc = subprocess.run(
        ["gh", "secret", "set", name, "--repo", _REPO, "--body", value],
        capture_output=True, text=True,
    )
    if proc.returncode == 0:
        print(f"  ✅ Secret '{name}' set on {_REPO}")
        return True
    print(f"  ❌ Secret '{name}' failed: {proc.stderr.strip()}")
    return False


def _convert_manifest_code(code: str) -> dict | None:
    """Exchange manifest code for app credentials via GitHub API."""
    result = subprocess.run(
        ["gh", "api", f"/app-manifests/{code}/conversions", "-X", "POST"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: API call failed: {result.stderr}")
        return None
    return json.loads(result.stdout)


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for the manifest flow: serves form + handles callback."""

    app_data = None  # Set on successful callback
    _manifest_json = ""  # Set before server starts

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/":
            self._serve_form()
        elif parsed.path == "/callback":
            self._handle_callback(parsed.query)
        else:
            self._respond(404, "<h1>Not found</h1>")

    def _serve_form(self):
        """Auto-submitting form that posts manifest to GitHub."""
        # Escape for HTML attribute (single quotes in JSON)
        escaped = self._manifest_json.replace("'", "&#39;")
        html = f"""<!DOCTYPE html>
<html><body>
<p>Redirecting to GitHub to create the GlassBox Agent app...</p>
<form id="f" method="post"
      action="https://github.com/organizations/{_ORG}/settings/apps/new">
  <input type="hidden" name="manifest" value='{escaped}'>
</form>
<script>document.getElementById("f").submit();</script>
</body></html>"""
        self._respond(200, html)

    def _handle_callback(self, query: str):
        """Exchange the code from GitHub for app credentials."""
        params = urllib.parse.parse_qs(query)
        code = params.get("code", [None])[0]

        if not code:
            self._respond(400, "<h1>Error: no code received from GitHub</h1>")
            return

        print("\n  Exchanging code for app credentials...")
        data = _convert_manifest_code(code)

        if not data:
            self._respond(500, "<h1>Failed to create app. Check terminal output.</h1>")
            return

        _CallbackHandler.app_data = data
        app_id = data["id"]
        app_name = data["name"]
        app_slug = data.get("slug", app_name)

        # Save PEM temporarily (will be stored as secret)
        pem = data["pem"]
        pem_path = os.path.join(_DIR, f"{app_slug}.pem")
        with open(pem_path, "w") as f:
            f.write(pem)

        print(f"\n  App created successfully!")
        print(f"  Name:     {app_name}")
        print(f"  ID:       {app_id}")
        print(f"  Slug:     {app_slug}")
        print(f"  PEM:      {pem_path}")

        # Store as repo secrets
        print(f"\n  Setting repo secrets on {_REPO}...")
        s1 = _set_secret("APP_ID", str(app_id))
        s2 = _set_secret("APP_PRIVATE_KEY", pem)

        status = "All secrets set!" if (s1 and s2) else "Some secrets failed — check output above."

        self._respond(200, f"""<!DOCTYPE html>
<html><body>
<h1>GlassBox Agent app created!</h1>
<table>
  <tr><td><b>Name:</b></td><td>{app_name}</td></tr>
  <tr><td><b>ID:</b></td><td>{app_id}</td></tr>
  <tr><td><b>Slug:</b></td><td>{app_slug}</td></tr>
  <tr><td><b>Secrets:</b></td><td>{status}</td></tr>
</table>
<h2>Next step</h2>
<p>Install the app on the repo:
  <a href="https://github.com/organizations/{_ORG}/settings/installations"
     target="_blank">Open Installations</a>
</p>
<p>Then delete <code>{pem_path}</code> (already stored as secret).</p>
<p>You can close this tab.</p>
</body></html>""")

    def _respond(self, status: int, html: str):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


def main():
    """Run the manifest flow: form → GitHub → callback → secrets."""
    manifest = _load_manifest()
    _CallbackHandler._manifest_json = json.dumps(manifest)

    print("=" * 60)
    print("  GlassBox Agent — GitHub App Setup")
    print("=" * 60)
    print(f"\n  Manifest:  {_MANIFEST_PATH}")
    print(f"  Org:       {_ORG}")
    print(f"  Repo:      {_REPO}")
    print(f"  Callback:  http://localhost:{_PORT}/callback")
    print(f"\n  Opening browser — click 'Create GitHub App' on the GitHub page.\n")

    server = http.server.HTTPServer(("localhost", _PORT), _CallbackHandler)

    webbrowser.open(f"http://localhost:{_PORT}/")

    # Two requests: serve form (GET /) then handle callback (GET /callback)
    server.handle_request()
    server.handle_request()

    if _CallbackHandler.app_data:
        slug = _CallbackHandler.app_data.get("slug", "glassbox-agent")
        print(f"\n  Done! Install the app:")
        print(f"  https://github.com/organizations/{_ORG}/settings/installations")
        print(f"\n  Then delete: github-app/{slug}.pem")
        print(f"  Bot will post as: @{slug}[bot]")
    else:
        print("\n  Setup failed. Check output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
