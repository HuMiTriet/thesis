from aiohttp import web
import asyncio


async def handle(request):
    return web.Response(text="Hello, world")


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    web.run_app(app, port=5007)
