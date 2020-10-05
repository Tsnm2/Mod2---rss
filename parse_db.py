from psycopg2 import errors
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']


def db_connect():
    global conn
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')


def init_db():
    db_connect()
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE rss (title text, url text, post_format text, keyword text, disable_link_preview boolean, chat_id text, last_sync_time bigint, last_sync_post_url text, last_sync_post_title text)''')
    conn.commit()
    conn.close()


def db_load_all():
    db_connect()
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

def db_update(title, url, post_format, keyword, disable_link_preview, chat_id, last_sync_time, last_sync_post_url, last_sync_post_title,
              update=False):
    db_connect()
    c = conn.cursor()
    p = (last_sync_time, last_sync_post_url, last_sync_post_title, title)
    q = (title, url, post_format, keyword, disable_link_preview, chat_id, last_sync_time, last_sync_post_url, last_sync_post_title)
    if update:
        c.execute('''UPDATE rss SET last_sync_time = %s, last_sync_post_url = %s, last_sync_post_title = %s WHERE title = %s;''', p)
    else:
        c.execute(
            '''INSERT INTO rss(title,url,post_format,keyword,disable_link_preview,chat_id,last_sync_time,last_sync_post_url,last_sync_post_title) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            q)
    conn.commit()
    conn.close()


def db_remove(title):
    db_connect()
    c = conn.cursor()
    p = (title,)
    c.execute('''DELETE FROM rss WHERE title = %s;''', p)
    rowcount = c.rowcount
    conn.commit()
    conn.close()
    return rowcount


# INSERT INTO rss('title','url','post_format','keyword', 'disable_link_preview', 'chat_id', 'last_sync_time', 'last_update_post_url') VALUES('1','1','1','1',1,'1','1')

def create_db():
    # try to create a database if missing
    try:
        init_db()
    except errors.DuplicateTable:
        pass


def close_db():
    conn.close()


if __name__ == '__main__':
    # init_sqlite()
    db_update('3', '2', '1', '1', False, '1', 1, '1', '1')
    print(db_load_all())
