from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, InlineQueryHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, conversationhandler
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, Update, replymarkup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from config import TOKEN, Amazon_login, Amazon_Password, Categories, main_link, keywords, alpha
import time, random, requests, logging, json, urllib.request
from PIL import Image, ImageFont, ImageDraw, ImageOps
from func import resize
from shutil import copyfile
import pickle
import base64

## Amazon API Configuration 
url = "https://amazon-products1.p.rapidapi.com/offers"
url2 = "https://amazon-products1.p.rapidapi.com/search"
url3 = "https://amazon-products1.p.rapidapi.com/asin"
url4 = "https://amazon-products1.p.rapidapi.com/product"

iii = 'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='

headers = {
    'x-rapidapi-key': "fd34595df9msh13c2e0ceaa75e4cp1767f9jsn34c383e14eee",
    'x-rapidapi-host': "amazon-products1.p.rapidapi.com"
    }

# Webdriver Configuration
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(main_link)
username = driver.find_element_by_id('ap_email')
username.send_keys(Amazon_login)
password = driver.find_element_by_id('ap_password')
password.send_keys(Amazon_Password)
button = driver.find_element_by_id('signInSubmit')
button.click()

## logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

BUTTON1, BUTTON2, SEARCH, URL, SELECT, DIRECT = range(6)
def strike(text):
    return ''.join([u'\u0336{}'.format(c) for c in text])

