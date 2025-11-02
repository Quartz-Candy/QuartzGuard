from discord.ext import commands
from utils.logger import DiscordLogger

class ChatReactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = DiscordLogger("ChatReactions")

        self.death_emojis = {
            # death messages
            "pricked" : "🌵",
            "cactus" : "🌵",
            "drowned" : "🏊",
            "kinetic" : "🧚",
            "blew up" : "💥",
            "blown up" : "💥",
            "Intentional Game Design" : "🛌",
            "hit the ground" : "⬇️",
            "fell" : "⬇️",
            "fall" : "⬇️",
            "stalagmite" : "🪨",
            "squashed" : "",
            "flames" : "🔥",
            "fire" : "🔥",
            "burned" : "🔥",
            "bang" : "🎆",
            "lava" : "🌋",
            "struck" : "⛈️",
            "danger zone" : "🌋",
            "magic" : "🎩",
            "froze" : "🥶",
            "frozen" : "🥶",
            "slain" : "🩸",
            "stung" : "🐝",
            "shriek" : "🗣",
            "smashed" : "🔨",
            "spear" : "🗡️",
            "shot" : "💘",
            "pummeled" : "💥",
            "fireballed" : "🔥",
            "skull" : "☠️",
            "starved" : "🍗",
            "suffocated" : "🫁",
            "squished" : "🏃‍♂️",
            "confines" : "🌎",
            "poked" : "🔪",
            "hurt" : "🌹",
            "impaled" : "⚔️",
            "world" : "🌎",
            "withered" : "🥀",
            "even more magic" : "🤯",
            # hostile mobs
            "blaze": "❤️‍🔥",
            "bogged": "🐸",
            "breeze": "💨",
            "creeking": "🫀",
            "creeper": "💣",
            "dragon" : "🐉",
            "elder guardian": "💂",
            "endermite": "👾",
            "evoker": "🪄",
            "ghast": "😾",
            "guardian": "🛡️",
            "hoglin": "🐗",
            "husk": "🫔",
            "magma cube": "🟥",
            "phantom": "👻",
            "piglin brute": "💪",
            "pillager": "🏹",
            "ravager": "🐘",
            "shulker": "📦",
            "silverfish": "🪳",
            "skeleton": "💀",
            "slime": "🫟",
            "spider" : "🕷",
            "stray": "❄️",
            "vex": "👻",
            "vindicator": "🧑‍⚖️",
            "warden": "👮",
            "witch": "🧙",
            "wither": "🥀",
            "zoglin": "🧟",
            "zombie": "🧟",
            "zombie villager": "🧟",
        }

    async def cog_load(self):
        self.logger.write("info", "loaded")

    async def cog_unload(self):
        self.logger.write("info", "unloaded")

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            for info in msg.embeds:
                for death, emoji in self.death_emojis.items():
                    if death in info.to_dict()["description"].lower():
                        await msg.add_reaction(emoji)


        if "good bot" in msg.content.lower():
            await msg.add_reaction("🥹")
        elif "bad bot" in msg.content.lower():
            await msg.add_reaction("😟")

async def setup(bot):
    await bot.add_cog(ChatReactions(bot))