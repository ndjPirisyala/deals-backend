from flask import Flask, jsonify, request
import logging
from threading import Thread
from selenium import webdriver
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, InlineQueryHandler, CallbackQueryHandler, CallbackContext
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, Update
from config import TOKEN, Amazon_login, Amazon_Password, Category_Links, main_link, default_cats
import time
import random
import datetime
import pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

global flag
flag = True
global post_dict

# app = Flask(_name_)

post_list = []
postX = []
op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome()
# driver = webdriver.Chrome('chromedriver')  # Optional argument, if not specified will search path.
driver.get(main_link)
username = driver.find_element_by_id('ap_email')
username.send_keys(Amazon_login)
password = driver.find_element_by_id('ap_password')
password.send_keys(Amazon_Password)
button = driver.find_element_by_id('signInSubmit')
button.click()



def start(update: Update, context: CallbackContext) -> None:
    global a, b
    a = update
    b = context
    print(update._effective_user.id)
    keyboard = []
    temp = []
    n = 0
    m = 0
    for key in Category_Links:
        temp.append(InlineKeyboardButton(key, callback_data=key))
        n += 1

        if n == 2:
            keyboard.append(temp)
            temp = []
            n = 0
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def stop(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="bot Stopping Now...")
    global flag
    flag = False


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = update.callback_query.message.from_user.username
    query.answer()
    answer = query.data
    query.edit_message_text(text="Searching for deals on Amazon. Please wait... (this can take up to 2 minutes)")
    driver.get(Category_Links[answer])
    time.sleep(5)
    f1 = 0
    list = []
    cards = driver.find_elements_by_class_name("a-section.a-spacing-none.tallCellView.gridColumn3.singleCell")
    for card in cards:
        temp = []
        try:
            link = card.find_element_by_id("dealTitle").get_attribute("href")
            # print(link)
            temp.append(link)
        except:
            pass
        try:
            special_offer = card.find_element_by_class_name("a-size-mini.a-color-base.dotdBadge").text
            temp.append(special_offer)
            print(special_offer)
        except Exception as e:
            print(e)
            temp.append('')
        try:
            price = card.find_element_by_class_name("gb-font-size-medium.inlineBlock.unitLineHeight.dealPriceText").text
            temp.append(price)
        except:
            temp.append('')
        try:
            discount_line = card.find_element_by_class_name("a-row.a-spacing-top-mini.unitLineHeight").text
            t_adviced_price = discount_line.split(': ')
            adviced_price = t_adviced_price[0] + " :"
            temp.append(adviced_price)
            t_old_price = t_adviced_price[1].split("(")
            old_price = t_old_price[0]
            temp.append(old_price)
            dis_percentage = '(' + t_old_price[1]
            temp.append(dis_percentage)
        except Exception as e:
            print(e)
            temp.append('')
        try:
            title = card.find_element_by_id("dealTitle").text
            # print(title)
            temp.append(title)
        except:
            pass
        try:
            vendor = card.find_element_by_id("shipSoldInfo").text
            temp.append(vendor)
        except:
            temp.append('')
        try:
            timer = card.find_element_by_css_selector('div.a-row.unitLineHeight').text
            print(timer)
        except Exception as e:
            print(e)

        list.append(temp)

    # print(list)
    global select_dict
    select_dict = {}
    try:
        for card in list:
            driver.get(card[0])
            button = driver.find_element_by_id('amzn-ss-text-link')
            button.click()
            time.sleep(2)
            link1 = driver.find_element_by_xpath("//*[@id='amzn-ss-text-shortlink-textarea']").text
            if card[1] != '':
                card[1] = '\n⭐ ' + card[1]
            try:
                image = driver.find_element_by_xpath("//*[@id='imgTagWrapperId']/img").get_attribute("src")
                caption = [image, "🚨 <b>" + card[6] + "</b>" + '\n \n' + "💰 " + card[2] + " <b>invece di</b> " + card[4] + " " + card[5] + '\n \n' + '➡️' + " " + link1, ["🚨", card[6], "💰", card[2], "invece di", card[4], card[5], '➡️', link1]]
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=image, parse_mode='html',
                                       caption=caption[1] + '\n\n' + str(f1 + 1))
                select_dict[str(f1 + 1)] = caption
                f1 += 1
                print("Working")
            except:
                try:
                    link_2 = driver.find_element_by_xpath(
                        "//*[@id='octopus-dlp-asin-stream']/ul/li/span/div/div[1]/a").get_attribute("href")
                    driver.get(link_2)
                    image = driver.find_element_by_xpath("//*[@id='imgTagWrapperId']/img").get_attribute("src")
                    caption = [image, "🚨 <b>" + card[6] + "</b>" + '\n \n' + "💰 " + card[2] + " <b>invece di</b> " + card[4] + " " + card[5] + '\n \n' + '➡️' + " " + link1, ["🚨", card[6], "💰", card[2], "invece di", card[4], card[5], '➡️', link1]]
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=image, parse_mode='html',
                                           caption=caption[1] + '\n\n' + str(f1 + 1))
                    select_dict[str(f1 + 1)] = caption
                    f1 += 1
                    print("Working")
                except Exception as e:
                    print(e)
            if f1 == 5:
                break
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="That's all. To post... send /select {post number here} (ex :- /select 1). post number won't be posted in the real post")
    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sorry... Something was wrong. please try again after a few minutes")


