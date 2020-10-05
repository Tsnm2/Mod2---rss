url = 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
import feedparser

rss_d = feedparser.parse(url)
import parse_db
import FeedEntry
import time

rss_dict = {}


def rss_load():
    # if the dict is not empty, empty it.
    if bool(rss_dict):
        rss_dict.clear()

    for row in parse_db.sqlite_load_all():
        rss_dict[row[0]] = (row[1], row[2], row[3], row[4], row[5], row[6], row[7])


def rss_monitor():
    update_flag = False
    for name, dict_list in rss_dict.items():
        # dict_list[0] url
        # dict_list[1] format
        # dict_list[2] keyword
        # dict_list[3] disable_link_preview
        # dict_list[4] chat_id
        # dict_list[5] last_sync_time
        # dict_list[6] last_sync_post_url

        rss_d = feedparser.parse(dict_list[0])
        if not rss_d.entries:
            # print(f'Get {name} feed failed!')
            print('x', end='')
            break
        # if dict_list[5] == rss_d.entries[0]['link']:
        #     print('-', end='')
        if dict_list[5] >= int(time.mktime(rss_d.entries[0].published_parsed)):
            print('-', end='')
        else:
            print('\nUpdating', name)
            update_flag = True
            for entry in reversed(rss_d.entries):
                if int(time.mktime(entry.published_parsed)) > dict_list[5]:
                    entry_attr = []
                    feed_attr = ['title', 'link', 'author', 'summary']
                    for i in range(len(feed_attr)):
                        try:
                            entry_attr.append(entry[feed_attr[i]])
                        except KeyError:
                            entry_attr.append("")

                    if dict_list[2] != "ALL":
                        if (dict_list[2] in entry_attr[0]) or (dict_list[2] in entry_attr[3]):
                            fe = FeedEntry.FeedEntry(name, dict_list[0], entry_attr[0], entry_attr[1], entry_attr[2],
                                                     entry_attr[3], entry.published)
                            post_str = fe.generate_post(dict_list[1])
                        else:
                            continue
                    else:
                        fe = FeedEntry.FeedEntry(name, dict_list[0], entry_attr[0], entry_attr[1], entry_attr[2],
                                                 entry_attr[3], entry.published)
                        post_str = fe.generate_post(dict_list[1])
                    # message.send(chatid, entry['summary'], rss_d.feed.title, entry['link'], context)
                    print(post_str)
                    print(entry['title'])
                    # bot.send_message(dict_list[4], post_str, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview = bool(dict_list[3]))
            parse_db.sqlite_update(name, dict_list[0], dict_list[1], dict_list[2], dict_list[3], dict_list[4],
                                   time.mktime(rss_d.entries[0].published_parsed), rss_d.entries[0]['link'],
                                   True)  # update db

    if update_flag:
        print('Updated.')
        rss_load()  # update rss_dict


url = 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
title = "Test"
post_format = "{feed_title}: {entry_title} {entry_url}"
keyword = "ALL"
disable_link_preview = True
chat_id = "0"
# parse_db.init_sqlite()
try:
    rss_d = feedparser.parse(url)
    rss_d.entries[0]['title']
except IndexError:
    print(
        "ERROR: The link does not seem to be a RSS feed or is not supported")
    raise
# parse_db.sqlite_update(title, url, post_format, keyword, disable_link_preview, chat_id, 0, "")
rss_load()
print(rss_dict)
rss_monitor()
# rss_load()
print(rss_dict)
