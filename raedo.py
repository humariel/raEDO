import discord
import youtube_dl
import os
import queue
import time
import asyncio

client = discord.Client()
song_queue = queue.Queue()

ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }

def play_next(error):
    global message_channel
    global leave

    if not song_queue.empty():
        url = song_queue.get()
        v_client = client.voice_clients[0]

        #in windows rewriting over previous file doesnt work. so we delete the previous file before downloading
        if os.path.isfile("song.mp3"):
            os.remove("song.mp3")

        #download song with youtube_dl
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        #find file in running location that just got downloaded and get its name
        for f in os.listdir('.'):
            if f.endswith(('mp3', 'wav', 'flac', 'aac')):
                #rename so that only only file is in directory at a time. this overwrites previous file
                os.rename(f, "song.mp3")
        
        #play the song
        msg = '[PLAY]Hey-oh, you know how we play the hits on raEDO, so check this one out!'
        asyncio.run_coroutine_threadsafe(message_channel.send(msg), client.loop)
        source = discord.FFmpegPCMAudio("song.mp3")
        v_client.play(source, after=play_next)
    else:
        print("\nBOT WILL LEAVE CURRENT VOICE CHANNEL IN 5 MINS!\n")
        #wait 2.5 mins until bot disconnects
        leave = True
        time.sleep(150)
        leave_voice_channel()


def leave_voice_channel():
    if leave:
        v_client = client.voice_clients[0]
        msg = '[LEAVE]I\'m leaving cause yall ain\'t listening to nothing. Keep it cool my brothas!'
        asyncio.run_coroutine_threadsafe(message_channel.send(msg), client.loop)
        asyncio.run_coroutine_threadsafe(v_client.disconnect(), client.loop)

@client.event
async def on_ready():
    print('raEDO is ready!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #-----------------------------------PLAY-----------------------------------------------#
    if message.content.startswith(('-play', '-p', '!play', '!p')):
        global message_channel
        global leave

        message_channel = message.channel

        #find author's voice channel and connect to it
        author = message.author
        if author.voice == None:
            await message.channel.send('Yoh dog, connect to a voice channel for me to play your vibe. Peace!')
            return

        #check if bot is already on a voice_channel
        if len(client.voice_clients) == 0:
            #if not on any coice channel connect to the one where author is
            v_channel = author.voice.channel
            v_client = await v_channel.connect()
        else:
            v_client = client.voice_clients[0]

        #get music url
        if len(message.content.split(" ")) < 2:
            await message.channel.send('[HELP]Not the way to ask for a song, bro. Try -p <link on youtube>. Got you!')
            return
        url = message.content.split(" ")[1]

        leave = False
        print("\nBOT WILL NO LONGER LEAVE, IN CASE IT WERE, BECAUSE A NEW SONG CAME IN.\n")

        #check wether song should be played or placed in queue
        if v_client.is_playing():
            song_queue.put(url)
            await message.channel.send('[QUEUE]Check it bruh, some other vibe playing right now, so that gonna hold on on queue for a sec. Respec be the main deal, here, on raEDO.')
        else:
            await message.channel.send('[PLAY]Hey-oh, you know how we play the hits on raEDO, so check this one out!')

            #in windows rewriting over previous file doesnt work. so we delete the previous file before downloading
            if os.path.isfile("song.mp3"):
                os.remove("song.mp3")

            #download song with youtube_dl
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            #find file in running location that just got downloaded and get its name
            for f in os.listdir('.'):
                if f.endswith(('mp3', 'wav', 'flac', 'aac')):
                    #rename so that only only file is in directory at a time. this overwrites previous file
                    os.rename(f, "song.mp3")
            
            #play the song
            source = discord.FFmpegPCMAudio("song.mp3")
            v_client.play(source, after=play_next)
    #-----------------------------------PLAY-----------------------------------------------#

    #-----------------------------------RESUME---------------------------------------------#
    #-----------------------------------RESUME---------------------------------------------#

    #-----------------------------------STOP-----------------------------------------------#
    #-----------------------------------STOP-----------------------------------------------#

    #-----------------------------------LEAVE----------------------------------------------#
    #-----------------------------------LEAVE----------------------------------------------#

    #-----------------------------------HELP-----------------------------------------------#
    #-----------------------------------HELP-----------------------------------------------#



with open('token.txt', "r") as f:
    token = f.read()

client.run(token)