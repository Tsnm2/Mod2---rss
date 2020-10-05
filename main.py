from datetime import datetime
import feedparser
import logging
import FeedEntry
import os
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
from telegram.error import BadRequest, RetryAfter
import parse_db
import time

# Docker env
if os.environ.get('TOKEN'):
    token = os.environ['TOKEN']
    admin = os.environ.get('ADMIN')
    delay = int(os.environ['DELAY'])
    port = int(os.environ.get("PORT", "8443"))
    webhook_url = os.environ.get("WEBHOOK_URL")
else:
    token = "X"
    delay = 120

if token == "X":
    print("Token not set!")

rss_dict = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def run(updater):
    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=token)
    updater.bot.set_webhook("https://{}/{}".format(webhook_url, token))


# ADMIN
def is_admin(update):
    chat = update.message.chat
    userid = str(chat.id)
    command = update.message.text
    print(f'\nUser {userid} attempted to use "{command}", ', end='')
    if admin != userid:
        update.effective_message.reply_text('You have no privilege to use this bot.')
        print('forbidden.')
        raise
    else:
        print('allowed.')

def replace_underscore(content):
    keyword_dict = {
        '{feed_title}': 'FEEDTITLE',
        '{feed_url}': 'FEEDURL',
        '{entry_title}': 'ENTRYTITLE',
        '{entry_url}': 'ENTRYURL',
        '{entry_author}': 'ENTRYAUTHOR',
        '{entry_content}': 'ENTRYCONTENT',
        '{entry_published}': 'ENTRYPUBLISHED'
    }
    for key, value in keyword_dict.items():
        content = content.replace(key, value)
    content = content.replace('_', ' ')
    for key, value in keyword_dict.items():
        content = content.replace(value, key)
    return content


def cmd_rss_add(update, context):
    is_admin(update)

    # args_full = update.message.text.replace('/add_', '')
    # args = args_full.split("_")

    # try if there are 6 arguments passed
    try:
        context.args[5]
    except IndexError:
        update.effective_message.reply_text(
            "ERROR: The format needs to be: /add title http://www.example.com post_format keyword disable_link_preview chat_id")
        raise
    # try if the url is a valid RSS feed
    try:
        rss_d = feedparser.parse(context.args[1])
        rss_d.entries[0]['title']
        test_feed = FeedEntry.FeedEntry(replace_underscore(context.args[0]), context.args[1], rss_d.entries[0])
    except IndexError:
        update.effective_message.reply_text(
            "ERROR: The link does not seem to be a RSS feed or is not supported")
        raise
    except Exception as e:
        update.effective_message.reply_text("Error happened: " + str(e))
        raise
    parse_db.db_update(replace_underscore(context.args[0]), context.args[1], replace_underscore(context.args[2]),
                       replace_underscore(context.args[3]), bool(int(context.args[4])), context.args[5],
                       int(test_feed.get_entry_published()), test_feed.get_entry_url(), test_feed.get_entry_title())
    rss_load()
    update.effective_message.reply_text(
        "Added \nTitle: %s\nRSS: %s\nPost format: %s\nKeyword: %s\nDisable link preview: %s\nChat ID: %s" % (
            replace_underscore(context.args[0]), context.args[1], replace_underscore(context.args[2]),
            replace_underscore(context.args[3]), str(bool(int(context.args[4]))), context.args[5]),
        disable_web_page_preview=True)


# INSERT INTO rss('title','url','post_format', 'keyword', 'disable_link_preview', 'chat_id', 'last_sync_time', 'last_sync_post_url') VALUES('1','1','1','1',1,1,1,'1')

# RSS________________________________________
def rss_load():
    # if the dict is not empty, empty it.
    if bool(rss_dict):
        rss_dict.clear()

    for row in parse_db.db_load_all():
        rss_dict[row[0]] = (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])


def cmd_rss_list(update, context):
    is_admin(update)
    # dict_list[0] url
    # dict_list[1] format
    # dict_list[2] keyword
    # dict_list[3] disable_link_preview
    # dict_list[4] chat_id
    # dict_list[5] last_sync_time
    # dict_list[6] last_sync_post_url
    if bool(rss_dict) is False:
        update.effective_message.reply_text("The database is empty")
    else:
        for title, dict_list in rss_dict.items():
            update.effective_message.reply_text(
                "Title: " + title +
                "\nRSS url: " + dict_list[0] +
                "\nRSS format: " + dict_list[1] +
                "\nRSS keyword: " + dict_list[2] +
                "\nDisable link preview: " + str(dict_list[3]) +
                "\nTarget chat id: " + dict_list[4] +
                "\nLast checked time: " + datetime.fromtimestamp(dict_list[5]).strftime('%Y-%m-%d %H:%M:%S') +
                "\nLast checked article: " + dict_list[6] +
                "\nLast checked title: " + dict_list[7])


def cmd_rss_remove(update, context):
    is_admin(update)

    db_remove = parse_db.db_remove(replace_underscore(context.args[0]))
    rss_load()
    if db_remove >= 1:
        update.effective_message.reply_text("Removed: " + replace_underscore(context.args[0]))
    else:
        update.effective_message.reply_text(f'Something went wrong. The record is not removed.')


