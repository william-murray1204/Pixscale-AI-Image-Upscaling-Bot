#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from telebot import TeleBot, types
from pixscale_db import DBHelper
from datetime import datetime
from logging import getLogger
from traceback import format_exc
from telebot.types import LabeledPrice
from telebot import apihelper
from sys import getsizeof
import requests
from PIL import Image, UnidentifiedImageError
from requests.exceptions import ConnectionError, ReadTimeout


# Retrieves sensitive data from .env file
load_dotenv()
PIXSCALE_API_KEY = os.getenv('PIXSCALE_API_KEY')

EDWIN_API_KEY = os.getenv('EDWIN_API_KEY')
ADMIN_CHATID = os.getenv('ADMIN_CHATID')

STRIPE_PROVIDER_TOKEN = os.getenv('STRIPE_PROVIDER_TOKEN')

bot = TeleBot(PIXSCALE_API_KEY)
prices = [LabeledPrice(label='Unlimited Annual Access', amount=100)]
logger = getLogger()
tickIcon = u"\u2714"

# Create the MySQL pool
db = DBHelper()

# Sends Telegram notifications


def notifications(message_content):
    url = f"https://api.telegram.org/bot{EDWIN_API_KEY}"
    params = {"chat_id": ADMIN_CHATID, "text": message_content}
    r = requests.get(url + "/sendMessage", params=params)

# Main function


