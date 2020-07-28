import instaloader
from datetime import datetime
import time
import logging
import os
import telegram
from telegram.ext import CommandHandler, Updater

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s," 
)
logger = logging.getLogger()

logger.info('Getting connection with instaloader')
L = instaloader.Instaloader(download_comments=False, max_connection_attempts=9, post_metadata_txt_pattern=None, save_metadata=False, download_video_thumbnails=False, download_geotags=False, filename_pattern="{shortcode}")

logger.info('Connected successfully')

PROFILES = ["checkandplay","elrubiuswtf", "instantgaminges", "levelupcom", "3djuegos"] #set here your profile accounts to get posts

date = datetime.now() 
now = datetime(date.year,date.month,date.day)

timeSleep = 10 #set time to wait between posts

TOKEN = os.getenv("TOKEN") #get bot token

def getStart(update, context):
    bot = context.bot
    chatId = update.message.chat_id

    while True:
        try:
            for PROFILE in PROFILES:
                logger.info(f'Profile = {PROFILE}')
                print(f'Timeout: {timeSleep}')
                time.sleep(timeSleep)
                profile = instaloader.Profile.from_username(L.context, PROFILE) #connect with the profile
                logger.info('Profile loaded')

                for post in profile.get_posts(): #get posts of the profile
                    if post.date >= now: #if the posts were published "today"
                        print(f'Timeout to download: {timeSleep}')
                        time.sleep(timeSleep)
                        download = L.download_post(post,PROFILE)#download post
                        if download==True: #the download has been successfully
                            video = post.is_video #verify if the post is a video
                            if video==True:
                                try:
                                    with open(post.owner_username+'/'+post.shortcode+'.mp4' , 'rb') as f: #create and save a file with post
                                        bot.send_video(chat_id=chatId, video=f) #send the video to the chat
                                        if post.caption == None: #if the post has no description
                                            bot.sendMessage(chat_id=chatId, parse_mode='HTML', text=f'<b>{post.owner_username}:</b> None')
                                        else: #send message with post description
                                            bot.sendMessage(chat_id=chatId, parse_mode='HTML', text=f'<b>{post.owner_username}:</b> {post.caption}')
                                        
                                        break
                                except:
                                    pass   
                            else: #the post is an image
                                try:
                                    with open(post.owner_username+'/'+post.shortcode+'.jpg' , 'rb') as f:
                                        bot.send_photo(chat_id=chatId, photo=f) #send image
                                        if post.caption == None:
                                            bot.sendMessage(chat_id=chatId, parse_mode='HTML', text=f'<b>{post.owner_username}:</b> None')
                                        else: #send post description
                                            bot.sendMessage(chat_id=chatId, parse_mode='HTML', text=f'<b>{post.owner_username}:</b> {post.caption}')
                                        
                                        break
                                except:
                                    pass                    
            
                logger.info('Next profile')                    

        except:
            pass



if __name__ == "__main__":
    myBot = telegram.Bot(token=TOKEN) #connect with telegram bot

updater = Updater(myBot.token, use_context=True) #to get info sent to the bot
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", getStart)) #set command

updater.start_polling()
print('BOT RUNNING')
updater.idle()