def extra():
    cat_link = random.choice(default_cats)
    driver.get(cat_link)
    f1 = 0
    list = []
    cards = driver.find_elements_by_class_name("a-section.a-spacing-none.tallCellView.gridColumn3.singleCell")
    for card in cards:
        temp = []
        try:
            link = card.find_element_by_id("dealTitle").get_attribute("href")
            # print(link)
            temp.append(link)
        except:
            pass
        try:
            special_offer = card.find_element_by_class_name("a-size-mini.a-color-base.dotdBadge").text
            temp.append(special_offer)
        except:
            temp.append('')
        try:
            price = card.find_element_by_class_name("gb-font-size-medium.inlineBlock.unitLineHeight.dealPriceText").text
            temp.append(price)
        except:
            temp.append('')
        try:
            discount_line = card.find_element_by_class_name("a-row.a-spacing-top-mini.unitLineHeight").text
            t_adviced_price = discount_line.split(': ')
            adviced_price = t_adviced_price[0] + " :"
            temp.append(adviced_price)
            t_old_price = t_adviced_price[1].split("(")
            old_price = t_old_price[0]
            temp.append(old_price)
            dis_percentage = '(' + t_old_price[1]
            temp.append(dis_percentage)
        except:
            temp.append('')
        try:
            title = card.find_element_by_id("dealTitle").text
            # print(title)
            temp.append(title)
        except:
            pass
        try:
            vendor = card.find_element_by_id("shipSoldInfo").text
            temp.append(vendor)
        except:
            temp.append('')
        list.append(temp)
        random.shuffle(list)
    print(list)
    print("@" * 100)
    global extra_posts
    extra_posts = []
    for card in list:
        driver.get(card[0])
        button2 = driver.find_element_by_id('amzn-ss-text-link')
        button2.click()
        time.sleep(2)
        link1 = driver.find_element_by_xpath("//*[@id='amzn-ss-text-shortlink-textarea']").text
        if card[1] != '':
            card[1] = '\n⭐ ' + card[1]
        try:
            image = driver.find_element_by_xpath("//*[@id='imgTagWrapperId']/img").get_attribute("src")
            caption = [image, "🚨 <b>" + card[6] + "</b>" + '\n \n' + "💰 " + card[2] + "<b> invece di </b>" + card[4] + " " + card[5] + '\n \n' + '➡️' + " " + link1, ["🚨", card[6], "💰", card[2], "invece di", card[4], card[5], '➡️', link1]]
            extra_posts.append(caption)
            f1 += 1
            print("Working")
        except:
            try:
                link_2 = driver.find_element_by_xpath(
                    "//*[@id='octopus-dlp-asin-stream']/ul/li/span/div/div[1]/a").get_attribute("href")
                driver.get(link_2)
                image = driver.find_element_by_xpath("//*[@id='imgTagWrapperId']/img").get_attribute("src")
                caption = [image, "🚨 <b>" + card[6] + "</b>" + '\n \n' + "💰 " + card[2] + "<b> invece di</b> " + card[4] + " " + card[5] + '\n \n' + '➡️' + " " + link1, ["🚨", card[6], "💰", card[2], "invece di", card[4], card[5], '➡️', link1]]
                extra_posts.append(caption)
                f1 += 1
                print("Working")
            except:
                continue
        if f1 == 5:
            break
    print(extra_posts)


def select(update, context):
    try:
        num = update.message.text
        num = num.replace('/select ', '')
        post_list.append(select_dict[num])
        context.bot.send_message(chat_id=update.effective_chat.id, text="Noted. I'll post it soon")
    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sorry. I didn't understand. send again with the correct item number. (ex:- '/select 2')")


def done(update, context):
    global upd, cont
    upd = update
    cont = context
    time.sleep(1)
    # print(post_list)


def main():
    global postX
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('select', select))
    updater.dispatcher.add_handler(CommandHandler('done', done))
    updater.dispatcher.add_handler(CommandHandler('stop', stop))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # updater.dispatcher.add_handler(InlineQueryHandler(inline_caps))
    # updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot

    updater.start_polling()
    while flag == True:
        current_time = datetime.datetime.now()
        if current_time.hour == 14:
            time.sleep(29880)
            print('hello' * 100)
        try:
            for post in post_list:
                cont.bot.send_photo(chat_id='@offerte_nerd', photo=post[0], parse_mode='html', caption=post[1])
                if len(postX) == 10:
                    postX.pop()
                postX.insert(0, post)
                pickle.dump(postX, open('temp', 'wb'))
                print(post[0])
                print(post[1])
                print('*' * 100)
                time.sleep(900)
                post_list.remove(post)

            if len(post_list) == 0:
                try:
                    post = random.choice(extra_posts)
                    print(post)
                    extra_posts.remove(post)
                    print("#" * 100)
                    cont.bot.send_photo(chat_id='@offerte_nerd', photo=post[0], parse_mode='html', caption=post[1])
                    if len(postX) == 10:
                        postX.pop()
                    postX.insert(0, post)
                    pickle.dump(postX, open('temp', 'wb'))
                    time.sleep(900)
                except Exception as e:
                    cont.bot.send_message(chat_id='229958009, ',
                                          text="List Empty... Searching for deals on Amazon Automatically")
                    extra()
        except:
            continue
    updater.idle()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT


# @app.route('/deals')
# def get_deals():
#    return jsonify(postX)



main()
