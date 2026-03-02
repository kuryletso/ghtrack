from dataclasses import dataclass
from bs4 import BeautifulSoup
import httpx
import os


# DATA MODELS
@dataclass
class ActivityEvent:
    type: str
    repo: str
    created_at: str
    raw: dict

@dataclass
class ContributionDay:
    date: str
    level: int

class GitHubAPIError(Exception):
    pass

# BUILD CLIENT
class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ghtrack-cli",
        }

        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers=self.headers,
            timeout=10.0
        )

        self.html_client = httpx.Client(
            headers={
                    "Accept" : "text/html",
                    "User-Agent": "ghtrack-cli"
            },
            timeout=10.0
        )

    def __enter__(self):
        return self
    
    def _close(self):
        self.client.close()

    def __exit__(self, exc_type, exc, tb):
        self._close()


    # UTILS
    def _get(self, endpoint: str, params: dict | None = None):
        try:
            response = self.client.get(endpoint, params=params)
        except httpx.RequestError as e:
            raise GitHubAPIError(f"Network error: {e}") from e
        
        if response.status_code >= 400:
            raise GitHubAPIError(
                f"GitHub API error {response.status_code}: {response.text}"
            )
        # remaining_tokens = response.headers.get("X-RateLimit-Remaining")
        
        return response.json()

    def _parse_contributions(self, html: str) -> list[ContributionDay]:
        soup = BeautifulSoup(html, "html.parser")
        calendar = soup.find("table", class_="ContributionCalendar-grid")
        if not calendar:
            raise GitHubAPIError("Failed to locate contributions calendar in HTML.")
        cells = calendar.find_all("td", attrs={"data-date": True})

        contributions = []

        for cell in cells:
            contributions.append(ContributionDay(
                date=cell["data-date"],
                level=int(cell.get("data-level",0))
            ))
        return contributions

    # FETCH DATA
    def fetch_user_activity(
            self,
            username: str,
            limit: int = 10,
    ) -> list[ActivityEvent]:
        data = self._get(f"/users/{username}/events")    
        events = []
        for item in data[:limit]:
            events.append(
                ActivityEvent(
                    type=item["type"],
                    repo=item["repo"]["name"],
                    created_at=item["created_at"],
                    raw=item
                )
            )
        return events

    def fetch_contribution_graph(
            self,
            username: str,
    ) -> list[ContributionDay]:
        url = f"https://github.com/users/{username}/contributions"

        try:
            response = self.html_client.get(url)
        except httpx.RequestError as e:
            raise GitHubAPIError(f"Network error: {e}") from e
        
        if response.status_code == 404:
            raise GitHubAPIError(f"User not found")

        html = response.text

        return self._parse_contributions(html)