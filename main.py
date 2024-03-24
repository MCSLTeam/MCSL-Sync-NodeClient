from src.utils import init_settings, argument_parser, FileSync
from src import __version__
from src.api import start_production_server
import sys


if __name__ == "__main__":
    args = argument_parser.parse_args()
    if not any(value for _, value in args.__dict__.items()):
        argument_parser.error("No argument was specified.")

    if args.init:
        init_settings()
    if args.server:
        start_production_server()
    if args.version:
        print(__version__)
    if args.test_url:
        pass
    if args.update:
        from asyncio import run
        run(FileSync().load_self())
    if args.calculate:
        from src.utils.database import get_total_space
        from asyncio import run
        print(run(get_total_space()))
    sys.exit(0)