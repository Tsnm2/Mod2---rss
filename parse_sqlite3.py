from pathlib import Path
import sqlite3

Path("config").mkdir(parents=True, exist_ok=True)


# SQLITE
def sqlite_connect():
    global conn
    conn = sqlite3.connect('config/rss.db', check_same_thread=False)


def init_sqlite():
    sqlite_connect()
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE rss (title text, url text, post_format text, keyword text, disable_link_preview integer, chat_id integer, last_sync_time integer, last_sync_post_url text)''')
    conn.commit()
    conn.close()


def sqlite_load_all():
    sqlite_connect()
    c = conn.cursor()
    c.execute('SELECT * FROM rss')
    rows = c.fetchall()
    conn.close()
    return rows


# table feeds
# FeedTitle
# feed.title
# FeedUrl
# rss_d.feed.title_detail.base
# EntryFormat
# #FeedEntries
# LastSyncTime(in feed)
# LastSyncPost(in feed)

def sqlite_update(title, url, post_format, keyword, disable_link_preview, chat_id, last_sync_time, last_sync_post_url,
                  update=False):
    sqlite_connect()
    c = conn.cursor()
    p = [last_sync_time, last_sync_post_url, title]
    q = [title, url, post_format, keyword, disable_link_preview, chat_id, last_sync_time, last_sync_post_url]
    if update:
        c.execute('''UPDATE rss SET last_sync_time = ?, last_sync_post_url = ? WHERE title = ?;''', p)
    else:
        c.execute(
            '''INSERT INTO rss('title','url','post_format', 'keyword', 'disable_link_preview', 'chat_id', 'last_sync_time', 'last_sync_post_url') VALUES(?,?,?,?,?,?,?,?)''',
            q)
    conn.commit()
    conn.close()


def sqlite_remove(title):
    sqlite_connect()
    c = conn.cursor()
    p = [title]
    c.execute('''DELETE FROM rss WHERE title = ?;''', p)
    conn.commit()
    conn.close()


# INSERT INTO rss('title','url','post_format','keyword', 'disable_link_preview', 'chat_id', 'last_sync_time', 'last_update_post_url') VALUES('1','1','1','1',1,'1','1')

def create_sqlite():
    # try to create a database if missing
    try:
        init_sqlite()
    except sqlite3.OperationalError:
        pass


def close_sqlite():
    conn.close()


if __name__ == '__main__':
    # init_sqlite()
    sqlite_update('3', '2', '1', '1', 1, 1, 1, '1')
    print(sqlite_load_all())
