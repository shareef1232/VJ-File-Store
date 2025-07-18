# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import sys
import glob
import importlib
import logging
import logging.config
import requests
import threading
import asyncio
from pathlib import Path
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from datetime import date, datetime
import pytz
from aiohttp import web
from typing import Union, Optional, AsyncGenerator

from config import LOG_CHANNEL, ON_HEROKU, CLONE_MODE, PORT
from Script import script
from plugins.clone import restart_bots
from TechVJ.bot import StreamBot
from TechVJ.utils.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients
from TechVJ.server import web_server

# ✅ Logging Configuration
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# ✅ Auto Ping Setup (Every 10 minutes)
def start_auto_ping():
    def ping_loop():
        while True:
            try:
                response = requests.get("https://your-koyeb-or-render-url.com/ping", timeout=10)
                logging.info(f"✅ Auto Ping Success: {response.status_code}")
            except Exception as e:
                logging.warning(f"⚠️ Auto Ping failed: {e}")
            time.sleep(600)  # 10 minutes

    thread = threading.Thread(target=ping_loop, daemon=True)
    thread.start()

# Start Auto Ping
start_auto_ping()

# ✅ Plugin Loading
ppath = "plugins/*.py"
files = glob.glob(ppath)
StreamBot.start()

loop = asyncio.get_event_loop()

async def start():
    print('\nInitalizing Tech VJ Bot')
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username

    await initialize_clients()

    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = f"plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Tech VJ Imported => " + plugin_name)

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    me = await StreamBot.get_me()
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")

    await StreamBot.send_message(
        chat_id=LOG_CHANNEL,
        text=script.RESTART_TXT.format(today, time_str)
    )

    # ✅ Setup Web Server
    app = await web_server()

    async def ping(request):
        return web.Response(text="Pong!")

    app.router.add_get("/ping", ping)
    runner = web.AppRunner(app)
    await runner.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(runner, bind_address, PORT).start()

    # ✅ Clone Mode
    if CLONE_MODE:
        await restart_bots()

    print("Bot Started Powered By @VJ_Botz")
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
