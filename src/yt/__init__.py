from __future__ import print_function

import subprocess
import sys
import urllib

import gdata.youtube
import gdata.youtube.service

yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = True

def play_url(url):
    yt_dl = subprocess.Popen(['youtube-dl', '-g', url], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (url, err) = yt_dl.communicate()
    if yt_dl.returncode != 0:
        sys.stderr.write(err)
        raise RuntimeError('Error getting URL.')
    mplayer = subprocess.Popen(['mplayer', '-quiet', '-fs', '--', url.decode('UTF-8').strip()])
    mplayer.wait()

def print_feed(feed):
    number = 1
    for entry in feed.entry:
        print('%s: %s: %s' % (number, ', '.join([x.name.text for x in entry.author]), entry.media.title.text))
        number += 1

def search(terms):
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = urllib.quote_plus(terms)
    query.orderby = 'relevance'
    return yt_service.YouTubeQuery(query)

def main():
    #feed = yt_service.GetYouTubeVideoFeed('http://gdata.youtube.com/feeds/api/standardfeeds/most_viewed')
    #print_feed(feed)

    if len(sys.argv) < 2:
        print('Need argument')
        sys.exit(1)

    terms = ' '.join(sys.argv[1:])

    feed = search(terms)
    print_feed(feed)

    number = 0
    while number < 1 or number > len(feed.entry):
        number = int(raw_input('Choose 1-%s: ' % (len(feed.entry))))

    entry = feed.entry[number - 1]
    print('Playing entry: %s' % (entry.media.title.text))
    play_url(entry.GetSwfUrl())
