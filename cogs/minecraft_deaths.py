import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from utils.logger import DiscordLogger
from utils.wordpressAPI import WordPressAPI
from build_html import obituary
from datetime import datetime
import hashlib
import os
import json
import shutil


class MinecraftDeaths(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = DiscordLogger("MinecraftDeaths")
        self.wp = WordPressAPI()
        self.graveyard_id = 0

        try:
            with open(os.path.join("configs", "minecraft_deaths.json"), "r", encoding="utf-8") as cfg:
                mc_config = json.load(cfg)
        except RuntimeError as e:
            self.logger.write("critical", f"Failed to load config! {e}")

        try:
            with open(os.path.join("configs", "discord.json"), "r", encoding="utf-8") as cfg:
                discord_config = json.load(cfg)
        except RuntimeError as e:
            self.logger.write("critical", f"Failed to load config! {e}")

        # Minecraft Deaths Config
        self.stats_dir = mc_config.get("stats_dir")
        self.player_deaths_dir = mc_config.get("player_deaths_dir")

        self.player_deaths_original = os.path.join(self.player_deaths_dir, "player_deaths.log")
        self.player_deaths_compare = mc_config.get("player_deaths_compare")
        self.death_compare_hash = None

        # Discord Config
        self.general_channel = self.bot.get_channel(discord_config.get("general-chat"))
        self.graveyard_channel = self.bot.get_channel(discord_config.get("graveyard"))
        self.bot_channel = self.bot.get_channel(discord_config.get("bot-chat"))
        # TODO: add graveyard channel to list
        self.send_to_channels = [self.general_channel]

    async def cog_load(self):
        # creates files if not present and copies modified time
        if not os.path.exists(self.player_deaths_original):
            with open(self.player_deaths_original, "w+", encoding="utf-8"):
                self.logger.write("info", "Creating player_deaths.log")

        if not os.path.exists(self.player_deaths_compare):
            await self.copy_deaths()
            self.logger.write("info", "Copying player deaths")

        self.logger.write("info", "Checking for new player deaths")
        self.logger.write("info", "loaded")

        # Here because it needs await and I can't do that in __init__
        self.graveyard_id = await self.wp.get_id_by_slug("graveyard")
        await self.get_player_deaths.start()

    async def cog_unload(self):
        self.get_player_deaths.stop()
        self.logger.write("info", "Stopped checking for new player deaths")
        self.logger.write("info", "unloaded")

    async def copy_deaths(self):
        shutil.copy2(self.player_deaths_original, self.player_deaths_compare)

    async def get_stats(self, uuid):
        try:
            with open(os.path.join(self.stats_dir, f"{uuid}.json"), "r", encoding="utf-8") as stats:
                return stats.readlines()[0]
        except FileNotFoundError:
            self.logger.write("error", f"{uuid}.json not found in stats folder")
        except Exception as e:
            self.logger.write("critical", e)


    @tasks.loop(seconds=10)
    async def get_player_deaths(self):
        with open(self.player_deaths_original, "rb") as data:
            original_hash = hashlib.md5(data.read()).hexdigest()

        if self.death_compare_hash != original_hash:
            with open(self.player_deaths_compare, "rb") as data:
                self.death_compare_hash = hashlib.md5(data.read()).hexdigest()

            with open(self.player_deaths_original, "r", encoding="utf-8") as file:
                original_content = file.readlines()
            with open(self.player_deaths_compare, "r", encoding="utf-8") as file:
                compare_content = file.readlines()

            for change in set(original_content).symmetric_difference(set(compare_content)):
                json_string = json.loads(change)

                # feel like there has to be another way, but trying to get first key with just json would not work
                uuid = list(json_string.keys())[0]
                player = json_string[uuid]["player"]
                death_msg = json_string[uuid]["deathMessage"]
                time_of_death = json_string[uuid]["time"]

                embed = discord.Embed(title=f"🪦 {player} has died!",
                                      description=death_msg,
                                      colour=0x00b0f4,
                                      timestamp=datetime.now())

                embed.add_field(name="Obituary",
                                value=f"https://quartzcandy.com/graveyard/{player}",
                                inline=False)

                embed.set_image(url=f"https://mc-heads.net/head/{uuid}")
                self.logger.write("info", f"Announced {player}'s death to Discord")

                # TODO: Fix permission error to graveyard channel
                for channel in self.send_to_channels:
                    await channel.send(embed=embed)

                html_content = obituary.obituary_html(player, death_msg, time_of_death,
                                                      uuid, stats=await self.get_stats(uuid))

                if await self.wp.create_page(player, html_content, parent=self.graveyard_id, status="publish") != 201:
                    self.logger.write("error", f"Failed to post {player}'s obituary to WordPress")
                    await self.bot_channel.send(f"⚠️ Failed to upload {player}'s obituary to WordPress!"
                                                f"||@{206267067131756545} sucks at programming or the site is down||")

                    await self.wp.store_request(self.graveyard_id, player, html_content, f"{player}_obituary.json")
                else:
                    self.logger.write("info", f"Posted {player}'s obituary to WordPress")


                if await self._update_graveyard(player, uuid) != 200:
                    self.logger.write("error", f"Failed to add {player} to the graveyard")
                    await self.bot_channel.send(f"⚠️ Failed to add {player} to the graveyard!")

                    await self.wp.store_request(self.graveyard_id, player, "", f"{player}_graveyard.json")
                else:
                    self.logger.write("info", f"Added {player} to the graveyard")

            await self.copy_deaths()
            self.logger.write("info", "Copied player deaths")

    async def _update_graveyard(self, player, uuid):
        html = await self.wp.get_page(self.graveyard_id)
        soup = BeautifulSoup(html["content"]["rendered"], "html.parser")

        player_table = soup.find("table")

        if not player_table:
            self.logger.write("critical", "Unable to find table")
            return None

        elif uuid in player_table:
            self.logger.write("info", "Player already in graveyard. Skipping")
            return None

        """
        GPT wrote the rest of this function. I spent hours trying to build the html
        myself and replacing the contents and while I could build the html I could
        not for the life of me replace the string instance of the current table into
        the new html to post. So I apologize for my sins and expect to be shamed :(
        
        Also this needs a sacrificial player to work so while I intended to find the
        rest of the table with html comments on the website, it would only be
        required for the first time. So instead I'm going to do the wrong thing
        and wait for a sacrifice.
        """
        new_tr = soup.new_tag("tr")
        new_th = soup.new_tag("th")
        new_h2 = soup.new_tag("h2", style="display:inline-block;")

        new_img = soup.new_tag(
            "img",
            src=f"https://mc-heads.net/avatar/{uuid}",
            width="25",
            height="25",
            loading="lazy",
            decoding="async",
            alt=""
        )

        new_a = soup.new_tag(
            "a",
            href=f"https://quartzcandy.com/graveyard/{player}"
        )
        new_a.string = player

        new_h2.append(new_img)
        new_h2.append("\n")
        new_h2.append(new_a)
        new_th.append(new_h2)
        new_tr.append(new_th)

        first_tr = player_table.find("tr")
        if first_tr:
            first_tr.insert_before(new_tr)
        else:
            player_table.append(new_tr)

        new_graveyard_html = str(soup)

        return await self.wp.update_page(self.graveyard_id, title="Graveyard", content=new_graveyard_html)

        # COMMANDS
        # rebuild player
        # rebuild all
        # multiple test players


async def setup(bot):
    await bot.add_cog(MinecraftDeaths(bot))
