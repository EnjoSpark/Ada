import os
import discord
import requests
import json
import random
import translators as ts
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

intents = discord.Intents(messages=True,
                          message_content=True,
                          reactions=True,
                          members=True,
                          guilds=True)
bot = commands.Bot(command_prefix='/', intents=intents)

joke_url = "https://official-joke-api.appspot.com/jokes/random"
quote_url = "https://zenquotes.io/api/random"
# sad_words = ['sad', 'unhappy', 'angry', 'miserable', 'depress', 'hate']
lang_emoji = {
    'zh': {'🇨🇳'},
    'ru': {'🇷🇺', '🇧🇾', '🇰🇬', '🇰🇿'},
    'en': {'🇬🇧', '🇺🇸', '🇦🇺', '🇳🇿', '🇨🇦'},
    'es': {
        '🇪🇸', '🇲🇽', '🇧🇷', '🇨🇱', '🇨🇴', '🇧🇿', '🇨🇷', '🇨🇺', '🇩🇴', '🇪🇨', '🇸🇻', '🇬🇹',
        '🇭🇳', '🇦🇷', '🇧🇴', '🇵🇪', '🇵🇾', '🇺🇾', '🇻🇪'
    },
    'ja': {'🇯🇵'},
    'ko': {'🇰🇷', '🇰🇵'},
    'fr': {'🇫🇷'},
    'de': {'🇩🇪'}
}

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def joke(ctx):
    await ctx.send(get_joke())


@bot.command()
async def inspire(ctx):
    await ctx.send(get_quote())


@bot.command()
async def translate(ctx, emoji, *, words):
    lang = get_emoji_lang(emoji)
    if not lang:
        return
    translated = ts.google(words, to_language=lang)
    pm = f'"{words}"\n{translated} ({emoji})'
    await ctx.author.send(pm)


# @bot.listen('on_message')
# async def console(msg):
#     if msg.author == bot.user:
#         return

#     if any(word in msg.content for word in sad_words):
#         choice = random.choice((0, 1))

#         if choice == 0:
#             reply = get_quote()
#         else:
#             reply = get_joke()
#         await msg.channel.send(reply)


@bot.listen('on_raw_reaction_add')
async def translate_if_flag(payload):
    emoji = payload.emoji.name
    lang = get_emoji_lang(emoji)
    if not lang:
        return
    channel = await bot.fetch_channel(payload.channel_id)
    if not channel:
        print('Channel is none!')
        return
    message = await channel.fetch_message(payload.message_id)
    member = payload.member
    if not (message and member):
        print('Missing info.')
        return
    translated = ts.google(message.content, to_language=lang)
    pm = f'"{message.content}"\n{translated} ({emoji})'
    await member.send(pm)


def get_emoji_lang(emoji):
    for k, v in lang_emoji.items():
        if emoji in v:
            return k
    return None


def get_joke():
    response = requests.get(joke_url)
    json_data = json.loads(response.text)
    joke = json_data['setup'] + " " + json_data['punchline']
    return joke


def get_quote():
    response = requests.get(quote_url)
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " --" + json_data[0]['a']
    return quote


bot.run(os.environ['TOKEN'])
