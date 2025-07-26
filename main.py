import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputAudioStream
from yt_dlp import YoutubeDL
from pymongo import MongoClient

# Env variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "ffmpeg")

# Setup MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["musicbot"]
history_col = db["history"]

# Pyrogram client
app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# PyTgCalls
pytgcalls = PyTgCalls(app)

# YT-DLP options
ydl_opts = {
    'format': 'bestaudio',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': False
}

async def download_audio(url):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['url'], info.get('title', 'Unknown')

@pytgcalls.on_stream_end()
async def on_end(_, update: Update):
    chat_id = update.chat_id
    await pytgcalls.leave_group_call(chat_id)

@app.on_message(filters.command("play") & filters.group)
async def play_music(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /play <song name or YouTube URL>")
    query = " ".join(message.command[1:])
    await message.reply_text("Searching...")

    # Download audio URL
    url, title = await download_audio(query)
    await pytgcalls.join_group_call(
        message.chat.id,
        InputAudioStream(url)
    )
    history_col.insert_one({"chat_id": message.chat.id, "title": title})
    await message.reply_text(f"🎶 Playing **{title}**")

@app.on_message(filters.command("stop") & filters.group)
async def stop_music(_, message):
    await pytgcalls.leave_group_call(message.chat.id)
    await message.reply_text("⏹ Stopped")

@app.on_message(filters.command("history") & filters.group)
async def history(_, message):
    songs = list(history_col.find({"chat_id": message.chat.id}))
    if not songs:
        return await message.reply_text("No songs played yet.")
    text = "Last Songs:\n" + "\n".join([s['title'] for s in songs[-10:]])
    await message.reply_text(text)

async def main():
    await app.start()
    await pytgcalls.start()
    print("Bot is running...")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
