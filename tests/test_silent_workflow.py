"""Tests for silent workflow - PATCH updates suppress email notifications.

Covers: update_comment in GitHubClient, silent_update in AgentPipeline.
"""

import json
import os
import subprocess
import sys
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.agent.github import GitHubClient


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def gh():
    """GitHubClient with test repo."""
    return GitHubClient("test-org/test-repo")


# ── update_comment: happy path ───────────────────────────────────────

def test_update_comment_uses_patch_method(gh):
    """update_comment must use PATCH (not POST) to avoid triggering email."""
    with patch.object(gh, "_gh_api") as mock_api:
        mock_api.return_value = MagicMock(returncode=0, stdout='{}', stderr='')
        gh.update_comment(123, "new body")
        mock_api.assert_called_once_with(
            "repos/test-org/test-repo/issues/comments/123",
            method="PATCH",
            data={"body": "new body"},
        )


def test_update_comment_returns_true_on_success(gh):
    """update_comment returns True when PATCH succeeds."""
    with patch.object(gh, "_gh_api") as mock_api:
        mock_api.return_value = MagicMock(returncode=0, stdout='{}', stderr='')
        result = gh.update_comment(123, "body")
        assert result is True


# ── update_comment: error handling ───────────────────────────────────

def test_update_comment_returns_false_on_failure(gh):
    """update_comment returns False when PATCH fails (e.g. comment deleted)."""
    with patch.object(gh, "_gh_api") as mock_api:
        mock_api.return_value = MagicMock(returncode=1, stdout='', stderr='Not Found')
        result = gh.update_comment(999, "body")
        assert result is False


def test_update_comment_returns_false_on_invalid_id(gh):
    """update_comment returns False for comment_id=0 or negative."""
    result = gh.update_comment(0, "body")
    assert result is False


# ── post_comment returns comment_id ──────────────────────────────────

def test_post_comment_returns_comment_id(gh):
    """post_comment must return the comment_id from the API response."""
    resp = json.dumps({"id": 42, "html_url": "https://github.com/..."})
    with patch.object(gh, "_gh_api") as mock_api:
        mock_api.return_value = MagicMock(returncode=0, stdout=resp, stderr='')
        comment_id = gh.post_comment(1, "hello")
        assert comment_id == 42


def test_post_comment_returns_zero_on_parse_error(gh):
    """post_comment returns 0 if API response is not valid JSON."""
    with patch.object(gh, "_gh_api") as mock_api:
        mock_api.return_value = MagicMock(returncode=0, stdout='not json', stderr='')
        comment_id = gh.post_comment(1, "hello")
        assert comment_id == 0


def test_post_comment_returns_zero_on_api_error(gh):
    """post_comment returns 0 if API call fails."""
    with patch.object(gh, "_gh_api") as mock_api:
        mock_api.return_value = MagicMock(returncode=1, stdout='', stderr='error')
        comment_id = gh.post_comment(1, "hello")
        assert comment_id == 0


# ── Integration: silent_update fallback ──────────────────────────────

def test_silent_update_falls_back_to_post_when_no_comment_id(gh):
    """When ack_comment_id is 0, silent_update falls back to post_comment."""
    resp = json.dumps({"id": 99})
    with patch.object(gh, "_gh_api") as mock_api:
        mock_api.return_value = MagicMock(returncode=0, stdout=resp, stderr='')
        comment_id = gh.silent_update(issue_number=1, comment_id=0, body="test")
        # Should have called POST (new comment), not PATCH
        call_args = mock_api.call_args
        assert "issues/1/comments" in call_args[0][0]
        assert comment_id == 99


def test_silent_update_edits_when_comment_id_valid(gh):
    """When ack_comment_id is valid, silent_update uses PATCH."""
    with patch.object(gh, "_gh_api") as mock_api:
        mock_api.return_value = MagicMock(returncode=0, stdout='{}', stderr='')
        comment_id = gh.silent_update(issue_number=1, comment_id=42, body="updated")
        call_args = mock_api.call_args
        assert "issues/comments/42" in call_args[0][0]
        assert call_args[1].get("method") == "PATCH" or call_args[0][1] == "PATCH"
        assert comment_id == 42


def test_silent_update_falls_back_to_post_when_patch_fails(gh):
    """When PATCH fails, silent_update falls back to POST."""
    resp_post = json.dumps({"id": 77})
    with patch.object(gh, "_gh_api") as mock_api:
        # First call (PATCH) fails, second call (POST) succeeds
        mock_api.side_effect = [
            MagicMock(returncode=1, stdout='', stderr='Not Found'),
            MagicMock(returncode=0, stdout=resp_post, stderr=''),
        ]
        comment_id = gh.silent_update(issue_number=1, comment_id=42, body="test")
        assert comment_id == 77
        assert mock_api.call_count == 2
