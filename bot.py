import logging
import os
import re
from datetime import datetime

import discord
from discord.ext import tasks
from dotenv import load_dotenv

from components import mabi, er

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

    er.on_ready()

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
    
        file = discord.File('img/mabi_logo_2.png', filename='mabi_logo.png') 

        # embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar)
        embed.set_author(name="마비노기 경매장 검색", icon_url="attachment://mabi_logo.png")

        # Error handling
        if item_price.get("status_code") != 200:

            embed.add_field(name="ERROR!", value=item_price.get("errorCode"), inline=False)
            embed.add_field(name = chr(173), value = "") # Add a blank field
        
            embed.set_footer(text="Data based on NEXON Open API")
            
            await message.channel.send(file=file, embed=embed, reference=message.reference, mention_author=False, delete_after=5)

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

    # 판매시 수수료 쿠폰 이득 구간 !coupon <아이템 이름>
    if message.content.startswith("!coupon"):
        item = message.content.split(" ", 1)[1]
        if item == "":
            await message.channel.send("아이템 이름을 입력해주세요.")

        await message.delete()

        file = discord.File('img/mabi_logo_2.png', filename='mabi_logo.png') 

        embed = discord.Embed(
            color = message.author.color if message.author.color != discord.Colour.default() else discord.Colour.greyple()
        )

        # embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar)
        embed.set_author(name="마비노기 수수료 계산기", icon_url="attachment://mabi_logo.png")

        loading_msg = await message.channel.send(f"{item}을(를) 검색하는중...")

        await loading_msg.delete()

        item_price = mabi.getItemPrice(item)

        # Error handling
        if item_price.get("status_code") != 200:

            embed.add_field(name="ERROR!", value=item_price.get("errorCode"), inline=False)
            embed.add_field(name = chr(173), value = "") # Add a blank field
        
            embed.set_footer(text="Data based on NEXON Open API")
            
            await message.channel.send(file=file, embed=embed, reference=message.reference, mention_author=False, delete_after=5)

            return
        
        discount_per = mabi.getItemCharge(item_price.get("price"))

        # 제일 이득인 쿠폰
        #coupon_result = max(list(discount_per.items()), key=lambda v: v[1])

        embed.add_field(name="아이템", value=item, inline=False)
        embed.add_field(name="가격", value=item_price.get("price") + " 골드", inline=False)

        embed.add_field(name = chr(173), value = "")

        embed.add_field(name = "프리미엄 플러스 팩 사용", value = "", inline=False)
        embed.add_field(name="쿠폰 미사용", value=discount_per.get("premium").get("no_coupon") + " 골드", inline=True)
        embed.add_field(name="10% 할인 쿠폰", value=discount_per.get("premium").get("10") + " 골드", inline=True)
        embed.add_field(name="20% 할인 쿠폰", value=discount_per.get("premium").get("20") + " 골드", inline=True)
        embed.add_field(name="30% 할인 쿠폰", value=discount_per.get("premium").get("30") + " 골드", inline=True)
        embed.add_field(name="50% 할인 쿠폰", value=discount_per.get("premium").get("50") + " 골드", inline=True)
        embed.add_field(name="100% 할인 쿠폰", value=discount_per.get("premium").get("100") + " 골드", inline=True)
        embed.add_field(name = chr(173), value = "")
        
        embed.add_field(name = "프리미엄 플러스 팩 미사용", value = "", inline=False)
        embed.add_field(name="쿠폰 미사용", value=discount_per.get("basic").get("no_coupon") + " 골드", inline=True)
        embed.add_field(name="10% 할인 쿠폰", value=discount_per.get("basic").get("10") + " 골드", inline=True)
        embed.add_field(name="20% 할인 쿠폰", value=discount_per.get("basic").get("20") + " 골드", inline=True)
        embed.add_field(name="30% 할인 쿠폰", value=discount_per.get("basic").get("30") + " 골드", inline=True)
        embed.add_field(name="50% 할인 쿠폰", value=discount_per.get("basic").get("50") + " 골드", inline=True)
        embed.add_field(name="100% 할인 쿠폰", value=discount_per.get("basic").get("100") + " 골드", inline=True)
        embed.add_field(name = chr(173), value = "")
        
        embed.set_footer(text="Data based on NEXON Open API")
        
        await message.channel.send(file=file, embed=embed, reference=message.reference, mention_author=False)

    # 이터리 로테이션
    if message.content.startswith("!rotation"):

        await message.delete()

        loading_msg = await message.channel.send("로테이션을 검색하는중...")

        await loading_msg.delete()

        data = er.freeCharacters()

        file = discord.File('img/er_logo.jpg', filename='er_logo.jpg') 

        embed = discord.Embed(
            color = message.author.color if message.author.color != discord.Colour.default() else discord.Colour.greyple()
        )

        embed.set_author(name="이터널리턴 로테이션", icon_url="attachment://er_logo.jpg")

        for item in data:
            embed.add_field(name=item, value="", inline=True)

        embed.add_field(name = chr(173), value = "")

        embed.set_footer(text="Data based on Nimble Neuron Open API")
        
        await message.channel.send(file=file, embed=embed, reference=message.reference, mention_author=False)



client.run(os.getenv("DISCORD_TOKEN"))