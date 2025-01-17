from gettext import gettext as _

from gi.repository import Gio

from lutris.services.steam import SteamService, SteamGame
from lutris.database.games import get_game_by_field, get_games
from lutris.util.log import logger
from lutris.game import Game
from lutris.util.strings import slugify

STEAM_INSTALLER = "steam-wine"  # Lutris installer used to setup the Steam client


class SteamWindowsGame(SteamGame):
    service = "steamwindows"
    installer_slug = "steamwindows"
    runner = "wine"


class SteamWindowsService(SteamService):
    id = "steamwindows"
    name = _("Steam for Windows")
    runner = "wine"
    game_class = SteamWindowsGame

    def generate_installer(self, db_game, steam_game):
        """Generate a basic Steam installer"""
        return {
            "name": db_game["name"],
            "version": self.name,
            "slug": slugify(db_game["name"]) + "-" + self.id,
            "game_slug": slugify(db_game["name"]),
            "runner": self.runner,
            "appid": db_game["appid"],
            "script": {
                "requires": "steam-wine",
                "game": {"appid": db_game["appid"]}
            }
        }

    def install(self, db_game):
        steam_game = get_game_by_field("steam-wine", "installer_slug")
        if not steam_game:
            logger.error("Steam for Windows is not installed in Lutris")
            return

        appid = db_game["appid"]
        db_games = get_games(filters={"service_id": appid, "installed": "1", "service": self.id})
        existing_game = self.match_existing_game(db_games, appid)
        if existing_game:
            logger.debug("Found steam game: %s", existing_game)
            game = Game(existing_game.id)
            game.save()
            return
        application = Gio.Application.get_default()
        application.show_installer_window(
            [self.generate_installer(db_game, steam_game)],
            service=self,
            appid=appid
        )
