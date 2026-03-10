from ghtrack.api import GitHubClient, GitHubAPIError, ContributionDay
from unittest.mock import Mock
from datetime import datetime
import pytest

SAMPLE_HTML = """
<table class="ContributionCalendar-grid">
  <tr>
    <td class="ContributionCalendar-day"
        data-date="2026-02-18"
        data-level="4"></td>
    <td class="ContributionCalendar-day"
        data-date="2026-02-19"
        data-level="2"></td>
  </tr>
</table>
"""

def test_parse_contributions():
    client = GitHubClient()
    result = client._parse_contributions(SAMPLE_HTML)

    assert len(result) == 2
    assert result[0].date == "2026-02-18"
    assert result[0].level == 4
    assert result[1].date == "2026-02-19"
    assert result[1].level == 2

def test_get():
    client = GitHubClient()

    mock_response = Mock()
    mock_response.status_code = 404

    client.client.get = Mock(return_value=mock_response)

    try:
        client._get("/users/unknown")
    except GitHubAPIError as e:
        assert "GitHub API error 404" in str(e)
    else:
        assert False, "Expected GitHub API error"

def test_fetch_user_activity():
    client = GitHubClient()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "type": "PushEvent",
            "repo": {"name": "user/repo"},
            "created_at": "2026-02-18T00:00:00Z"
        }
    ]

    client.client.get = Mock(return_value=mock_response)
    events = client.fetch_user_activity("user",limit=1)

    assert len(events) == 1
    assert events[0].type == "PushEvent"
    assert events[0].repo == "user/repo"
    assert events[0].created_at == datetime.fromisoformat("2026-02-18T00:00:00Z")

def test_fetch_contribution_graph():
    client = GitHubClient()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = SAMPLE_HTML

    client.html_client.get = Mock(return_value=mock_response)

    result = client.fetch_contribution_graph("user")

    assert isinstance(result, list)
    assert len(result) == 2

    assert isinstance(result[0], ContributionDay)
    assert result[0].date == "2026-02-18"
    assert result[0].level == 4

    assert isinstance(result[1], ContributionDay)
    assert result[1].date == "2026-02-19"
    assert result[1].level == 2

def test_fetch_contribution_graph_404():
    client = GitHubClient()

    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = ""

    client.html_client.get = Mock(return_value=mock_response)

    with pytest.raises(GitHubAPIError, match="User not found"):
        client.fetch_contribution_graph("user")