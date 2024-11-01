#!/usr/bin/env python3
import asyncio
import openai
import os
import re
import sys
import telebot
from youtube_transcript_api import YouTubeTranscriptApi

DEFAULT_PROMPT = "Summarize user text in less than 100 words in the text language"

def Transcript(video_id, preferred_languages=None):
        try:
                transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        except:
                return None
        langs = preferred_languages or []
        transcript = None
        try:
                transcript = transcripts.find_manually_created_transcript(langs)
        except:
                try:
                        transcript = transcripts.find_generated_transcript(langs)
                except:
                        pass
        return ' '.join(chunk['text'] for chunk in transcript.fetch()) if transcript else None


def Summarize(text, prompt):
        org, proj, key = [os.environ.get('OPENAI_'+x, None)
                          for x in ('ORGANIZATION', 'PROJECT', 'API_KEY')]
        if not all((org, proj, key)):
            print('OpenAI credentials are not set, skip GenAI summarization step')
            return 'Raw transcript: ' + text

        client = openai.OpenAI(organization=org, project=proj, api_key=key)
        chat_completion = client.chat.completions.create(
                messages=[
                        { 'role': 'system', 'content': prompt, },
                        { 'role': 'user',   'content': text, },
                ],
                model="gpt-4o-mini",
                response_format = { 'type': 'text' },
        )

        return chat_completion.choices[0].message.content


def Handle(text):
        m = re.search('(?:https://)?(?:www.)?(?:youtube.com|youtu.be)/(?:watch\\?v=|shorts/|live/)?([a-zA-Z0-9-]+)', text)
        if m:
                prompt = os.environ.get('PROMPT_YT', DEFAULT_PROMPT).strip()
                print(f"I am in the handler for YouTube clip {m.group(1)}. Summarize using prompt [{prompt}]")
                preferred_languages = os.environ.get('PREFERRED_LANGUAGES', '').split()
                t = Transcript(m.group(1), preferred_languages)
                return Summarize(t, prompt) if t else 'No video transcript'

        return None

bots = []
telegram_bot_id = os.environ.get('TELEGRAM_BOT_ID', None)
if telegram_bot_id:
    print(f'Run Lt Spoiler as a Telegram bot ({telegram_bot_id})')
    from telebot.async_telebot import AsyncTeleBot
    bot = AsyncTeleBot(telegram_bot_id)
    bots.append(bot.infinity_polling())

    @bot.message_handler()
    async def handle_all(message):
            reply = Handle(message.text)
            if reply:
                await bot.reply_to(message, reply)

discord_bot_id = os.environ.get('DISCORD_BOT_ID', None)
if discord_bot_id:
    print(f'Run Lt Spoiler as a Discord bot ({discord_bot_id})')
    import discord
    class MyClient(discord.Client):
            async def on_ready(self):
                    print(f'Logged on as {self.user}, {self.user.mention}!')

            async def on_message(self, message):
                    if message.author != self.user:
                        reply = Handle(message.content)
                        if reply:
                            await message.reply(reply)

    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    bots.append(client.start(discord_bot_id))

if bots:
    async def run():
        await asyncio.gather(*bots)

    asyncio.run(run())
else:
    print('Run Lt Spoiler in command-line mode')
    message = ' '.join(sys.argv[1:])
    if message:
        print(f'User message: [{message}]')
        response = Handle(message)
        print('Response:', response)
    else:
        print(f'Usage: {sys.argv[0]} message')

