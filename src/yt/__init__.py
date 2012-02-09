from __future__ import print_function

import curses
import curses.textpad
import curses.wrapper
import json
import locale
import re
import subprocess
import sys
import urllib
import urllib2

def main():
    ui = Ui()
    ui.run()

class ScreenSizeError(Exception):
    def __init__(self, m = 'Terminal too small to continue'):
        self.message = str(m)

    def __str__(self):
        return m

class Ui(object):
    def __init__(self):
        # A cache of the last feed result
        self._last_feed = None

        # The ordering
        self._ordering = 'relevance'

        # Specify the current feed
        if len(sys.argv) > 1:
            self._feed = search(' '.join(sys.argv[1:]))
        else:
            self._feed = standard_feed('most_viewed')

        # The items to display in the pager
        self._items = None

        # A mapping between ordering name and human-name
        self._ordering_names = {
            'relevance': 'relvance',
            'viewCount': 'view count',
            'published': 'publication date',
            'rating': 'rating',
        }

    def run(self):
        # Get the locale encoding
        locale.setlocale(locale.LC_ALL, '')
        self._code = locale.getpreferredencoding()
        
        # Start the curses main loop
        curses.wrapper(self._curses_main)

    def _curses_main(self, scr):
        curses.noecho()
        self._screen = scr
        self._screen.keypad(1)

        # Check the screen size
        (h, w) = self._screen.getmaxyx()
        if h < 1:
            raise ScreenSizeError()

        # Initialise the display
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        # Set attributes
        self._title_attr = curses.color_pair(1)
        self._uploader_attr = curses.color_pair(6)
        self._bar_attr = curses.color_pair(5)

        self._status = ''
        self._help = [
                ('[/]', 'prev/next'),
                ('o', 'ordering'),
                ('s', 'search'),
                ('1-9', 'choose'),
                ('v', 'choose index'),
                ('u', 'user'),
        ]

        # Create the windows
        self._main_win = curses.newwin(h-1,w,1,0)
        self._status_bar = curses.newwin(1,w,0,0)
        self._status_bar.bkgd(' ', curses.color_pair(5))
        self._help_bar = curses.newwin(1,w,h-1,0)
        self._help_bar.bkgd(' ', self._bar_attr)

        self._update_screen()
        self._run_pager()

    def _reposition_windows(self):
        (h, w) = self._screen.getmaxyx()
        if h < 3:
            raise ScreenSizeError()

        self._main_win.resize(h-1, w)
        self._status_bar.resize(1, w)
        self._help_bar.resize(1, w)
        self._help_bar.mvwin(h-1, 0)

    def _input(self, prompt):
        (h, w) = self._screen.getmaxyx()
        if w < len(prompt) + 2:
            raise ScreenSizeError()

        self._help_bar.erase()
        self._help_bar.addstr(0, 0, ('%s:' % (prompt,)).encode(self._code))
        self._help_bar.refresh()
        input_win = curses.newwin(1, w-len(prompt)-2, h-1, len(prompt)+2)
        input_win.bkgd(' ', self._bar_attr)
        curses.curs_set(1)
        curses.echo()
        try:
            s = input_win.getstr(0,0)
        except KeyboardInterrupt:
            s = None
        curses.noecho()
        curses.curs_set(0)
        return s

    def _get_feed(self, start, count):
        count = min(count, 25) # 25 is the max number of results we can get in one go
        start += 1 # FSR, Google decides to 1-index this

        if self._last_feed is not None and 'data' in self._last_feed \
            and int(self._last_feed['data']['itemsPerPage']) >= count \
            and int(self._last_feed['data']['startIndex']) == start:
                return self._last_feed
        self._show_message(u'Talking to YouTube\u2026')
        self._last_feed = self._feed['fetch_cb'](start, count, self._ordering)
        return self._last_feed

    def _update_screen(self):
        self._reposition_windows()
        (h, w) = self._main_win.getmaxyx()

        # Show the items in the window
        self._main_win.erase()
        if self._items is not None and len(self._items) > 0:
            self._show_video_items(self._items)
        self._main_win.refresh()

        # Update the help bar
        self._help_bar.erase()
        if w > 2:
            self._add_table_row(self._help, 0, 0, w-1, self._bar_attr, max_width=16, win=self._help_bar)
        self._help_bar.refresh()

        # Update the status bar
        self._status_bar.erase()
        if w > 2:
            self._status_bar.addstr(0, 0, truncate(self._status, w-1).encode(self._code))
        self._status_bar.refresh()

    def _run_pager(self):
        idx = 0
        while True:
            # Get size of window and => number of items/page
            (h, w) = self._main_win.getmaxyx()
            n_per_page = h // 3

            # Get the items for the current page
            feed = self._get_feed(idx, n_per_page)
            self._items = None
            if feed is not None and 'data' in feed and 'items' in feed['data']:
                feed = self._get_feed(idx, n_per_page)
                self._items = feed['data']['items']
                if len(self._items) > n_per_page:
                    self._items = self._items[:n_per_page]

            if self._items is not None:
                self._status = 'Showing %i-%i of %s' % (idx+1, idx+len(self._items), self._feed['description'])
            else:
                self._status = 'No results for %s' % (self._feed['description'],)

            if self._ordering in self._ordering_names:
                self._status += ' ordered by ' + self._ordering_names[self._ordering]

            # Update the screen with the new items
            self._update_screen()

            c = self._main_win.getch()
            if c == ord('q'): # quit
                break
            elif c == ord(']'): # next
                # have we had all the items?
                if not 'data' in self._last_feed or not 'totalItems' in self._last_feed['data'] or len(self._items) + idx < self._last_feed['data']['totalItems']:
                    idx += n_per_page
            elif c == ord('['): # previous
                if idx > n_per_page:
                    idx -= n_per_page
                else:
                    idx = 0
            elif c == ord('s'): # search
                s = self._input('search')
                if s is not None and len(s) > 0:
                    self._feed = search(s)
                    self._last_feed = None
                    self._ordering = 'relevance'
                    idx = 0
            elif c == ord('v'): # video
                s = self._input('number')
                if s is not None:
                    try:
                        self._play_video(int(s) - 1)
                    except ValueError:
                        pass
            elif c == ord('u'): # user
                s = self._input('user')
                if s is not None:
                    self._feed = user(s)
                    self._last_feed = None
                    self._ordering = 'published'
                    idx = 0
            elif c >= ord('1') and c <= ord('9'): # specific video
                self._play_video(c - ord('1'))
            elif c == ord('o'): # ordering
                self._show_message('Order by: (v)iew count, (r)elevance, (p)ublication date or ra(t)ing?')
                oc = self._main_win.getch()
                self._ordering = None
                
                while self._ordering is None:
                    if oc == ord('r'):
                        self._ordering = 'relevance'
                    elif oc == ord('v'):
                        self._ordering = 'viewCount'
                    elif oc == ord('p'):
                        self._ordering = 'published'
                    elif oc == ord('t'):
                        self._ordering = 'rating'

                self._last_feed = None
                idx = 0


    def _play_video(self, idx):
        # idx is 0-based(!)
        if self._items is None or idx < 0 or idx >= len(self._items):
            return
        item = self._items[idx]
        url = item['player']['default']
        self._show_message('Playing ' + url)
        play_url(url)

    def _show_video_items(self, items):
        # Get size of window and maximum number of items per page
        (h, w) = self._main_win.getmaxyx()
        n_per_page = h // 3

        # How many items should we show?
        n_to_show = min(n_per_page, len(items))

        # Print the results along with an index number
        maxw = len(str(len(items)))

        n = 1; y = 0
        for item in items[:n_to_show]:
            num_str = ('%'+str(maxw)+'i') % (n,)
            if w > maxw:
                self._main_win.addstr(y, 0, num_str.encode(self._code), curses.color_pair(4) | curses.A_BOLD)
            self._add_video_item(y, maxw + 1, w-maxw-1, item)
            n += 1
            y += 3

    def _add_video_item(self, y, x, w, item):
        # Bail if we have _no_ horizontal space
        if w <= 0:
            return

        title = item['title']
        uploader = item['uploader']

        likes = int(item['likeCount']) if 'likeCount' in item else 0
        ratings = int(item['ratingCount']) if 'ratingCount' in item else 0
        comments = int(item['commentCount']) if 'commentCount' in item else 0
        views = int(item['viewCount']) if 'viewCount' in item else 0
        favorites = int(item['favoriteCount']) if 'favoriteCount' in item else 0

        # Show the title and uploader, prioritising the title
        if len(uploader) > w:
            self._main_win.addstr(y,x,truncate(title, w).encode(self._code), self._title_attr)
        else:
            self._main_win.addstr(y,x,truncate(title, w-len(uploader)).encode(self._code), self._title_attr)
            self._main_win.addstr(y,x+w-len(uploader), uploader.encode(self._code), self._uploader_attr)

        desc = item['description']
        if desc is None or len(desc.strip()) == 0:
            desc = 'No description'
        desc = re.sub(r'[\n\r]', r' ', desc)
        self._main_win.addstr(y+1,x,truncate(desc, w).encode(self._code), curses.color_pair(2))
        self._add_table_row([
                ('d', duration(item['duration'])),
                ('v', number(views)),
                ('c', number(comments)),
                ('l/d', '%s/%s' % (number(likes), number(ratings - likes)) ),
                ('f', number(favorites)),
            ], y+2, x, w, curses.color_pair(3) | curses.A_DIM, max_width=22)

    def _show_message(self, s):
        # Check length of message
        (h, w) = self._main_win.getmaxyx()
        if w < 3 or h < 3:
            return

        winw = min(len(s)+2, w)

        mw = curses.newwin(3, winw, (h//2)-1, (w-winw)//2)
        mw.bkgd(' ', curses.color_pair(5))
        mw.erase()
        mw.border()
        mw.addstr(1,1, truncate(s,winw-2).encode(self._code))
        mw.refresh()

    def _add_table_row(self, data, y, x, w, attr, max_width=None, min_width=4, win=None):
        if win is None:
            win = self._main_win
        n_keys = len(data)
        cell_w = max(w // n_keys, min_width)
        if max_width is not None:
            cell_w = min(cell_w, max_width)
        for k,v in data:
            if x < w:
                win.addstr(y, x, truncate('%s:%s' % (k,v), min(w-x, cell_w)).encode(self._code), attr)
            x += cell_w

def truncate(s, n):
    if(len(s) <= n):
        return s
    if(n < 1):
        return ''
    return s[:(n-1)] + u'\u2026'

def duration(n):
    if n < 60*60:
        return '%im%02is' % (n//60, n%60)
    return '%sh%-2im%02is' % (n//(60*60), (n%(60*60))//60, n%60)

def number(n):
    if n < 1000:
        return str(n)
    if n < 1000000:
        return '%.1fk' % (n/1000.0,)
    return '%.1fM' % (n//1000000.0,)

def play_url(url):
    yt_dl = subprocess.Popen(['youtube-dl', '-g', url], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (url, err) = yt_dl.communicate()
    if yt_dl.returncode != 0:
        sys.stderr.write(err)
        raise RuntimeError('Error getting URL.')
    mplayer = subprocess.Popen(
            ['mplayer', '-quiet', '-fs', '--', url.decode('UTF-8').strip()],
            stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    mplayer.wait()

def search(terms):
    def fetch_cb(start, maxresults, ordering):
        url = 'https://gdata.youtube.com/feeds/api/videos'
        query = {
            'q': terms,
            'v': 2,
            'alt': 'jsonc',
            'start-index': start,
            'max-results': maxresults,
            'orderby': ordering,
        }
        return json.load(urllib2.urlopen('%s?%s' % (url, urllib.urlencode(query))))

    return { 'fetch_cb': fetch_cb, 'description': 'search for "%s"' % (terms,) }

def user(username):
    def fetch_cb(start, maxresults, ordering):
        url = 'https://gdata.youtube.com/feeds/api/users/%s/uploads' % (username,)
        query = {
            'v': 2,
            'alt': 'jsonc',
            'start-index': start,
            'max-results': maxresults,
            'orderby': ordering,
        }
        return json.load(urllib2.urlopen('%s?%s' % (url, urllib.urlencode(query))))

    return { 'fetch_cb': fetch_cb, 'description': 'uploads by "%s"' % (username,) }

def standard_feed(feed_name):
    def fetch_cb(start, maxresults, ordering):
        url = 'https://gdata.youtube.com/feeds/api/standardfeeds/%s' % (feed_name,)
        query = {
            'v': 2,
            'alt': 'jsonc',
            'start-index': start,
            'max-results': maxresults,
            'orderby': ordering,
        }
        return json.load(urllib2.urlopen('%s?%s' % (url, urllib.urlencode(query))))

    feed = { 'fetch_cb': fetch_cb, 'description': '??? standard feed' }

    if feed_name == 'most_viewed':
        feed['description'] = 'most viewed'

    return feed

