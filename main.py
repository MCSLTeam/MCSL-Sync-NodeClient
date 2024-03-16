from src.utils import init_settings, argument_parser
from src import __version__
from src.api import start_production_server
import sys
from src.utils.downloader import AsyncDownloader


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
    if args.download:
        downloader = AsyncDownloader()
        import asyncio
        asyncio.run(downloader.download(uri=args.download, core_type="Paper", mc_version="1.19.3", core_version="308"))

    sys.exit(0)
