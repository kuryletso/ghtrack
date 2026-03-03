from api import ActivityEvent, ContributionDay
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class RepoActivity:
    event_cnt: defaultdict[str,int]
    last_update: str

def render_activity(
        events: list[ActivityEvent],
        username: str,
        return_json: bool = False,
        no_color: bool = False
        ) -> str:
    
    if return_json:
        parsed_events = [event.raw for event in events]
        json_string = json.dumps(parsed_events)
        return json_string

    # Group by repos
    repos: dict[str, RepoActivity] = {}
    for event in events:
        repo = repos.get(event.repo)
        if not repo:
            repo = RepoActivity(
                event_cnt=defaultdict(int),
                last_update=event.created_at
            )
            repos[event.repo] = repo
        repo.event_cnt[event.type] += 1
        repo.last_update = max(repo.last_update,event.created_at)
    
    # Order by latets event in repo
    repos = dict(sorted(
        repos.items(),
        key=lambda x: x[1].last_update,
        reverse=True
        ))

    header = f"Recent activity of {username}:\n"
    content: list[str] = []
    for repo,activity in repos.items():
        for event,cnt in activity.event_cnt.items():
            row = f"- done {cnt} {event} in {repo}"
            content.append(row)

    return header + "\n".join(content)