def cmd_help(update, context):
    is_admin(update)

    print(context.chat_data)
    update.effective_message.reply_text(
        "RSS to Telegram bot" +
        "\n\nAfter successfully adding a RSS link, the bot starts fetching the feed every "
        + str(delay) + " seconds. (This can be set)" +
        "\n\nTitles are used to easily manage RSS feeds" +
        "\n\ncommands:" +
        "\n/help Posts this help message" +
        "\n/add title http://www.example.com post_format keyword disable_link_preview chat_id" +
        "\n/remove title removes the RSS link" +
        "\n/list Lists all the titles and the RSS links from the DB" +
        "\n/test Inbuilt command that fetches a post from Reddit RSS." +
        "\n\nWhen there is space inside title, post_format or keyword, you can use '_' as a replacement." +
        "\npost_format accepts feed_title, feed_url, entry_title, entry_url, entry_author, entry_content and "
        "entry_published. Put them into {} to pass them as variables. The format will be parsed as HTML." +
        "\nWhen keyword is 'ALL', all feeds are accepted." +
        "\n\nThe current chatId is: " + str(update.message.chat.id)

    )


def cmd_test(update, context):
    is_admin(update)

    url = "https://www.reddit.com/r/funny/new/.rss"
    rss_d = feedparser.parse(url)
    rss_d.entries[0]['link']
    update.effective_message.reply_text(rss_d.entries[0]['link'])


def rss_monitor(context):
    update_flag = False
    bot = context.bot
    for name, dict_list in rss_dict.items():
        # dict_list[0] url
        # dict_list[1] format
        # dict_list[2] keyword
        # dict_list[3] disable_link_preview
        # dict_list[4] chat_id
        # dict_list[5] last_sync_time
        # dict_list[6] last_sync_post_url
        # dict_list[7] last_sync_post_title

        rss_d = feedparser.parse(dict_list[0])
        if not rss_d.entries:
            # print(f'Get {name} feed failed!')
            print('x', end='')
            break

        latest_feed = FeedEntry.FeedEntry(name, dict_list[0], rss_d.entries[0])

        if dict_list[5] >= latest_feed.get_entry_published():
            print('-', end='')

        else:
            print('\nUpdating', name)
            update_flag = True
            for entry in reversed(rss_d.entries):
                fe = FeedEntry.FeedEntry(name, dict_list[0], entry)
                if dict_list[5] < fe.get_entry_published():
                    try:
                        if dict_list[6] == fe.get_entry_url() and dict_list[7] == fe.get_entry_title():
                            parse_db.db_update(name, dict_list[0], dict_list[1], dict_list[2], dict_list[3],
                                               dict_list[4], fe.get_entry_published(), fe.get_entry_url(), fe.get_entry_title(),
                                               True)  # update db
                            continue
                        elif dict_list[2] != "ALL" and (dict_list[2] not in fe.get_entry_title()) and (dict_list[2] not in fe.get_entry_content()):
                            parse_db.db_update(name, dict_list[0], dict_list[1], dict_list[2], dict_list[3],
                                               dict_list[4], fe.get_entry_published(), fe.get_entry_url(), fe.get_entry_title(),
                                               True)  # update db
                            continue
                        else:
                            post_str = fe.generate_post(dict_list[1])
                    except Exception as e:
                        post_str = str(e)
                    while True:
                        try:
                            bot.send_message(dict_list[4], post_str, parse_mode=ParseMode.HTML,
                                             disable_web_page_preview=dict_list[3])
                            parse_db.db_update(name, dict_list[0], dict_list[1], dict_list[2], dict_list[3],
                                               dict_list[4], fe.get_entry_published(), fe.get_entry_url(), fe.get_entry_title(),
                                               True)  # update db
                            time.sleep(1)
                        except BadRequest as br:
                            bot.send_message(admin, "Error: " + str(
                                br) + "\nPlease check the Chat ID and make sure your bot is in the group/channel.")
                        except RetryAfter as ra:
                            print(ra)
                            print(f"Telegram flood control exceeded when delivering: {fe.get_entry_title()}")
                            time.sleep(30)
                            continue
                        except Exception as e:
                            print(e)
                            print(f"Error happened when delivering: {fe.get_entry_title()}")
                            bot.send_message(admin, "Error: " + str(
                                e) + f"\nFailed to deliver: {fe.get_entry_title()}")
                            #time.sleep(30)
                            break
                        break
    if update_flag:
        print('Updated.')
        rss_load()  # update rss_dict


def main():
    print(f'ADMIN: {admin}\nDELAY: {delay}s\n')

    updater = Updater(token=token, use_context=True)
    job_queue = updater.job_queue
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("add", cmd_rss_add))
    dp.add_handler(CommandHandler("start", cmd_help))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("test", cmd_test))
    dp.add_handler(CommandHandler("list", cmd_rss_list))
    dp.add_handler(CommandHandler("remove", cmd_rss_remove))

    run(updater)

    parse_db.create_db()
    rss_load()

    job_queue.run_repeating(rss_monitor, delay)
    rss_monitor(updater)

    # updater.start_polling()
    # updater.idle()
    parse_db.close_db()


if __name__ == '__main__':
    main()
