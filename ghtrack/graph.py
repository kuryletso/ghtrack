from api import ContributionDay
from dataclasses import asdict
import json

LEVEL_MAP_WITH_COLOR = {
    0: "\033[48;5;236m  \033[0m",
    1: "\033[48;5;22m  \033[0m",
    2: "\033[48;5;28m  \033[0m",
    3: "\033[48;5;34m  \033[0m",
    4: "\033[48;5;40m  \033[0m",
}

LEVEL_MAP_NO_COLOR = {
    0: '..',
    1: '::',
    2: 'oo',
    3: 'OO',
    4: '@@'
}

def _group_by_days(
        days: list[ContributionDay],
        ) -> list[list[ContributionDay]]:
    weeks = []
    current_week = []

    for day in days:
        current_week.append(day)
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
    if current_week:
        weeks.append(current_week)

    return weeks

def _build_month_labels(weeks: list[list[ContributionDay]]):
    width = len(weeks) * 2
    label_line = [" "] * width

    prev_month = None

    for i,week in enumerate(weeks):
        first_day = week[0].date
        month = first_day.strftime("%b")

        if month != prev_month:
            pos = i * 2
            for j, ch in enumerate(month):
                if pos + j < width:
                    label_line[pos + j] = ch
            prev_month = month
    return "    " + "".join(label_line)

def format_contribution_graph_text(
        days: list[ContributionDay],
        no_color: bool,
        ) -> str:
    days.sort(key=lambda x: x.date)
    weeks = _group_by_days(days)
    content = LEVEL_MAP_NO_COLOR if no_color else LEVEL_MAP_WITH_COLOR
    
    lines = []
    lines.append(_build_month_labels(weeks))

    weekday_labels = {
        1: 'Mon ',
        3: 'Wed ',
        5: 'Fri '
    }

    for row in range(7):
        prefix = weekday_labels.get(row, "    ")
        line = [prefix]
        for week in weeks:
            if row < len(week):
                level = week[row].level
                line.append(content[level])
            else:
                line.append("  ")
        lines.append("".join(line))

    return "\n".join(lines)

def format_contribution_graph_json(
        days: list[ContributionDay]
        ) -> str:
    return json.dumps(
        [{"date": d.date.isoformat(), "level": d.level} for d in days],
        indent=2
        )