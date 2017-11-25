import discord
import os
import time
from discord.ext.commands import Bot
from discord.ext import commands
from gtts import gTTS
from config import token


class VoiceState:
    def __init__(self, bot):
        self.voice = None
        # self.current = None
        self.bot = bot
        self.player = None

    def is_playing(self):
        if self.voice is None:
            return False

        return not self.player.is_done()


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state
        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    @commands.command(pass_context=True)
    async def join(self, ctx):
        """Joins a voice channel"""
        channel = ctx.message.author.voice.voice_channel
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Problem')

    @commands.command(pass_context=True)
    async def play(self, ctx, url: str):
        """Plays a song"""
        state = self.get_voice_state(ctx.message.server)

        try:
            if state.player is not None:
                state.player.stop()
            state.player = await state.voice.create_ytdl_player(url)
        except Exception as e:
            await self.bot.send_message('error ' + str(e) + ' occurred')
        else:
            state.player.volume = 0.6
            state.player.start()

    @commands.command(pass_context=True)
    async def pause(self, ctx):
        """Pauses the song/video"""

        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            state.player.pause()

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        """Resumes the song/video"""

        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            state.player.resume()

    @commands.command(pass_context=True)
    async def say(self, ctx, text: str):
        """Says something"""

        server = ctx.message.server
        state = self.get_voice_state(server)
        voice = state.voice
        # bot creates text
        tts = gTTS(text=text, lang='es')
        tts.save('say.mp3')

        # wait until the file exists
        while not os.path.exists('say.mp3'):
            time.sleep(1)

        # the bot says the text
        if state.player is not None:
            state.player.pause()
        player = voice.create_ffmpeg_player('say.mp3')
        player.start()


client = Bot(description='Simple Bot', command_prefix='!')
client.add_cog(Music(client))


@client.event
async def on_ready():
    print('Logged in!')


# Need to change token
client.run(token, bot=False)

