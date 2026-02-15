"""Phase 2 tests: BaseAgent ABC + GitHubClient."""

import pytest
from unittest.mock import MagicMock, patch

from glassbox_agent.core.base_agent import BaseAgent
from glassbox_agent.core.settings import Settings
from glassbox_agent.tools.github_client import GitHubClient


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing the ABC."""
    def think(self, context: dict) -> str:
        return "thinking..."
    def act(self, context: dict) -> dict:
        return {"result": "done"}


class TestBaseAgent:
    def setup_method(self):
        self.client = MagicMock()
        self.github = MagicMock(spec=GitHubClient)
        self.settings = Settings()
        self.agent = ConcreteAgent(
            name="Test Agent", avatar="🧪",
            client=self.client, github=self.github, settings=self.settings,
        )

    def test_name_and_avatar(self):
        assert self.agent.name == "Test Agent"
        assert self.agent.avatar == "🧪"

    def test_comment_formats_with_header(self):
        self.github.post_comment.return_value = 123
        cid = self.agent.comment(42, "Hello world")
        self.github.post_comment.assert_called_once()
        body = self.github.post_comment.call_args[0][1]
        assert "🧪 **Test Agent**" in body
        assert "Hello world" in body
        assert cid == 123

    def test_react_delegates_to_github(self):
        self.agent.react(99, "+1")
        self.github.add_reaction.assert_called_once_with(99, "+1")

    def test_call_llm(self):
        mock_choice = MagicMock()
        mock_choice.message.content = '{"result": true}'
        self.client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
        result = self.agent._call_llm("test prompt", json_mode=True)
        assert result == '{"result": true}'
        call_kwargs = self.client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["response_format"] == {"type": "json_object"}

    def test_abstract_methods_enforced(self):
        with pytest.raises(TypeError):
            BaseAgent(name="X", avatar="X", client=MagicMock(),
                      github=MagicMock(), settings=Settings())

    def test_think_and_act(self):
        assert self.agent.think({}) == "thinking..."
        assert self.agent.act({}) == {"result": "done"}


class TestGitHubClient:
    def test_init(self):
        gh = GitHubClient("owner/repo")
        assert gh._repo == "owner/repo"

    @patch("glassbox_agent.tools.github_client.GitHubClient._gh_api")
    def test_post_comment(self, mock_api):
        mock_api.return_value = MagicMock(returncode=0, stdout='{"id": 456}', stderr="")
        gh = GitHubClient("owner/repo")
        cid = gh.post_comment(42, "test body")
        assert cid == 456

    @patch("glassbox_agent.tools.github_client.GitHubClient._gh_api")
    def test_update_comment(self, mock_api):
        mock_api.return_value = MagicMock(returncode=0)
        gh = GitHubClient("owner/repo")
        assert gh.update_comment(123, "updated") is True

    def test_update_comment_invalid_id(self):
        gh = GitHubClient("owner/repo")
        assert gh.update_comment(0, "body") is False
        assert gh.update_comment(-1, "body") is False

    @patch("glassbox_agent.tools.github_client.GitHubClient._gh_api")
    def test_add_reaction(self, mock_api):
        mock_api.return_value = MagicMock(returncode=0)
        gh = GitHubClient("owner/repo")
        assert gh.add_reaction(123, "+1") is True

    def test_add_reaction_invalid_id(self):
        gh = GitHubClient("owner/repo")
        assert gh.add_reaction(0) is False

    @patch("glassbox_agent.tools.github_client.GitHubClient._gh_api")
    def test_silent_update_edits_existing(self, mock_api):
        mock_api.return_value = MagicMock(returncode=0)
        gh = GitHubClient("owner/repo")
        result = gh.silent_update(42, 123, "updated body")
        assert result == 123

    @patch("glassbox_agent.tools.github_client.GitHubClient._gh_api")
    def test_silent_update_falls_back_to_post(self, mock_api):
        mock_api.side_effect = [
            MagicMock(returncode=1),  # update fails
            MagicMock(returncode=0, stdout='{"id": 789}', stderr=""),  # post succeeds
        ]
        gh = GitHubClient("owner/repo")
        result = gh.silent_update(42, 123, "body")
        assert result == 789

    @patch("glassbox_agent.tools.github_client.GitHubClient._gh_api")
    def test_create_pr(self, mock_api):
        mock_api.return_value = MagicMock(
            returncode=0, stdout='{"html_url": "https://github.com/o/r/pull/1"}'
        )
        gh = GitHubClient("owner/repo")
        url = gh.create_pr("branch", 42, "title", "body")
        assert "pull/1" in url