global asin_list, posts, final_posts, extra_posts, flag
posts = {}
asin_list = []
final_posts = []
extra_posts = []
postX = []
posts_to_front = 0
flag = False
def start(update: Update, context: CallbackContext) -> None:
    # print(update.effective_user.id)
    update.message.reply_text("Select an Option")

    keyboard = [
        [InlineKeyboardButton("Search with a Category", callback_data='1')],
        [InlineKeyboardButton("Search with a Keyword", callback_data='2')],
        [InlineKeyboardButton("Enter an Item to the list", callback_data="3")],
        [InlineKeyboardButton("Instant Post Add", callback_data="4")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please select:', reply_markup=reply_markup)

    return BUTTON1

def button1(update: Update, context: CallbackContext) -> None:
    # print(update.callback_query.message.chat.first_name)
    query = update.callback_query
    query.answer()
    answer = query.data
    if answer == '1':
        temp = []
        keyboard = []
        n = 0
        for key in Categories:
            temp.append(InlineKeyboardButton(key, callback_data = key))
            n += 1

            if n == 2:
                keyboard.append(temp)
                temp = []
                n = 0
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text = "Please Select" , chat_id = update.effective_user.id ,reply_markup = reply_markup)
        return BUTTON2

    elif answer == '2':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Send a Keyword")
        return SEARCH 
    
    elif answer == "3":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Send a URL")
        return URL

    elif answer == "4":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Send a URL")
        return DIRECT

def button2(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        query.answer()
        answer = query.data
        query.edit_message_text(text= "Searching for deals on Amazon. Please wait...")
        querystring = {"min_number":"1","country":"IT","type":"ALL","max_number":"100", "sub_categories" : f"{Categories[answer]}"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        x = json.loads(response.text)
        # print(x)
        # print(type(x))
        i = 1
        global asin_list
        length = len(x["offers"])
        if length < 5:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Only {length} deals are available for the {answer} category")
        for item in x["offers"]:
            asin = item["asin"]
            if asin not in asin_list:
                if i <= 5:
                    asin_list.append(asin)
                    title = item["title"]
                    try:
                        image = item["images"][0]
                    except:
                        image = item["image"]
                    price = item["prices"]["current_price"]
                    old_price = item["prices"]["previous_price"]
                    if '-' in str(price) or '-' in str(old_price):
                        continue
                    checkout_discount = item["prices"]["previous_price"]
                    currency = item["prices"]["currency"]
                    link = item["full_link"]
                    reviews = item["reviews"]["total_reviews"]
                    stars = item["reviews"]["stars"]
                    resize(image=image, currency=currency, old_price=float(old_price), price=price)
                    caption = f"🚨 {title}\n\n💰 A {price}{currency} invece di {old_price}{currency}\n⭐️ Recensioni : {stars} stelle\n\n➡️ {link} \n\n {str(i)}"
                    # print(caption)
                    keyboard = [[InlineKeyboardButton("link", callback_data='1')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('a.png', 'rb'), parse_mode= 'html', caption= caption, reply_markup=reply_markup)
                    # context.bot.send_photo(chat_id=update.effective_chat.id, photo= image, parse_mode= 'html', caption= caption )
                    posts[str(i)] = [asin, title, image, link, price, old_price, currency, reviews, stars]
                    i +=1
        context.bot.send_message(chat_id=update.effective_chat.id, text="That's all")
        # print("yes")
        return SELECT
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error. Looks like this category doesn't have any deals .Please try again. '/start")
        return ConversationHandler.END


def search(update, context):
    try:
        keyword = update.message.text
        keyword = keyword.replace(" ", "+")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Searching on Amazon. Please wait...")
        querystring_1 = {"country":"IT","query":f"{keyword}","page":"1"}
        response = requests.request("GET", url2, headers=headers, params=querystring_1)
        y =json.loads(response.text)
        i = 1
        for item in y["results"]:
            asin = item["asin"]
            if asin not in asin_list:
                if i <= 5:
                    if not item["prices"]["previous_price"] == -1.0:
                        # print(item["prices"]["previous_price"])
                        asin_list.append(asin)
                        title = item["title"]
                        try:
                            image = item["images"][0]
                        except:
                            image = item["image"]
                        price = item["prices"]["current_price"]
                        old_price = item["prices"]["previous_price"]
                        if '-' in str(price) or '-' in str(old_price):
                            continue
                        checkout_discount = item["prices"]["previous_price"]
                        currency = item["prices"]["currency"]
                        link = item["full_link"]
                        reviews = item["reviews"]["total_reviews"]
                        stars = item["reviews"]["stars"]
                        resize(image=image, currency=currency, old_price=float(old_price), price=price)
                        caption = f"🚨 {title}\n\n💰 A {price}{currency} invece di {old_price}{currency}\n⭐️ Recensioni : {stars} stelle\n\n➡️ {link} \n\n {str(i)}"
                        # print(caption)
                        keyboard = [[InlineKeyboardButton("link", callback_data='1')]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('a.png', 'rb'), parse_mode= 'html', caption= caption, reply_markup=reply_markup, timeout=100)
                        # context.bot.send_photo(chat_id=update.effective_chat.id, photo= image, parse_mode= 'html', caption= caption )
                        posts[str(i)] = [asin, title, image, link, price, old_price, currency, reviews, stars]
                        i +=1
        context.bot.send_message(chat_id=update.effective_chat.id, text="That's all")
        return SELECT
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error. Please Send again")
        return SEARCH

def url_add(update, context):
    global cont, upd, flag, final_posts, Id, flag
    Id = update.effective_chat.id
    cont = context
    upd = update
    if not update.message.text == '/cancel':
        try:
            keyword = update.message.text
            querystring = {"url":f"{keyword}"}
            response = requests.request("GET", url3, headers=headers, params=querystring)
            z = json.loads(response.text)
            asin = z["asin"]
            querystring = {"country":"IT","asin":f"{asin}"}
            response = requests.request("GET", url4, headers=headers, params=querystring)
            item = json.loads(response.text)
            asin = item["asin"]
            # print(asin)
            # print(asin_list)
            if asin not in asin_list:
                asin_list.append(asin)
                title = item["title"]
                try:
                    image = item["images"][0]
                except:
                    image = item["image"]
                link = item["full_link"]
                price = item["prices"]["current_price"]
                old_price = item["prices"]["previous_price"]
                checkout_discount = item["prices"]["previous_price"]
                currency = item["prices"]["currency"]
                reviews = item["reviews"]["total_reviews"]
                stars = item["reviews"]["stars"]
                resize(image=image, currency=currency, old_price=float(old_price), price=price)
                if old_price == -1.0:
                    caption = f"🚨 {title}\n\n💰 {price}{currency}\n⭐️ Recensioni : {stars} stelle\n\n➡️ {link}"
                else:
                    caption = f"🚨 {title}\n\n💰 A {price}{currency} invece di {old_price}{currency}\n⭐️ Recensioni : {stars} stelle\n\n➡️ {link}"
                # print(caption)
                keyboard = [[InlineKeyboardButton("link", callback_data='1')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('a.png', 'rb'), parse_mode= 'html', caption= caption, reply_markup=reply_markup)
                # context.bot.send_photo(chat_id=update.effective_chat.id, photo= image, parse_mode= 'html', caption= caption )
                final_posts.append([asin, title, image, link, price, old_price, currency, reviews, stars])
                    
                context.bot.send_message(chat_id=update.effective_chat.id, text="Added to the list")
                flag = True
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Error. Please send again")
            return URL
    return ConversationHandler.END

def direct(update, context):
    global cont, upd, flag, final_posts, Id, flag, posts_to_front
    Id = update.effective_chat.id
    cont = context
    upd = update
    if not update.message.text == '/cancel':
        try:
            keyword = update.message.text
            querystring = {"url":f"{keyword}"}
            response = requests.request("GET", url3, headers=headers, params=querystring)
            z = json.loads(response.text)
            asin = z["asin"]
            querystring = {"country":"IT","asin":f"{asin}"}
            response = requests.request("GET", url4, headers=headers, params=querystring)
            item = json.loads(response.text)
            asin = item["asin"]
            # print(asin)
            # print(asin_list)
            if asin not in asin_list:
                asin_list.append(asin)
                title = item["title"], postX
                try:
                    image = item["images"][0]
                except:
                    image = item["image"]
                link = item["full_link"]
                driver.get(link)
                time.sleep(4)
                try:
                    image = driver.find_element_by_xpath("//*[@id='imgTagWrapperId']/img").get_attribute("src")
                except:
                    image = image
                button = driver.find_element_by_id('amzn-ss-text-link')
                button.click()
                time.sleep(2)
                link1 = driver.find_element_by_xpath("//*[@id='amzn-ss-text-shortlink-textarea']").text
                price = item["prices"]["current_price"]
                old_price = item["prices"]["previous_price"]
                checkout_discount = item["prices"]["previous_price"]
                currency = item["prices"]["currency"]
                reviews = item["reviews"]["total_reviews"]
                stars = item["reviews"]["stars"]
                resize(image=image, currency=currency, old_price=float(old_price), price=price)
                if old_price == -1.0:
                    caption = f"🚨 {title}\n\n💰 {price}{currency}\n⭐️ Recensioni : {stars} stelle\n\n➡️ {link}"
                    cap = f"🚨 {title}\n\n💰 A {price}{currency} invece di {old_price}{currency}\n⭐️ Recensioni : {stars} stelle"
                    captionx = cap.replace('\n', 'v123v123s123s123n123n123')
                else:
                    caption = f"🚨 {title}\n\n💰 A {price}{currency} invece di {old_price}{currency}\n⭐️ Recensioni : {stars} stelle\n\n➡️ {link}"
                    cap = f"🚨 {title}\n\n💰 A {price}{currency} invece di {old_price}{currency}\n⭐️ Recensioni : {stars} stelle"
                    captionx = cap.replace('\n', 'v123v123s123s123n123n123')
                keyboard = [[InlineKeyboardButton("link", callback_data='1')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('a.png', 'rb'), parse_mode= 'html', caption= caption, reply_markup=reply_markup)
                context.bot.send_photo(chat_id=update.effective_chat.id, photo= image, parse_mode= 'html', caption= caption )
                name = ''.join(random.choice(alpha) for _ in range(7)).lower() +'-'+str(int(time.time()))+'.png'
                copyfile('a.png', f'images/{name}')

                cont.bot.send_photo(chat_id='@nadeejachannel', photo= open('a.png', 'rb'), parse_mode= 'html', caption= caption)
                # print('*'*100)                    
                context.bot.send_message(chat_id=update.effective_chat.id, text="Posted on the Channel")

                # TO THE FRONTEND
                with open("a.png", "rb") as image_file:
                    IMG64 = base64.b64encode(image_file.read())
                post_temp = [str(IMG64), captionx, "➡️", link]
                postX = pickle.load(open('temp', 'rb'))
                if len(postX) == 12:
                    postX.pop()
                postX.insert(0, [post_temp, 0])
                posts_to_front += 1
                pickle.dump(posts_to_front, open('count', 'wb'))
                pickle.dump(postX, open('temp', 'wb'))

                flag = True
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Error. Please send again")
            return URL
    return ConversationHandler.END

def select(update, context):
    global cont, upd, flag, final_posts, Id
    Id = update.effective_chat.id
    cont = context
    upd = update
    try:
        count = update.message.text
        count = count.replace('/select ', '')
        if count.lower() == "all":
            for i in posts.values():
                final_posts.append(i)
            context.bot.send_message(chat_id=update.effective_chat.id, text= "Noted. I'll post it soon")  
            flag = True
            context.bot.send_message(chat_id=update.effective_chat.id, text= "'/start' to search again")
            return ConversationHandler.END
            
        else:
            final_posts.append(posts[count])
            context.bot.send_message(chat_id=update.effective_chat.id, text= "Noted. I'll post it soon")
            flag = True
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text= "Sorry. I didn't understand. send again with the correct item number. (ex:- '/select 2' or '/select all')" )


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("/start to start again")
    return ConversationHandler.END

def stop(update: Update, context: CallbackContext):
    update.message.reply_text("/resume to continue")
    global flag
    flag = False

def resume(update: Update, context: CallbackContext):
    update.message.reply_text("/Starting")
    global flag, cont, upd
    cont = context
    upd = update
    flag = True
    
def main():
    global postX, posts_to_front
    updater = Updater(TOKEN, use_context=True)

    conv_handler = ConversationHandler(
        entry_points=[(CommandHandler('start', start))],
        states={
            BUTTON1 : [CallbackQueryHandler(button1), CommandHandler('cancel', cancel)],
            BUTTON2 : [CallbackQueryHandler(button2), CommandHandler('cancel', cancel)],
            SELECT : [CommandHandler("select", select), CommandHandler('cancel', cancel)],
            SEARCH : [MessageHandler(Filters.text, search), CommandHandler('cancel', cancel)],
            URL : [MessageHandler(Filters.text, url_add), CommandHandler('cancel', cancel)],
            DIRECT : [MessageHandler(Filters.text, direct), CommandHandler('cancel', cancel)],
        },
        fallbacks= [CommandHandler('cancel', cancel, run_async=True)],
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler('stop', stop))
    updater.dispatcher.add_handler(CommandHandler('resume', resume))
    # updater.dispatcher.add_handler(CommandHandler('help', help_command, run_async=True))

    updater.start_polling()
    while True:
        if flag == True:
            print("*")
            try:
                # print(final_posts)
                for post in final_posts:
                    driver.get(post[3])
                    time.sleep(4)
                    try:
                        image = driver.find_element_by_xpath("//*[@id='imgTagWrapperId']/img").get_attribute("src")
                    except:
                        image = post[2]
                    resize(image=image, currency=post[6], old_price=post[5], price=post[4])
                    button = driver.find_element_by_id('amzn-ss-text-link')
                    button.click()
                    time.sleep(2)
                    link1 = driver.find_element_by_xpath("//*[@id='amzn-ss-text-shortlink-textarea']").text
                    caption = f"🚨 {post[1]}\n\n💰 A {post[4]}{post[6]} invece di {float(post[5])}{post[6]}\n⭐️ Recensioni : {post[8]} stelle\n\n➡️ {link1}"
                    cap = f"🚨 {post[1]}\n\n💰 A {post[4]}{post[6]} invece di {float(post[5])}{post[6]}\n⭐️ Recensioni : {post[8]} stelle"
                    captionx = cap.replace('\n', 'v123v123s123s123n123n123')
                    name = ''.join(random.choice(alpha) for _ in range(7)).lower() +'-'+str(int(time.time()))+'.png'
                    copyfile('a.png', f'images/{name}')
                   
                    cont.bot.send_photo(chat_id='@nadeejachannel', photo= open('a.png', 'rb'), parse_mode= 'html', caption= caption)

                    # TO THE FRONTEND
                    with open("a.png", "rb") as image_file:
                        IMG64 = base64.b64encode(image_file.read())
                    post_temp = [str(IMG64), captionx, "➡️", link1]
                    postX = pickle.load(open('temp', 'rb'))
                    if len(postX) == 12:
                        postX.pop()
                    postX.insert(0, [post_temp, 0])
                    posts_to_front += 1
                    pickle.dump(posts_to_front, open('count', 'wb'))
                    pickle.dump(postX, open('temp', 'wb'))

                    final_posts.remove(post)
                    time.sleep(900)
                if len(final_posts) == 0:
                    try:
                        post = random.choice(extra_posts)
                        driver.get(post[3])
                        time.sleep(4)
                        try:
                            image = driver.find_element_by_xpath("//*[@id='imgTagWrapperId']/img").get_attribute("src")
                        except:
                            image = post[2]
                        resize(image=image, currency=post[6], old_price=post[5], price=post[4])
                        button = driver.find_element_by_id('amzn-ss-text-link')
                        button.click()
                        time.sleep(2)
                        link1 = driver.find_element_by_xpath("//*[@id='amzn-ss-text-shortlink-textarea']").text
                        caption = f"🚨 {post[1]}\n\n💰 A {post[4]}{post[6]} invece di {float(post[5])}{post[6]}\n⭐️ Recensioni : {post[8]} stelle\n\n➡️ {link1}"
                        cap = f"🚨 {post[1]}\n\n💰 A {post[4]}{post[6]} invece di {float(post[5])}{post[6]}\n⭐️ Recensioni : {post[8]} stelle"
                        captionx = cap.replace('\n', 'v123v123s123s123n123n123')
                        name = ''.join(random.choice(alpha) for _ in range(7)).lower() +'-'+str(int(time.time()))+'.png'
                        copyfile('a.png', f'images/{name}')
 
                        cont.bot.send_photo(chat_id='@nadeejachannel', photo= open('a.png', 'rb'), parse_mode= 'html', caption= caption)

                        # TO THE FRONTEND
                        with open("a.png", "rb") as image_file:
                            IMG64 = base64.b64encode(image_file.read())
                        post_temp = [str(IMG64), captionx, "➡️", link1]
                        postX = pickle.load(open('temp', 'rb'))
                        if len(postX) == 12:
                            postX.pop()
                        postX.insert(0, [post_temp, 0])
                        posts_to_front += 1
                        pickle.dump(posts_to_front, open('count', 'wb'))
                        pickle.dump(postX, open('temp', 'wb'))
                        
                        extra_posts.remove(post)
                        time.sleep(900)
                    except Exception as e:
                        print(e)
                        cont.bot.send_message(chat_id=Id, text= "List Empty... Searching for deals on Amazon Automatically")
                        querystring_1 = {"country":"IT","query":f"{random.choice(keywords)}","page":"1"}
                        response = requests.request("GET", url2, headers=headers, params=querystring_1)
                        y =json.loads(response.text)
                        i = 1
                        for item in y["results"]:
                            asin = item["asin"]
                            if asin not in asin_list:
                                if i <= 5:
                                    if not item["prices"]["previous_price"] == -1.0:
                                        asin_list.append(asin)
                                        title = item["title"]
                                        try:
                                            image = item["images"][0]
                                        except:
                                            image = item["image"]
                                        price = item["prices"]["current_price"]
                                        old_price = item["prices"]["previous_price"]
                                        if '-' in str(price) or '-' in str(old_price):
                                            continue
                                        checkout_discount = item["prices"]["previous_price"]
                                        currency = item["prices"]["currency"]
                                        link = item["full_link"]
                                        reviews = item["reviews"]["total_reviews"]
                                        stars = item["reviews"]["stars"]
                                        extra_posts.append([asin, title, image, link, price, old_price, currency, reviews, stars])
                                        i +=1
            except Exception as e:
                print(e)
                continue
    
    updater.idle()


if __name__ == '__main__':
    main()
