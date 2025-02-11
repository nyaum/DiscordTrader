import logging
import os
import re
from datetime import datetime

import discord
from discord.ext import tasks
from dotenv import load_dotenv

import mabi

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(command_prefix='!',intents=intents)

now = datetime.now()

SINGLE_EMOJI_REGEX = re.compile(
    r"""
    ^               # Start of string
    (?!<.*<)        # Negative lookahead to ensure there is not more than one '<' at the beginning
    <               # Emoji opening delimiter
    (a)?            # Optional 'a' for animated emoji
    :               # Colon delimiter
    (.+?)           # Emoji name
    :               # Colon delimiter
    ([0-9]{15,21})  # Emoji ID
    >               # Emoji closing delimiter
    $               # End of string
    """,
    re.VERBOSE,
)

@tasks.loop(minutes=1.0)
async def change_status():
    await client.change_presence(activity=discord.Game(name=f"{len(client.guilds)}개의 서버와 함께"))

@client.event
async def on_ready():
    change_status.start()
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message: discord.Message):

    if not message.guild or message.author.bot:
        return

    # 이모지를 업로드하면 이모지를 업로드한 사람의 이름과 이모지를 확대해서 보여줌
    if (m := SINGLE_EMOJI_REGEX.match(message.content)):
        embed = discord.Embed(
            color = message.author.color if message.author.color != discord.Colour.default() else discord.Colour.greyple()
        )
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar)
        emoji_id = m.group(3)
        extension = ".gif" if m.group(1) else ".png"
        embed.set_image(url=f"https://cdn.discordapp.com/emojis/{emoji_id}{extension}")

        try:
            await message.delete()
            await message.channel.send(embed=embed, reference=message.reference, mention_author=False)
        except discord.Forbidden:
            pass
        except Exception as e:
            logging.exception(e)

    # 도움말
    if message.content == "!help":
        await message.channel.send("```!help : 도움말\n!mt <아이템 이름> : 경매장 아이템 검색```")
    
    # start region Mabinogi

    # 아이템 가격 검색 (마비노기 : !mt <아이템 이름>)
    if message.content.startswith("!mt"):

        item = message.content.split(" ", 1)[1]

        if item == "":
            await message.channel.send("아이템 이름을 입력해주세요.")

        await message.delete()

        loading_msg = await message.channel.send(f"{item}을(를) 검색하는중...")

        item_price = mabi.getItemPrice(item)

        await loading_msg.delete()  

        embed = discord.Embed(
            color = message.author.color if message.author.color != discord.Colour.default() else discord.Colour.greyple()
        )
    
        file = discord.File('img/mabi_logo.png', filename='mabi_logo.png') 

        # embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar)
        embed.set_author(name="마비노기 경매장 검색", icon_url="attachment://mabi_logo.png")

        # Error handling
        if item_price.get("status_code") != 200:

            embed.add_field(name="ERROR!", value=item_price.get("errorCode"), inline=False)
            embed.add_field(name = chr(173), value = "") # Add a blank field
        
            embed.set_footer(text="Data based on NEXON Open API")
            
            await message.channel.send(file=file, embed=embed, reference=message.reference, mention_author=False)

            return

        # Parse and format the expiration date
        expire_date = datetime.fromisoformat(item_price.get("expire").replace("Z", "+00:00"))
        diff = expire_date.strftime("%Y-%m-%d %H:%M:%S")

        embed.add_field(name="아이템", value=item_price.get("item"), inline=False)
        embed.add_field(name="가격", value=item_price.get("price") + " 골드", inline=False)
        embed.add_field(name="만료일", value=diff, inline=False)
        embed.add_field(name = chr(173), value = "") # Add a blank field
        
        embed.set_footer(text="Data based on NEXON Open API")
        
        await message.channel.send(file=file, embed=embed, reference=message.reference, mention_author=False)

    # end region Mabinogi

    # start region EternalReturn

    if message.content.startswith("!er"):
        print("rank")

    # end region EternalReturn

client.run(os.getenv("DISCORD_TOKEN"))