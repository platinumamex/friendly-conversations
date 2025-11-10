import os
import asyncio
import random
from datetime import datetime, timezone
from dotenv import load_dotenv
import discord

load_dotenv()

TOKEN_A = os.getenv("TOKEN_A")
TOKEN_B = os.getenv("TOKEN_B")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# Timing controls (tweak as you like)
MIN_DELAY_SEC = int(os.getenv("MIN_DELAY_SEC", "45"))     # minimum pause between messages
MAX_DELAY_SEC = int(os.getenv("MAX_DELAY_SEC", "180"))    # maximum pause between messages
BURST_CHANCE = float(os.getenv("BURST_CHANCE", "0.15"))   # chance of a quick follow-up
BURST_MIN = int(os.getenv("BURST_MIN", "8"))
BURST_MAX = int(os.getenv("BURST_MAX", "20"))

# Optional quiet hours (UTC) to avoid constant night spam
QUIET_START = os.getenv("QUIET_START_UTC")  # e.g., "06" for 06:00
QUIET_END = os.getenv("QUIET_END_UTC")      # e.g., "08" for 08:00

from dialogue import make_message

intents = discord.Intents.none()
intents.guilds = True
intents.messages = True
intents.message_content = False  # we don't read content

bot_a = discord.Client(intents=intents)
bot_b = discord.Client(intents=intents)

# Shared state
last_msg = None
ready_event = asyncio.Event()

async def wait_for_ready():
    await ready_event.wait()

def in_quiet_hours():
    if QUIET_START is None or QUIET_END is None:
        return False
    now = datetime.now(timezone.utc).hour
    start = int(QUIET_START)
    end = int(QUIET_END)
    if start == end:
        return False
    if start < end:
        return start <= now < end
    return now >= start or now < end

async def chatter_loop():
    await wait_for_ready()
    channel = bot_a.get_channel(CHANNEL_ID) or bot_b.get_channel(CHANNEL_ID)
    if channel is None:
        print("Invalid CHANNEL_ID or bots lack access.")
        return

    speaker = "A"
    global last_msg

    while True:
        # Optional quiet period
        if in_quiet_hours():
            await asyncio.sleep(300)
            continue

        # Main delay
        delay = random.randint(MIN_DELAY_SEC, MAX_DELAY_SEC)
        await asyncio.sleep(delay)

        # Compose
        msg = make_message(speaker, last_msg=last_msg)
        try:
            if speaker == "A":
                await channel.send(msg)
            else:
                await channel.send(msg)
        except Exception as e:
            print(f"Send error: {e}")

        last_msg = msg

        # Occasional quick follow-up (“burst”) by the other speaker
        if random.random() < BURST_CHANCE:
            await asyncio.sleep(random.randint(BURST_MIN, BURST_MAX))
            speaker = "B" if speaker == "A" else "A"
            burst_msg = make_message(speaker, last_msg=last_msg)
            try:
                await channel.send(burst_msg)
                last_msg = burst_msg
            except Exception as e:
                print(f"Burst send error: {e}")

        # Switch turn
        speaker = "B" if speaker == "A" else "A"

@bot_a.event
async def on_ready():
    print(f"Bot A ready as {bot_a.user}")
    if bot_b.is_ready():
        ready_event.set()

@bot_b.event
async def on_ready():
    print(f"Bot B ready as {bot_b.user}")
    if bot_a.is_ready():
        ready_event.set()

async def main():
    # Login both bots concurrently
    await asyncio.gather(
        bot_a.start(TOKEN_A),
        bot_b.start(TOKEN_B),
    )

if __name__ == "__main__":
    # Kick off background chatter after both are ready
    async def runner():
        asyncio.create_task(chatter_loop())
        await main()
    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        pass
