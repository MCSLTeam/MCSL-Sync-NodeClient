from src.utils import init_settings, argument_parser, FileSync
from src import __version__
from src.api import start_production_server
import sys


if __name__ == "__main__":
    from src.utils import read_settings
    read_settings()
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
        run(FileSync(upd=args.update).load_self())
    if args.calculate:
        from src.utils.database import get_total_space
        from asyncio import run
        print(run(get_total_space()))
    if args.global_upstream:
        from src.utils import set_upstream
        set_upstream(args.global_upstream)
    sys.exit(0)