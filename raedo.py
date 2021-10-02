import discord  #interact with discord
import youtube_dl   # download youtbe videos via url
import os
import queue
import time
import asyncio
from youtube_search import YoutubeSearch # obtain a youtube video url via a query
import validators # to validate if a string is a url
import json
import urllib
import urllib.request


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
    """
    Recursive function to play the next song in queue.
    """
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
            #extract name of song. credits to porto on https://stackoverflow.com/questions/1216029/get-title-from-youtube-videos
            params = {"format": "json", "url": url}
            name_search_url = "https://www.youtube.com/oembed"
            query_string = urllib.parse.urlencode(params)
            name_search_url = name_search_url + "?" + query_string

            with urllib.request.urlopen(name_search_url) as response:
                response_text = response.read()
                data = json.loads(response_text.decode())
                songname = data['title']

        #find file in running location that just got downloaded and get its name
        for f in os.listdir('.'):
            if f.endswith(('mp3', 'wav', 'flac', 'aac')):
                #rename so that only only file is in directory at a time. this overwrites previous file
                os.rename(f, "song.mp3")
        
        #play the song
        msg = '[ PLAY ] Hey-oh, you know how we play the hits on raEDO, so check this:\n {}!'.format(songname)
        asyncio.run_coroutine_threadsafe(message_channel.send(msg), client.loop)
        source = discord.FFmpegPCMAudio("song.mp3")
        v_client.play(source, after=play_next)
    else:
        print("\n[ LEAVE ] BOT WILL LEAVE CURRENT VOICE CHANNEL IN 2.5 MINS!\n")
        #wait 2.5 mins until bot disconnects
        leave = True
        time.sleep(150)
        leave_voice_channel()


def leave_voice_channel():
    """
    Handles the leaving from voice channel activity caused by inactivity of the bot.
    """
    if leave:
        v_client = client.voice_clients[0]
        msg = '[ LEAVE ] I\'m leaving cause yall ain\'t listening to nothing. Keep it cool my brothas!'
        asyncio.run_coroutine_threadsafe(message_channel.send(msg), client.loop)
        asyncio.run_coroutine_threadsafe(v_client.disconnect(), client.loop)


def parse_play_message(msg):
    """
    Parses a play message. It looks for either a url or a query to make a search on youtube and produce a url.

    Inputs: msg - the play message to be parsed;
    Outputs:  url - the url of the song to be played;
    """
    url = None
    #first isolate the actual message from the command
    content = msg.split(" ", 1)[1]
    if validators.url(content):
        # in case of being an url just return it
        return content
    else:
        search_res = YoutubeSearch(content, max_results=1).to_json()
        try:
            # if it's not a url, we assume it is a query and make a search on youtube
            # credits to Pedro Lobito on https://stackoverflow.com/questions/60489888/how-to-use-a-key-words-instead-of-a-url-with-youtube-dl-and-discord-py
            yt_id = str(json.loads(search_res)['videos'][0]['id'])
            yt_url = 'https://www.youtube.com/watch?v='+yt_id
            url = 'https://www.youtube.com/watch?v='+yt_id
            return url
        except:
            pass
    return url


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
        url = parse_play_message(message.content)
        if not url:
            msg = '[ SEARCH ] I couldn\'t find your song my man. Maybe try again with some other words. Or use a link.'
            await message.channel.send(msg)
            return

        leave = False
        print("\nBOT WILL NO LONGER LEAVE, IN CASE IT WERE, BECAUSE A NEW SONG CAME IN.\n")

        #check wether song should be played or placed in queue
        if v_client.is_playing():
            song_queue.put(url)
            await message.channel.send('[ QUEUE ] Check it bruh, some other vibe playing right now, so that gonna hold on on queue for a sec. Respec be the main deal, here, on raEDO.')
        else:
            #in windows rewriting over previous file doesnt work. so we delete the previous file before downloading
            if os.path.isfile("song.mp3"):
                os.remove("song.mp3")

            #download song with youtube_dl
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                #extract name of song. credits to porto on https://stackoverflow.com/questions/1216029/get-title-from-youtube-videos
                params = {"format": "json", "url": url}
                name_search_url = "https://www.youtube.com/oembed"
                query_string = urllib.parse.urlencode(params)
                name_search_url = name_search_url + "?" + query_string

                with urllib.request.urlopen(name_search_url) as response:
                    response_text = response.read()
                    data = json.loads(response_text.decode())
                    songname = data['title']

            #find file in running location that just got downloaded and get its name
            for f in os.listdir('.'):
                if f.endswith(('mp3', 'wav', 'flac', 'aac')):
                    #rename so that only only file is in directory at a time. this overwrites previous file
                    os.rename(f, "song.mp3")
            
            await message.channel.send('[ PLAY ] Hey-oh, you know how we play the hits on raEDO, so check this:\n {}!'.format(songname))

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