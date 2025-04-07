#!python3
# encoding=utf-8
import logging
import os
import requests
import ics


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Fetch calendar events and export static files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("output", help="Output directory for the exported files")
    parser.add_argument(
        "--urls",
        nargs="*",
        help="URL to fetch the iCalendar file from, e.g. https://calendars.icloud.com/holidays/cn_zh.ics",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Path to the iCalendar file, e.g. /path/to/your/file.ics",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    events = []
    if args.urls:
        for url in args.urls:
            logging.info(f"Fetching calendar from {url}")
            response = requests.get(url)
            response.raise_for_status()
            calendar = ics.Calendar(response.text)
            for event in calendar.events:
                events.append(event)
    if args.files:
        for path in args.files:
            logging.info(f"Reading calendar from {path}")
            calendar = ics.Calendar(open(path, "r").read())
            for event in calendar.events:
                events.append(event)

    data = {}
    for event in events:
        logging.debug(f"Add event {event.name} from {event.begin} to {event.end}")
        for timestamp in range(event.begin.int_timestamp, event.end.int_timestamp):
            if timestamp not in data:
                data[timestamp] = set()
            data[timestamp].add(event.name)

    symlinks = {}
    os.makedirs(args.output, exist_ok=True)
    for timestamp, events in data.items():
        logging.debug(f"Writing events for {timestamp}: {events}")
        text = "\n".join(sorted(events))
        if text in symlinks:
            os.symlink(symlinks[text], f"{args.output}/{timestamp}")
        else:
            with open(f"{args.output}/{timestamp}", "w") as f:
                f.write(text)
            symlinks[text] = f"./{timestamp}"
