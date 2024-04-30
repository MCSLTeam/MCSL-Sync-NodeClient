
import argparse

argument_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
argument_parser.add_argument(
    "-v",
    "--version",
    help="Show version of MCSL-Sync-Nodeside",
    action="store_true",
    default=False,
)
argument_parser.add_argument(
    "-u",
    "--update",
    help="Update core files",
    # action="store_true",
    default=False,
)
argument_parser.add_argument(
    "-i",
    "--init",
    help="Init MCSL-Sync-Nodeside configuration",
    action="store_true",
    default=False,
)
argument_parser.add_argument(
    "-s",
    "--server",
    help="Run MCSL-Sync-Nodeside server",
    action="store_true",
    default=False,
)
argument_parser.add_argument(
    "-t",
    "--test-url",
    help="Test Downloader",
    default=False,
)
argument_parser.add_argument(
    "-g",
    "--global-upstream",
    help="Set global upstream server",
    default=False,
)
argument_parser.add_argument(
    "-sg",
    "--sync-database",
    help="Sync database",
    action="store_true",
    default=False,
)