from dotenv import dotenv_values
from utils.logger import DiscordLogger
import os
import aiohttp


# Need to rewrite to use the same session instead of creating new ones
class WordPressAPI:
    def __init__(self):
        self.logger = DiscordLogger("WordPress")
        config = dotenv_values(os.path.join("configs", "wordpress.env"))

        if None in config:
            self.logger.write("critical", "wordpress.env is None!")

        self.storage_dir = os.path.join("..", "logs")

        self.url = config.get("wordpress_url")
        self.user = config.get("wordpress_user")
        self.password = config.get("wordpress_app_password")
        self.auth = aiohttp.BasicAuth(self.user, self.password)

    async def get_id_by_slug(self, slug):
        data = {"slug": slug}

        async with aiohttp.ClientSession(auth=self.auth) as session:
            response = await session.get(self.url + "wp-json/wp/v2/pages", json=data)
            json = await response.json()
            return json[0]["id"]

    async def get_page(self, page_id):
        async with aiohttp.ClientSession(auth=self.auth) as session:
            response = await session.get(self.url + f"wp-json/wp/v2/pages/{page_id}")
            return await response.json()

    async def create_page(self, title, content, **kwargs):
        data = {"title": title, "content": content}
        data.update(kwargs)

        async with aiohttp.ClientSession(auth=self.auth) as session:
            response = await session.post(self.url + "wp-json/wp/v2/pages", json=data)
            return response.status

    async def update_page(self, page_id, title, content, **kwargs):
        data = {"title": title, "content": content}
        data.update(kwargs)

        async with aiohttp.ClientSession(auth=self.auth) as session:
            response = await session.post(self.url + f"wp-json/wp/v2/pages/{page_id}", json=data)
            return response.status

    async def store_request(self, page_id, title, content, filename, **kwargs):
        data_request = {
            "page_id": page_id,
            "title": title,
            "content": content,
        }
        data_request.update(kwargs)

        with open(os.path.join(self.storage_dir, filename), "w", encoding="utf-8") as file:
            file.write(str(data_request))