def main():
    while True:
        try:
            # Logs errors to the 'pixscale_error_log' table
            def error_log(func, error, userID):
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                db.log_error(dt_string, func, error, userID)

            # Creates fileOutput settings button
            def make_fileOutput_keyboard(userID):
                markup = types.InlineKeyboardMarkup()
                settings = db.retrieve_user_settings(userID)
                output_format = settings[0]
                if output_format == 'Auto':
                    autoIcon = tickIcon + " "
                    pngIcon = ""
                    jpgIcon = ""
                    webpIcon = ""
                elif output_format == 'png':
                    autoIcon = ""
                    pngIcon = tickIcon + " "
                    jpgIcon = ""
                    webpIcon = ""
                elif output_format == 'jpg':
                    autoIcon = ""
                    pngIcon = ""
                    jpgIcon = tickIcon + " "
                    webpIcon = ""
                else:
                    autoIcon = ""
                    pngIcon = ""
                    jpgIcon = ""
                    webpIcon = tickIcon + " "

                markup.add(types.InlineKeyboardButton(
                    text=f'{pngIcon}png', callback_data="outputFormat,png"),
                    types.InlineKeyboardButton(text=f'{jpgIcon}jpg', callback_data="outputFormat,jpg"),
                    types.InlineKeyboardButton(text=f'{webpIcon}webp', callback_data="outputFormat,webp"),
                    types.InlineKeyboardButton(text=f"{autoIcon}Auto", callback_data="outputFormat,Auto"))
                return markup

            # Creates upsamplingScale settings button
            def make_upsamplingScale_keyboard(userID):
                markup = types.InlineKeyboardMarkup()
                settings = db.retrieve_user_settings(userID)
                upsamplingScale = settings[1]
                if upsamplingScale == 2.0:
                    onexIcon = ""
                    twoxIcon = tickIcon + " "
                    threexIcon = ""
                    fourxIcon = ""
                    customxIcon = ""
                    customValue = ""
                elif upsamplingScale == 3.0:
                    onexIcon = ""
                    twoxIcon = ""
                    threexIcon = tickIcon + " "
                    fourxIcon = ""
                    customxIcon = ""
                    customValue = ""
                elif upsamplingScale == 4.0:
                    onexIcon = ""
                    twoxIcon = ""
                    threexIcon = ""
                    fourxIcon = tickIcon + " "
                    customxIcon = ""
                    customValue = ""
                elif upsamplingScale == 0.5:
                    onexIcon = tickIcon + " "
                    twoxIcon = ""
                    threexIcon = ""
                    fourxIcon = ""
                    customxIcon = ""
                    customValue = ""
                else:
                    onexIcon = ""
                    twoxIcon = ""
                    threexIcon = ""
                    fourxIcon = ""
                    customxIcon = tickIcon + " "
                    customValue = f" - {upsamplingScale}"
                markup.add(
                    types.InlineKeyboardButton(
                        text=f'{onexIcon}0.5x', callback_data="upsamplingScale,0.5"),
                    types.InlineKeyboardButton(
                        text=f"{twoxIcon}2x", callback_data="upsamplingScale,2"),
                    types.InlineKeyboardButton(
                        text=f'{threexIcon}3x', callback_data="upsamplingScale,3"),
                    types.InlineKeyboardButton(
                        text=f'{fourxIcon}4x', callback_data="upsamplingScale,4"),
                    types.InlineKeyboardButton(
                        text=f'{customxIcon}Custom{customValue}', callback_data="upsamplingScale,custom"))
                return markup

            # Creates animated settings button
            def make_animated_keyboard(userID):
                markup = types.InlineKeyboardMarkup()
                settings = db.retrieve_user_settings(userID)
                animated = settings[2]
                if animated == True:
                    onIcon = tickIcon + " "
                    offIcon = ""
                else:
                    onIcon = ""
                    offIcon = tickIcon + " "
                markup.add(types.InlineKeyboardButton(text=f"{onIcon}On", callback_data="animated,1"),
                           types.InlineKeyboardButton(
                    text=f'{offIcon}Off', callback_data="animated,0"))
                return markup

            # Creates facePresent settings button
            def make_facePresent_keyboard(userID):
                markup = types.InlineKeyboardMarkup()
                settings = db.retrieve_user_settings(userID)
                facePresent = settings[3]
                if facePresent == True:
                    onIcon = tickIcon + " "
                    offIcon = ""
                else:
                    onIcon = ""
                    offIcon = tickIcon + " "
                markup.add(types.InlineKeyboardButton(text=f"{onIcon}On", callback_data="facePresent,1"),
                           types.InlineKeyboardButton(
                    text=f'{offIcon}Off', callback_data="facePresent,0"))
                return markup

            # Handles the '/settings' message sent to the bot
            @bot.message_handler(commands=['settings'])
            def handle_command_adminwindow(message):
                try:
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    bot.send_message(chat_id=message.chat.id,
                                     text="File output format:",
                                     reply_markup=make_fileOutput_keyboard(
                                         message.chat.id),
                                     parse_mode='HTML')
                    bot.send_message(chat_id=message.chat.id,
                                     text="File upsampling scale:",
                                     reply_markup=make_upsamplingScale_keyboard(
                                         message.chat.id),
                                     parse_mode='HTML')
                    bot.send_message(chat_id=message.chat.id,
                                     text="Specialised animated image enhancment:",
                                     reply_markup=make_animated_keyboard(
                                         message.chat.id),
                                     parse_mode='HTML')
                    bot.send_message(chat_id=message.chat.id,
                                     text="Specialised human face enhancment:",
                                     reply_markup=make_facePresent_keyboard(
                                         message.chat.id),
                                     parse_mode='HTML')
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(commands=['settings']) \n\n{format_exc()}")
                    error_log("settings", format_exc(), message.chat.id)

            # Handles the settings buttons being pressed
            @bot.callback_query_handler(func=lambda call: True)
            def handle_query(call):
                try:
                    try:
                        callback = (call.data).split(',')
                        if callback[0] == "outputFormat":
                            db.modify_user_settings(
                                callback[1], None, None, None, call.message.chat.id)
                            bot.edit_message_text(chat_id=call.message.chat.id,
                                                  text="File output format:",
                                                  message_id=call.message.message_id,
                                                  reply_markup=make_fileOutput_keyboard(
                                                      call.message.chat.id),
                                                  parse_mode='HTML')
                        if callback[0] == "upsamplingScale":
                            if callback[1] == 'custom':
                                def custom(message):
                                    sent = bot.send_message(
                                        call.message.chat.id, 'Enter an upscale ratio larger than 0 and smaller than 4. A 10x10 pixel image and an upscale ratio of 2 will output a 20x20 pixel image. All images are enhanced regardless of the upscale ratio therefore a value of 1 will maintain the original dimensions.')
                                    bot.register_next_step_handler(
                                        sent, response)

                                def response(message):
                                    try:
                                        text = float(message.text)
                                        if text >= 0.01 and text <= 4:
                                            rounded_number = format(
                                                text, '.2f')
                                            db.modify_user_settings(None, float(
                                                rounded_number), None, None, message.chat.id)
                                            bot.send_message(
                                                message.chat.id, f"Upscaling ratio set to {str(rounded_number)}")
                                            bot.edit_message_text(chat_id=call.message.chat.id,
                                                                  text="File upscale ratio:",
                                                                  message_id=call.message.message_id,
                                                                  reply_markup=make_upsamplingScale_keyboard(
                                                                      call.message.chat.id),
                                                                  parse_mode='HTML')
                                        else:
                                            raise ValueError
                                    except ValueError:
                                        bot.send_message(
                                            message.chat.id, f"Invalid input, value must be a number larger than 0 and smaller than 4!")
                                custom(call.message)

                            else:
                                db.modify_user_settings(None, float(
                                    callback[1]), None, None, call.message.chat.id)
                                bot.edit_message_text(chat_id=call.message.chat.id,
                                                      text="File upscale ratio:",
                                                      message_id=call.message.message_id,
                                                      reply_markup=make_upsamplingScale_keyboard(
                                                          call.message.chat.id),
                                                      parse_mode='HTML')
                        if callback[0] == "animated":
                            db.modify_user_settings(
                                None, None, int(callback[1]), None, call.message.chat.id)
                            bot.edit_message_text(chat_id=call.message.chat.id,
                                                  text="Animated image enhancment:",
                                                  message_id=call.message.message_id,
                                                  reply_markup=make_animated_keyboard(
                                                      call.message.chat.id), parse_mode='HTML')
                        if callback[0] == "facePresent":
                            db.modify_user_settings(
                                None, None, None, int(callback[1]), call.message.chat.id)
                            bot.edit_message_text(chat_id=call.message.chat.id,
                                                  text="Human face enhancment:",
                                                  message_id=call.message.message_id,
                                                  reply_markup=make_facePresent_keyboard(
                                                      call.message.chat.id),
                                                  parse_mode='HTML')
                    except apihelper.ApiTelegramException:
                        pass
                except:
                    bot.send_message(
                        call.message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {call.message.chat.id}): \n\nIN FUNCTION = @bot.callback_query_handler(func=lambda call: True)) \n\n{format_exc()}")
                    error_log("handle_query", format_exc(),
                              call.message.chat.id)

            # Handles the '/start' message sent to the bot
            @bot.message_handler(commands=['start'])
            def start(message):
                try:
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    bot.send_message(
                        message.chat.id, "Welcome to Pixscale! Set your parameters using /settings, send us an image and our AI will rescale and increase its resolution accordingly. \n\nYou can control the Pixscale bot by sending these commands:\n\n/help - list this bot’s commands\n/buy - purchase a subscription to our service\n/settings - modify the image enhancement settings\n/terms - see our Privacy Policy and Terms & Conditions\n/feedback - send us your feedback on how we can improve our services\n\n• For the highest quality results, we suggest sending images without compression on the desktop Telegram application.")
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(commands=['start']) \n\n{format_exc()}")
                    error_log("start", format_exc(), message.chat.id)

            # Handles the '/feedback' message sent to the bot
            @bot.message_handler(commands=['feedback'])
            def feedback(message):
                try:
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    sent = bot.send_message(
                        message.chat.id, 'Please provide us with your feedback.')
                    bot.register_next_step_handler(sent, response)
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(commands=['feedback']) \n\n{format_exc()}")
                    error_log("feedback", format_exc(), message.chat.id)

            def response(message):
                try:
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    db.add_user_feedback(
                        dt_string, message.text, message.chat.id)
                    bot.send_message(
                        message.chat.id, "Thank you!\nFor further assistance, please contact us at pixscalecontact@gmail.com.")
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(commands=['feedback']) \n\n{format_exc()}")
                    error_log("feedback", format_exc(), message.chat.id)

            # Handles the '/terms' message sent to the bot
            @bot.message_handler(commands=['terms'])
            def terms(message):
                try:
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    bot.send_message(
                        message.chat.id, "Thank you for using Pixscale's Image Enhancement Bot. By using our services you understand and agree that:\n\n1. At Pixscale, we value your privacy. Pixscale DOES NOT download or save any of your images nor do we save or utilise your personal data for any reason.\n2. We are not responsible for any copyright/legal issues you may encounter from the use/publishing of images enhanced by our service.\n3. If you experience any problems with our bot, have any questions or suggestions, or require assistance in any other way, please contact our support email at pixscalecontact@gmail.com. We will normally get back to you within 1-5 working days. Thank you for your patience.\n4. If you would like to request a refund or dispute a transaction, please contact us at pixscalecontact@gmail.com with the relevant details.")
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(commands=['terms']) \n\n{format_exc()}")
                    error_log("terms", format_exc(), message.chat.id)

            # Handles the '/help' message sent to the bot
            @bot.message_handler(commands=['help'])
            def help(message):
                try:
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    bot.send_message(
                        message.chat.id, "You can control the Pixscale bot by sending these commands:\n\n/help - list this bot’s commands\n/buy - purchase a subscription to our service\n/settings - modify the image enhancement settings\n/terms - see our Privacy Policy and Terms & Conditions\n/feedback - send us your feedback on how we can improve our services")
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(commands=['help']) \n\n{format_exc()}")
                    error_log("help", format_exc(), message.chat.id)

            # Handles the '/buy' message sent to the bot
            @bot.message_handler(commands=['buy'])
            def buy(message):
                try:
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)

                    if db.check_user_status(0, message.chat.id) == True or db.check_user_status(2, message.chat.id) == True:
                        # PAYMENT >>>>
                        bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Pixscale gives all of its users 10 free image enhancements to test out our service. For a year of unlimited image enhancments, please consider upgrading to an Unlimited Annual Access subscription.',
                                         'NEW_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                    elif db.payment_outdated(dt_string, message.chat.id) == True:
                        db.update_user_status(2, message.chat.id)
                        # PAYMENT >>>>
                        bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your Unlimited Annual Access Subscription has come to an end. Please consider renewing your subscription for continued access to our services.',
                                         'RENEWAL_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                    else:
                        sub_len = db.check_subscription_length(
                            dt_string, message.chat.id)
                        bot.send_message(
                            message.chat.id, "You already have a subscription to our service with " + sub_len + " days remaining.")
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(commands=['buy']) \n\n{format_exc()}")
                    error_log("buy", format_exc(), message.chat.id)

            # Handles the '/giveuserid' message sent to the bot
            @bot.message_handler(commands=['giveuserid'])
            def giveuserid(message):
                try:
                    bot.send_message(
                        message.chat.id, "Your user ID is: " + str(message.chat.id))
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (giveuserid = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(commands=['giveuserid']) \n\n{format_exc()}")
                    error_log("giveuserid", format_exc(), message.chat.id)


            # Handles any other random text sent to the bot
            @bot.message_handler(content_types=['text'])
            def text(message):
                try:
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    bot.send_message(
                        message.chat.id, "Welcome to Pixscale! Set your parameters using /settings, send us an image and our AI will rescale and increase its resolution accordingly. \n\nYou can control the Pixscale bot by sending these commands:\n\n/help - list this bot’s commands\n/buy - purchase a subscription to our service\n/settings - modify the image enhancement settings\n/terms - see our Privacy Policy and Terms & Conditions\n/feedback - send us your feedback on how we can improve our services\n\n• For the highest quality results, we suggest sending images without compression on the desktop Telegram application.")
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(content_types=['text']) \n\n{format_exc()}")
                    error_log("text", format_exc(), message.chat.id)

            # Handles stickers sent to the bot
            @bot.message_handler(content_types=['sticker'])
            def text(message):
                try:
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    # Check if sticker is webp file or sticker
                    if message.sticker.is_animated is False and message.sticker.is_video == False:

                        if db.check_user_status(1, message.chat.id) == True:
                            if db.payment_outdated(dt_string, message.chat.id) == True:
                                db.update_user_status(2, message.chat.id)
                                # PAYMENT >>>>
                                bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your Unlimited Annual Access Subscription has come to an end. Please consider renewing your subscription for continued access to our services.',
                                                'RENEWAL_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                            else:
                                # Member Access >>>>
                                fileID = message.sticker.file_id
                                file_info = bot.get_file(fileID)
                                downloaded_file = bot.download_file(
                                    file_info.file_path)

                                # Calculates the file size in bytes
                                fileSize = getsizeof(downloaded_file)

                                if fileSize < 2150000:
                                    db.add_paid_action(
                                        dt_string, 1, message.chat.id)

                                    if not os.path.exists("image_queue"):
                                        os.mkdir("image_queue")

                                    image_path = "image_queue/" + \
                                        f'{fileID}_{message.chat.id}.webp'

                                    with open(image_path, 'wb') as new_file:
                                        new_file.write(downloaded_file)

                                    # Calculates the old and the new image dimensions
                                    try:
                                        foo = Image.open(image_path)
                                        dimensions = foo.size
                                        user_settings_array = db.retrieve_user_settings(
                                            message.chat.id)
                                        upsampling_scale = user_settings_array[1]
                                        img_len = int(
                                            float(dimensions[1]) * float(upsampling_scale))
                                        img_wid = int(
                                            float(dimensions[0]) * float(upsampling_scale))

                                        if upsampling_scale == 1:
                                            bot.send_message(
                                                message.chat.id, f"Enhancing image quality...")
                                        else:
                                            bot.send_message(
                                                message.chat.id, f"Enhancing & rescaling image from {dimensions[0]}x{dimensions[1]} to {img_wid}x{img_len} pixels...")

                                        # Sends image and details to database which is used by code running on seperate thread
                                        # that handles the image processing and user queue then sends the message back to the user to prevent blocking of the main thread
                                        db.add_image_to_queue(
                                            dt_string, fileID, None, fileSize, "webp", message.chat.id)
                                    except UnidentifiedImageError:
                                        bot.send_message(
                                            message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                                        if os.path.exists(image_path):
                                            os.remove(image_path)

                                else:
                                    bot.send_message(
                                        message.chat.id, f"The image you sent is too large to process. Please send an image under 2mb.")

                        elif db.check_user_status(0, message.chat.id) == True:
                            if db.check_trial_status(message.chat.id) == True:
                                if db.check_free_actions(message.chat.id) == True:
                                    # Free Trial Access >>>>

                                    fileID = message.sticker.file_id
                                    file_info = bot.get_file(fileID)
                                    downloaded_file = bot.download_file(
                                        file_info.file_path)

                                    # Calculates the file size in bytes
                                    fileSize = getsizeof(downloaded_file)

                                    if fileSize < 2150000:
                                        db.add_free_action(
                                            dt_string, 1, message.chat.id)

                                        if not os.path.exists("image_queue"):
                                            os.mkdir("image_queue")

                                        image_path = "image_queue/" + \
                                            f'{fileID}_{message.chat.id}.webp'

                                        with open(image_path, 'wb') as new_file:
                                            new_file.write(downloaded_file)

                                        # Calculates the old and the new image dimensions
                                        try:
                                            foo = Image.open(image_path)
                                            dimensions = foo.size
                                            user_settings_array = db.retrieve_user_settings(
                                                message.chat.id)
                                            upsampling_scale = user_settings_array[1]
                                            img_len = int(
                                                float(dimensions[1]) * float(upsampling_scale))
                                            img_wid = int(
                                                float(dimensions[0]) * float(upsampling_scale))

                                            if upsampling_scale == 1:
                                                bot.send_message(
                                                    message.chat.id, f"Enhancing image quality...")
                                            else:
                                                bot.send_message(
                                                    message.chat.id, f"Enhancing & rescaling image from {dimensions[0]}x{dimensions[1]} to {img_wid}x{img_len} pixels...")

                                            # Sends image and details to database which is used by code running on seperate thread
                                            # that handles the image processing and user queue then sends the message back to the user to prevent blocking of the main thread
                                            db.add_image_to_queue(
                                                dt_string, fileID, None, fileSize, "webp", message.chat.id)
                                        except UnidentifiedImageError:
                                            bot.send_message(
                                                message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                                            if os.path.exists(image_path):
                                                os.remove(image_path)

                                    else:
                                        bot.send_message(
                                            message.chat.id, f"The image you sent is too large to process. Please send an image under 2mb.")

                                else:
                                    db.format_user_trial(message.chat.id)
                                    # PAYMENT >>>>
                                    bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your 10 free image enhancements have run out. Please consider upgrading to our Unlimited Annual Access Service.',
                                                    'NEW_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                            else:
                                # PAYMENT >>>>
                                bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your 10 free image enhancements have run out. Please consider upgrading to our Unlimited Annual Access Service.',
                                                'NEW_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                        else:
                            # PAYMENT >>>>
                            bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your Unlimited Annual Access Subscription has come to an end. Please consider renewing your subscription for continued access to our services.',
                                            'RENEWAL_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')

                    # If the image is not a webp file then user is warned that image format is not supported
                    else:
                        bot.send_message(
                            message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(content_types=['sticker']) \n\n{format_exc()}")
                    error_log("sticker", format_exc(), message.chat.id)

            # Handles uncompressed audio sent to the bot
            @bot.message_handler(content_types=['audio'])
            def text(message):
                try:
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    bot.send_message(
                        message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(content_types=['audio']) \n\n{format_exc()}")
                    error_log("audio", format_exc(), message.chat.id)

            # Handles compressed video sent to the bot
            @bot.message_handler(content_types=['video'])
            def text(message):
                try:
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    bot.send_message(
                        message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(content_types=['video']) \n\n{format_exc()}")
                    error_log("video", format_exc(), message.chat.id)

            # Handles all uncompressed files sent to the bot
            @bot.message_handler(content_types=['document'])
            def text(message):
                try:
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    fileType = message.document.mime_type.split('/')
                    if fileType[0] != 'image':
                        bot.send_message(
                            message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                    else:

                        if db.check_user_status(1, message.chat.id) == True:
                            if db.payment_outdated(dt_string, message.chat.id) == True:
                                db.update_user_status(2, message.chat.id)
                                # PAYMENT >>>>
                                bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your Unlimited Annual Access Subscription has come to an end. Please consider renewing your subscription for continued access to our services.',
                                                 'RENEWAL_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                            else:
                                # Member Access >>>>
                                # Gets the fileId and the byte data of the image
                                fileID = message.document.file_id
                                file_info = bot.get_file(fileID)
                                rawname = message.document.file_name
                                downloaded_file = bot.download_file(
                                    file_info.file_path)

                                # Splits the files name and extension then determines what to store the file extension as in the database
                                fileDetails = rawname.split('.')
                                extension = fileDetails[1]
                                if extension == 'PNG':
                                    extension = 'png'
                                elif extension == 'png':
                                    extension = 'png'
                                else:
                                    extension = 'jpg'

                                # Calculates the file size in bytes
                                fileSize = getsizeof(downloaded_file)

                                if fileSize < 2150000:

                                    db.add_paid_action(
                                        dt_string, 1, message.chat.id)

                                    if not os.path.exists("image_queue"):
                                        os.mkdir("image_queue")

                                    image_path = "image_queue/" + \
                                        f'{fileID}_{message.chat.id}.{extension}'

                                    with open(image_path, 'wb') as new_file:
                                        new_file.write(downloaded_file)

                                    # Calculates the old and the new image dimensions
                                    try:
                                        foo = Image.open(image_path)
                                        dimensions = foo.size
                                        user_settings_array = db.retrieve_user_settings(
                                            message.chat.id)
                                        upsampling_scale = user_settings_array[1]
                                        img_len = int(
                                            float(dimensions[1]) * float(upsampling_scale))
                                        img_wid = int(
                                            float(dimensions[0]) * float(upsampling_scale))

                                        if upsampling_scale == 1:
                                            bot.send_message(
                                                message.chat.id, f"Enhancing the image quality of {rawname}...")
                                        else:
                                            bot.send_message(
                                                message.chat.id, f"Enhancing & rescaling {rawname} from {dimensions[0]}x{dimensions[1]} to {img_wid}x{img_len} pixels...")
                                        
                                        # Sends image and details to database which is used by code running on seperate thread
                                        # that handles the image processing and user queue then sends the message back to the user to prevent blocking of the main thread
                                        db.add_image_to_queue(
                                            dt_string, fileID, fileDetails[0], fileSize, extension, message.chat.id)
                                    except UnidentifiedImageError:
                                        bot.send_message(
                                            message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                                        if os.path.exists(image_path):
                                            os.remove(image_path)
                                    
                                else:
                                    bot.send_message(
                                        message.chat.id, f"The image {rawname} is too large to process. Please send an image under 2mb.")

                        elif db.check_user_status(0, message.chat.id) == True:
                            if db.check_trial_status(message.chat.id) == True:
                                if db.check_free_actions(message.chat.id) == True:
                                    # Free Trial Access >>>>
                                    fileID = message.document.file_id
                                    file_info = bot.get_file(fileID)
                                    rawname = message.document.file_name
                                    downloaded_file = bot.download_file(
                                        file_info.file_path)

                                    # Splits the files name and extension then determines what to store the file extension as in the database
                                    fileDetails = rawname.split('.')
                                    extension = fileDetails[1]
                                    if extension == 'PNG':
                                        extension = 'png'
                                    elif extension == 'png':
                                        extension = 'png'
                                    else:
                                        extension = 'jpg'

                                    # Calculates the file size in bytes
                                    fileSize = getsizeof(downloaded_file)

                                    if fileSize < 2150000:
                                        db.add_free_action(
                                            dt_string, 1, message.chat.id)

                                        if not os.path.exists("image_queue"):
                                            os.mkdir("image_queue")

                                        image_path = "image_queue/" + \
                                            f'{fileID}_{message.chat.id}.{extension}'

                                        with open(image_path, 'wb') as new_file:
                                            new_file.write(downloaded_file)

                                        # Calculates the old and the new image dimensions
                                        try:
                                            foo = Image.open(image_path)
                                            dimensions = foo.size
                                            user_settings_array = db.retrieve_user_settings(
                                                message.chat.id)
                                            upsampling_scale = user_settings_array[1]
                                            img_len = int(
                                                float(dimensions[1]) * float(upsampling_scale))
                                            img_wid = int(
                                                float(dimensions[0]) * float(upsampling_scale))

                                            if upsampling_scale == 1:
                                                bot.send_message(
                                                    message.chat.id, f"Enhancing the image quality of {rawname}...")
                                            else:
                                                bot.send_message(
                                                    message.chat.id, f"Enhancing & rescaling {rawname} from {dimensions[0]}x{dimensions[1]} to {img_wid}x{img_len} pixels...")

                                            # Sends image and details to database which is used by code running on seperate thread
                                            # that handles the image processing and user queue then sends the message back to the user to prevent blocking of the main thread
                                            db.add_image_to_queue(
                                                dt_string, fileID, fileDetails[0], fileSize, extension, message.chat.id)
                                        except UnidentifiedImageError:
                                            bot.send_message(
                                                message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                                            if os.path.exists(image_path):
                                                os.remove(image_path)

                                    else:
                                        bot.send_message(
                                            message.chat.id, f"The image {rawname} is too large to process. Please send an image under 2mb.")

                                else:
                                    db.format_user_trial(message.chat.id)
                                    # PAYMENT >>>>
                                    bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your 10 free image enhancements have run out. Please consider upgrading to our Unlimited Annual Access Service.',
                                                     'NEW_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                            else:
                                # PAYMENT >>>>
                                bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your 10 free image enhancements have run out. Please consider upgrading to our Unlimited Annual Access Service.',
                                                 'NEW_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                        else:
                            # PAYMENT >>>>
                            bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your Unlimited Annual Access Subscription has come to an end. Please consider renewing your subscription for continued access to our services.',
                                             'RENEWAL_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(content_types=['document']) \n\n{format_exc()}")
                    error_log("document", format_exc(), message.chat.id)

            # Handles compressed photos sent to the bot

            @bot.message_handler(content_types=['photo'])
            def photo(message):
                try:
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    if db.check_user_exists_db(message.chat.id) == False:
                        db.add_user(dt_string, 0, 0, 0, message.chat.id)
                    if db.check_user_settings_exists_db(message.chat.id) == False:
                        db.add_user_setting(message.chat.id)
                    if db.check_user_status(1, message.chat.id) == True:
                        if db.payment_outdated(dt_string, message.chat.id) == True:
                            db.update_user_status(2, message.chat.id)
                            # PAYMENT >>>>
                            bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your Unlimited Annual Access Subscription has come to an end. Please consider renewing your subscription for continued access to our services.',
                                             'RENEWAL_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                        else:
                            # Member Access >>>>

                            fileID = message.photo[-1].file_id
                            file_info = bot.get_file(fileID)
                            downloaded_file = bot.download_file(
                                file_info.file_path)

                            # Calculates the file size in bytes
                            fileSize = getsizeof(downloaded_file)

                            if fileSize < 2150000:
                                db.add_paid_action(
                                    dt_string, 1, message.chat.id)

                                if not os.path.exists("image_queue"):
                                    os.mkdir("image_queue")

                                image_path = "image_queue/" + \
                                    f'{fileID}_{message.chat.id}.jpg'

                                with open(image_path, 'wb') as new_file:
                                    new_file.write(downloaded_file)

                                # Calculates the old and the new image dimensions
                                try:
                                    foo = Image.open(image_path)
                                    dimensions = foo.size
                                    user_settings_array = db.retrieve_user_settings(
                                        message.chat.id)
                                    upsampling_scale = user_settings_array[1]
                                    img_len = int(
                                        float(dimensions[1]) * float(upsampling_scale))
                                    img_wid = int(
                                        float(dimensions[0]) * float(upsampling_scale))

                                    if upsampling_scale == 1:
                                        bot.send_message(
                                            message.chat.id, f"Enhancing image quality...")
                                    else:
                                        bot.send_message(
                                            message.chat.id, f"Enhancing & rescaling image from {dimensions[0]}x{dimensions[1]} to {img_wid}x{img_len} pixels...")

                                    # Sends image and details to database which is used by code running on seperate thread
                                    # that handles the image processing and user queue then sends the message back to the user to prevent blocking of the main thread
                                    db.add_image_to_queue(
                                        dt_string, fileID, None, fileSize, "jpg", message.chat.id)

                                except UnidentifiedImageError:
                                    bot.send_message(
                                        message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                                    if os.path.exists(image_path):
                                        os.remove(image_path)

                            else:
                                bot.send_message(
                                    message.chat.id, f"The image you sent is too large to process. Please send an image under 2mb.")

                    elif db.check_user_status(0, message.chat.id) == True:
                        if db.check_trial_status(message.chat.id) == True:
                            if db.check_free_actions(message.chat.id) == True:
                                # Free Trial Access >>>>

                                fileID = message.photo[-1].file_id
                                file_info = bot.get_file(fileID)
                                downloaded_file = bot.download_file(
                                    file_info.file_path)

                                # Calculates the file size in bytes
                                fileSize = getsizeof(downloaded_file)

                                if fileSize < 2150000:
                                    db.add_free_action(
                                        dt_string, 1, message.chat.id)

                                    if not os.path.exists("image_queue"):
                                        os.mkdir("image_queue")

                                    image_path = "image_queue/" + \
                                        f'{fileID}_{message.chat.id}.jpg'

                                    with open(image_path, 'wb') as new_file:
                                        new_file.write(downloaded_file)

                                    # Calculates the old and the new image dimensions
                                    try:
                                        foo = Image.open(image_path)
                                        dimensions = foo.size
                                        user_settings_array = db.retrieve_user_settings(
                                            message.chat.id)
                                        upsampling_scale = user_settings_array[1]
                                        img_len = int(
                                            float(dimensions[1]) * float(upsampling_scale))
                                        img_wid = int(
                                            float(dimensions[0]) * float(upsampling_scale))

                                        if upsampling_scale == 1:
                                            bot.send_message(
                                                message.chat.id, f"Enhancing image quality...")
                                        else:
                                            bot.send_message(
                                                message.chat.id, f"Enhancing & rescaling image from {dimensions[0]}x{dimensions[1]} to {img_wid}x{img_len} pixels...")

                                        # Sends image and details to database which is used by code running on seperate thread
                                        # that handles the image processing and user queue then sends the message back to the user to prevent blocking of the main thread
                                        db.add_image_to_queue(
                                            dt_string, fileID, None, fileSize, "jpg", message.chat.id)
                                    except UnidentifiedImageError:
                                        bot.send_message(
                                            message.chat.id, "This file type is either not supported or formatted incorrectly. Please send us an image with the correct formatting.")
                                        if os.path.exists(image_path):
                                            os.remove(image_path)

                                else:
                                    bot.send_message(
                                        message.chat.id, f"The image you sent is too large to process. Please send an image under 2mb.")

                            else:
                                db.format_user_trial(message.chat.id)
                                # PAYMENT >>>>
                                bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your 10 free image enhancements have run out. Please consider upgrading to our Unlimited Annual Access Service.',
                                                 'NEW_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                        else:
                            # PAYMENT >>>>
                            bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your 10 free image enhancements have run out. Please consider upgrading to our Unlimited Annual Access Service.',
                                             'NEW_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')
                    else:
                        # PAYMENT >>>>
                        bot.send_invoice(message.chat.id, 'Unlimited Annual Access', 'Your Unlimited Annual Access Subscription has come to an end. Please consider renewing your subscription for continued access to our services.',
                                         'RENEWAL_SUBSCRIPTION', STRIPE_PROVIDER_TOKEN, 'usd', prices, is_flexible=False, max_tip_amount=5000, suggested_tip_amounts=[50, 100, 200, 500], start_parameter='subscription')

                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(content_types=['photo']) \n\n{format_exc()}")
                    error_log("photo", format_exc(), message.chat.id)

            # Handles a transaction by answering telegrams 'answer_pre_checkout_query'
            @bot.pre_checkout_query_handler(func=lambda query: True)
            def checkout(pre_checkout_query):
                bot.answer_pre_checkout_query(
                    pre_checkout_query.id, ok=True, error_message="There was an error processing your transaction, please try again in a few minutes.")

            # Handles a successful payment by updating the users payment status, adding a payment to the log and sending the user a message
            @bot.message_handler(content_types=['successful_payment'])
            def successful_payment(message):
                try:
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    db.update_user(now, dt_string, 1, 12, message.chat.id)
                    db.add_payment(dt_string, 12, 1.00, "stripe",
                                   "usd", message.chat.id)
                    db.format_user_trial(message.chat.id)
                    bot.send_message(
                        message.chat.id, 'Thanks for your payment! You now have one year of unlimited access to our Image Enhancement Service.')
                except:
                    bot.send_message(
                        message.chat.id, "There was an error connecting to Pixscale's servers. This likely means we are undergoing maintenance. We apologise for any inconvenience and ask you to please try again in a few minutes.")
                    notifications(
                        f"[USER ENCOUNTERED] Pixscale Error (userID = {message.chat.id}): \n\nIN FUNCTION = @bot.message_handler(content_types=['successful_payment']) \n\n{format_exc()}")
                    error_log("successful_payment",
                              format_exc(), message.chat.id)

            bot.polling()
        except (ConnectionError, ReadTimeout, TimeoutError):
            continue


# Error handler
while True:
    try:
        if __name__ == '__main__':
            main()
    except Exception as Argument:
        logger.warning(format_exc())
        notifications(
            f"[SERVER ENCOUNTERED] Pixscale Error: \n{format_exc()}")
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
