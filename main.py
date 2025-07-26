import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

# ================== ENV VARIABLES ==================
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ================== PYROGRAM CLIENT ==================
app = Client(
    "music-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================== PYTGCALLS CLIENT ==================
call_py = PyTgCalls(app)

# ================== SIMPLE COMMAND ==================
@app.on_message(filters.command("start") & filters.private)
async def start(_, message):
    await message.reply("✅ **Music Bot is online and ready to play music!**\nUse `/play <song name>` in a group.")

@app.on_message(filters.command("play") & filters.group)
async def play_song(_, message):
    if len(message.command) < 2:
        return await message.reply("❌ Please give a song name or YouTube URL to play.")
    
    query = " ".join(message.command[1:])
    await message.reply(f"🎶 **Playing:** `{query}`")

    # Download using yt-dlp
    import yt_dlp
    ydl_opts = {"format": "bestaudio", "quiet": True, "outtmpl": "song.%(ext)s"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        file_path = ydl.prepare_filename(info)

    # Join and play audio
    await call_py.join_group_call(
        message.chat.id,
        AudioPiped(file_path)
    )

@app.on_message(filters.command("stop") & filters.group)
async def stop_music(_, message):
    await call_py.leave_group_call(message.chat.id)
    await message.reply("⏹ **Stopped the music.**")

# ================== MAIN ==================
async def main():
    await app.start()
    await call_py.start()
    print("Bot started successfully...")
    await idle()

if __name__ == "__main__":
    from pyrogram import idle
    asyncio.run(main())
