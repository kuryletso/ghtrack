import argparse
import sys
from api import GitHubClient
from activity import format_activity_text, format_activity_json
from graph import format_contribution_graph_text, format_contribution_graph_json


def parse_args():
    parser = argparse.ArgumentParser(prog="ghtrack",
                                     description="Show GitHub contribution graph and recent activity")
    parser.add_argument("username",
                        help="GitHub username")
    parser.add_argument("-g", "--graph",
                        action="store_true",
                        help="Only show contribution graph.")
    parser.add_argument("-a", "--activity",
                        action="store_true",
                        help="Only show recent activity.")
    parser.add_argument("--json",
                        action="store_true",
                        help="Output raw JSON instead of formatted output")
    parser.add_argument("-l","--limit",
                        type=int,
                        default=50,
                        help="Number of recent activities to show (default=10)")
    parser.add_argument("--no-color",
                        action="store_true",
                        help="Disable ANSI colors in output. Automatically disabled if piped or redirected")
    args =  parser.parse_args()

    if args.json:
        modes = sum([args.graph, args.activity])
        if modes != 1:
            parser.error("--json requires exactly one of --graph or --activity")

    return args


def main():
    args = parse_args()

    username = args.username
    show_graph = args.graph
    show_activity = args.activity

    if not show_graph and not show_activity:
        show_graph = True
        show_activity = True

    if args.limit <= 0:
        print("Error: --limit must be a positive integer")
        sys.exit(1)

    # If stdout is piped or redirected, color is automatically disabled
    if not sys.stdout.isatty():
        args.no_color = True

    with GitHubClient() as client:
        if show_graph:
            graph = client.fetch_contribution_graph(username=username)
            if args.json:
                output = format_contribution_graph_json(days=graph)
            else:
                output = format_contribution_graph_text(
                    days=graph,
                    no_color=args.no_color
                )
            print(output)

        if show_activity:
            activity = client.fetch_user_activity(
                username=username,
                limit=args.limit
            )
            output: str = ''
            if args.json:
                output = format_activity_json(activity)
            else:
                output = format_activity_text(
                    events=activity,
                    username=username,
                    no_color=args.no_color
                )
            print(output)



if __name__ == "__main__":
    main()