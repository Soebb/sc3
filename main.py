#_*_coding: utf-8_*_

import asyncio
import os, unittest, time, datetime
import urllib.request, urllib.error, urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.options import Options
from pyrogram import Client, filters
from youtube_dl import YoutubeDL

API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = Client('bot',
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN,
             workers=50,
             sleep_threshold=10)


@bot.on_message(filters.command('start') & filters.private)
async def start(bot, message):
    await message.reply(
        f"**Hi {message.chat.first_name}!**\n\n"
        "I am a bot to scrape youtube channel videos urls, just send me a youtube channel link to start scraping")

@bot.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def link_handler(bot, message):
    if not "channel" in message.text:
        await message.reply("Send me a youtube channel link")
    if "channel" in message.text:
        url = f"{message.text}"
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=chrome-data")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        driver.get(url)
        time.sleep(5)
        dt=datetime.datetime.now().strftime("%Y%m%d%H%M")
        height = driver.execute_script("return document.documentElement.scrollHeight")
        lastheight = 0

        while True:
            if lastheight == height:
                break
            lastheight = height
            driver.execute_script("window.scrollTo(0, " + str(height) + ");")
            time.sleep(2)
            height = driver.execute_script("return document.documentElement.scrollHeight")

        user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')
        for i in user_data:
            result = i.get_attribute('href')
        dl = result
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'noplaylist': False,
            'outtmpl': '%(title)s.%(ext)s'
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(dl, download=False)
            ydl.process_info(info_dict)
            video_file = ydl.prepare_filename(info_dict)
            await message.reply_video(video_file)


bot.run()
