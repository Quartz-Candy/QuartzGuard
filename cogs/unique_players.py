import discord
from discord.ext import commands, tasks
from utils.logger import DiscordLogger
from utils.wordpressAPI import WordPressAPI
from datetime import datetime
from bs4 import BeautifulSoup
import os
import json
import requests


class UniquePlayers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = DiscordLogger("UniquePlayers")
        self.wp = WordPressAPI()
        self.player_page_id = 0

        with open(os.path.join("configs", "minecraft_deaths.json"), "r", encoding="utf-8") as cfg:
            mc_config = json.load(cfg)

        with open(os.path.join("configs", "discord.json"), "r", encoding="utf-8") as cfg:
            discord_config = json.load(cfg)

        self.bot_channel = self.bot.get_channel(discord_config.get("bot-chat"))
        self.stats_dir = mc_config.get("stats_dir")

        if not os.path.exists(os.path.join("logs", "unique_players.txt")):
            with open(os.path.join("logs", "unique_players.txt"), "w", encoding="utf-8"):
                pass
        self.unique_players_file = os.path.join("logs", "unique_players.txt")

    async def cog_load(self):
        self.logger.write("info", "loaded")
        self.logger.write("info", "Starting to look for new players")
        self.player_page_id = await self.wp.get_id_by_slug("players")
        self.check_for_new_players.start()

    async def cog_unload(self):
        self.logger.write("info", "unloaded")
        self.check_for_new_players.stop()
        self.logger.write("info", "Stopped looking for new players")

    @tasks.loop(seconds=120)
    async def check_for_new_players(self):
        with open(self.unique_players_file, "r", encoding="utf-8") as players:
            unique_players = {line.strip() for line in players}

        stat_files = os.listdir(self.stats_dir)

        for stat in stat_files:
            uuid = stat[:-5]
            if uuid not in unique_players:
                player = self._get_username(uuid)
                self.logger.write("info", f"Found new player {player} | {uuid}")

                embed = discord.Embed(title=player,
                                      colour=0x00b0f4,
                                      timestamp=datetime.now())
                embed.set_author(name="New player!")
                embed.set_image(url=f"https://mc-heads.net/head/{uuid}")

                await self.bot_channel.send(embed=embed)
                self.logger.write("info", f"Announced new player {player}")

                if await self._post_to_player_list(uuid, player) == 200:
                    self.logger.write("info", f"Added {player} to site")
                else:
                    self.logger.write("info", f"Failed to add {player} to site")

                with open(self.unique_players_file, "a+", encoding="utf-8") as file:
                    file.write(f"{uuid}\n")
                    self.logger.write("info", f"Wrote {uuid} to unique_players.txt")

    async def _post_to_player_list(self, uuid, username):
        html = await self.wp.get_page(self.player_page_id)
        soup = BeautifulSoup(html["content"]["rendered"], "html.parser")

        player_table = soup.find("table")

        if not player_table:
            self.logger.write("critical", "Unable to find table")
            return None

        # Check if the player is already in the table
        if uuid in str(player_table):
            self.logger.write("info", "Player already in list. Skipping")
            return None

        # Create new <tr> for the player
        new_tr = soup.new_tag("tr")

        # Create the figure tag
        new_player_figure = soup.new_tag("figure")

        # Create the img tag
        new_img = soup.new_tag("img",
                               src=f"https://mc-heads.net/avatar/{uuid}/50",
                               alt=username,
                               decoding="async",
                               style="border-radius:4px; display:block; margin:auto;")

        # Append the img tag to the figure tag
        new_player_figure.append(new_img)

        # Append the player's username as text below the image
        new_player_figure.append(soup.new_string(username))

        # Create a <center> tag above the figure
        new_center = soup.new_tag("center")
        new_center.append(new_player_figure)

        # Create a <td> to wrap the player figure (with center)
        new_td = soup.new_tag("td")
        new_td.append(new_center)

        # Get the current rows in the table to check how many columns
        current_rows = player_table.find_all("tr")

        # Add the <td> to the appropriate row
        if current_rows:
            # Check the last row for its number of columns
            last_row = current_rows[-1]
            last_row_cells = last_row.find_all("td")

            # If the last row has less than 4 cells, append to it
            if len(last_row_cells) < 4:
                last_row.append(new_td)
            else:
                # Otherwise, create a new row
                new_tr.append(new_td)
                player_table.append(new_tr)
        else:
            # If there are no rows, start the table with the new row
            new_tr.append(new_td)
            player_table.append(new_tr)

        # After modifying the HTML, convert it back to a string
        new_player_list_html = str(soup)

        # Update the page with the new HTML content
        return await self.wp.update_page(self.player_page_id, title="Players", content=new_player_list_html)

    # not worth writing as an async
    def _get_username(self, uuid):
        url = f"https://api.minecraftservices.com/minecraft/profile/lookup/{uuid}"
        response = requests.get(url).json()

        try:
            return response["name"]
        except KeyError:
            self.logger.write("error", f"Unable to get username for {uuid}")
            return None

async def setup(bot):
    await bot.add_cog(UniquePlayers(bot))
