from api import ActivityEvent, ContributionDay
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime
import json


@dataclass
class RepoActivity:
    event_cnt: dict[str,int]
    last_update: datetime

def render_activity(
        events: list[ActivityEvent],
        username: str,
        return_json: bool = False,
        no_color: bool = False
        ) -> str:
    
    if return_json:
        parsed_events = [event.raw for event in events]
        json_string = json.dumps(parsed_events, indent=2)
        return json_string

    # Group by repos
    repos: dict[str, RepoActivity] = {}
    for event in events:
        repo = repos.get(event.repo)
        if event.repo not in repos:
            repos.setdefault(
                event.repo,
                RepoActivity(
                    event_cnt=defaultdict(int),
                    last_update=event.created_at
                    )
                )
        repo = repos[event.repo]
        repo.event_cnt[event.type] += 1
        repo.last_update = max(repo.last_update,event.created_at)
    
    # Order by latets event in repo
    sorted_repos = sorted(
        repos.items(),
        key=lambda x: x[1].last_update,
        reverse=True
        )

    header = f"Recent activity of {username}:\n"
    content: list[str] = []
    for repo,activity in sorted_repos:
        for event,cnt in sorted(activity.event_cnt.items()):
            row = f"- done {cnt} {event} in {repo}"
            content.append(row)

    return header + "\n".join(content)