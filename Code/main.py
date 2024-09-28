import argparse
import logging
from pathlib import Path

from api import ChatClientModule
from DMBotNetwork import Client
from gui.dm_client_app import DMClientApp
from root_path import ROOT_PATH
from systems.discord_rpc import DiscordRPC
from systems.loc import Localization as loc


class FixedWidthFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = f"{record.levelname:<7}"
        return super().format(record)


def init_classes() -> None:
    Client.register_methods_from_class([ChatClientModule])


def main() -> None:
    loc.load_translations(Path(ROOT_PATH / "Content" / "Client" / "loc" / "rus"))
    init_classes()
    DiscordRPC()

    Client()
    DMClientApp()
    DMClientApp.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск клиента DMBot")
    parser.add_argument("--debug", action="store_true", help="Включение режима отладки")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO

    handler = logging.StreamHandler()
    formatter = FixedWidthFormatter(
        "[%(asctime)s][%(levelname)s] %(name)s: %(message)s"
    )

    handler.setFormatter(formatter)

    logging.basicConfig(
        level=log_level,
        handlers=[handler],
    )

    main()
