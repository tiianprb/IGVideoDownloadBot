import logging
import validators
import datetime
import telegram
from instascrape import *
import datetime
from os import remove

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

token = 'Your token from telegram'
bot = telegram.Bot(token=token)

#Command handlers, they take 2 parameters, update and context

def start(update, context):
    #When the user starts the bot (/start)
    message = "Hello! Download any video from Instagram, just send me the link to the video and let me take care of the rest ;-)"

    update.message.reply_text(message)

def help(update, context):
    #When the user needs help (/help)
    message = "To get started, type '/start' \n Then paste the link to the Instagram video and wait for me to download it for you"
    update.message.reply_text(message)

def user_message(update, context):
    #If the user message is a valid url, we try to download the video, otherwise we send an error
    userMessage = update.message.text

    #we get the chat id, we will need it to send the file
    chat_id = update.message.chat.id

    if userMessage.find('http://') == 0 or userMessage.find('https://') == 0:
        pass
    else:
        userMessage = 'http://' + userMessage

    if validators.url(userMessage):

        filename = downloadVideo(userMessage)
        bot.send_video(chat_id, open(filename, 'rb'))
        remove(filename)
        
    else:
        update.message.reply_text(userMessage + " is not a valid link, stop playing with me")

def error(update, context):
    #Log errors
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def downloadVideo(url):
    
    #we search in the url words that can show us the format of the post, wether its a post, IGTV or Reel
    if url.find('/reel/') != -1:
        post = Reel(url)
        extension = '.mp4'
    elif url.find('/tv/') != -1:
        post = IGTV(url)
        extension = '.mp4'
    else:
        post = Post(url)
        extension = '.png'
        
    post.scrape()
    filename = datetime.datetime.now().strftime("%d%m%Y-%H%M%s") + extension
    post.download(fp=filename)

    return filename

def main():
    #Start the bot

    updater = Updater(token, use_context=True)

    #get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))

    #on no command, echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text, user_message))

    #log all errors
    dispatcher.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
