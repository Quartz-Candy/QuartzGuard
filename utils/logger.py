import logging
from os import path


class DiscordLogger:
    def __init__(self, cog_name, filename=path.join("logs", "quartzguard.log")):
        self.cog_name = cog_name

        logging.basicConfig(filename=filename,
                            encoding="utf-8",
                            filemode="a",
                            format="{asctime} - {levelname} - {message}",
                            style="{", datefmt="%m-%d-%Y %H:%M", )

    def write(self, level, message):
        if level.upper() == "DEBUG":
            logging.debug(f"[{self.cog_name}] {message}")
            print(f"{level.upper()} - [{self.cog_name}] {message}")

        elif level.upper() == "INFO":
            logging.info(f"[{self.cog_name}] {message}")
            print(f"{level.upper()} - [{self.cog_name}] {message}")

        elif level.upper() == "WARNING":
            logging.warning(f"[{self.cog_name}] {message}")
            print(f"{level.upper()} - [{self.cog_name}] {message}")

        elif level.upper() == "ERROR":
            logging.error(f"[{self.cog_name}] {message}")
            print(f"{level.upper()} - [{self.cog_name}] {message}")

        elif level.upper() == "CRITICAL":
            logging.critical(f"[{self.cog_name}] {message}")
            print(f"{level.upper()} - [{self.cog_name}] {message}")

        else:
            logging.debug(f"[{self.cog_name}] *Missing level* {message}")
            print(f"{level.upper()} - [{self.cog_name}] *Missing level* {message}")