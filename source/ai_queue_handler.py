#!/usr/bin/env python3
from ai_upscaler.algorithm import algo
import os
from dotenv import load_dotenv
from telebot import TeleBot
from pixscale_db import DBHelper
from datetime import datetime
from logging import getLogger
from traceback import format_exc
from io import BytesIO
from cv2 import imencode
import torch
import requests
from PIL import Image
import numpy as np
from cv2 import COLOR_BGRA2RGBA, cvtColor
from time import sleep
from telebot.apihelper import ApiTelegramException

# Retrieves sensitive data from .env file
load_dotenv()
PIXSCALE_API_KEY = os.getenv('PIXSCALE_API_KEY')
EDWIN_API_KEY = os.getenv('EDWIN_API_KEY')
ADMIN_CHATID = os.getenv('ADMIN_CHATID')

bot = TeleBot(PIXSCALE_API_KEY)
logger = getLogger()

# Create the MySQL pool
db = DBHelper()

# Logs errors to the 'pixscale_error_log' table


def error_log(func, error, userID):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    db.log_error(dt_string, func, error, userID)

# Sends Telegram notifications


def notifications(message_content):
    url = f"https://api.telegram.org/bot{EDWIN_API_KEY}"
    params = {"chat_id": ADMIN_CHATID, "text": message_content}
    r = requests.get(url + "/sendMessage", params=params)


def run_ai(fileID, conversionAttempts, fileName, fileSize, fileExt, userID, dateTime):

    try:
        image_directory = (
            "image_queue/" + f'{str(fileID)}_{str(userID)}.{str(fileExt)}')
        # Checks that there has not already been more than 6 attempts to convert the image to avoid bottlenecks incase of constant errors
        if conversionAttempts < 6:
            # This section can be modified to change how many times there is an attempt to convert the image untill it gets put to the back of the queue by updating dateTime to now
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            if conversionAttempts >= 1:
                if conversionAttempts == 1:
                    bot.send_message(
                        userID, "This image is large and therefore may take longer to process. Please bear with us, thank you.")
                    tile_size = 600
                    torch.cuda.empty_cache()
                if conversionAttempts == 2:
                    tile_size = 400
                    torch.cuda.empty_cache()
                if conversionAttempts == 3:
                    tile_size = 200
                    torch.cuda.empty_cache()
                if conversionAttempts == 4:
                    tile_size = 100
                    torch.cuda.empty_cache()
                if conversionAttempts == 5:
                    tile_size = 50
                    torch.cuda.empty_cache()
                db.add_conversion_attempt(
                    dateTime, fileID, True, dt_string, userID)
            else:
                db.add_conversion_attempt(
                    dateTime, fileID, True, dt_string, userID)
                # The tile size is set to 0 for default
                tile_size = 0
            user_settings_array = db.retrieve_user_settings(userID)
            output_format = user_settings_array[0]
            upsampling_scale = user_settings_array[1]

            animated = user_settings_array[2]
            if animated == 0:
                animated = False
            else:
                animated = True
            facePresent = user_settings_array[3]
            if facePresent == 0:
                facePresent = False
            else:
                facePresent = True

            # determines the file extension format of the image (jpeg, png, etc)
            if output_format == "Auto":
                extension = fileExt
            else:
                extension = output_format

            filesname = fileName
            if filesname is None:
                filesname = fileID

            if upsampling_scale < 1:
            
                foo = Image.open(image_directory)
                dimensions = (foo.size)
                old_len = dimensions[1]
                old_wid = dimensions[0]

                new_len = int(old_len * upsampling_scale)
                new_wid = int(old_wid * upsampling_scale)

                foo = foo.resize((new_wid, new_len), Image.Resampling.LANCZOS)

                def img_format(img):
                    buffer = imencode(f'.{extension}', img)[1].tobytes()
                    return buffer

                numpyimg = np.array(foo)
                RGBimg = cvtColor(numpyimg, COLOR_BGRA2RGBA)
                resized_image = BytesIO(img_format(RGBimg))
                resized_image.name = f'Pixscaled_{filesname}.{extension}'

                # Send back the processed image to the user
                sendtry1 = 0
                while sendtry1 <= 3:
                    try:
                        sendtry1 += 1
                        bot.send_document(userID, document=resized_image, timeout=10000)
                    except ApiTelegramException:
                        sleep(0.2)
                        pass

                # Remove the image metadata from database queue and remove image from local directory storage
                if os.path.exists(image_directory):
                    os.remove(image_directory)
                db.remove_image_from_queue(dt_string, fileID, userID)

            else:

                def img_format(img):
                    buffer = imencode(f'.{extension}', img)[1].tobytes()
                    return buffer

                # Process the image using the ai and return the result unless there is a memory error in which case it will skip the next steps
                output = algo(tile_size, upsampling_scale,
                              animated, facePresent, image_directory)

                if type(output) is str:
                    pass
                else:
                    # Format the output from the ai as bytes and add a name to the file
                    imageFile = BytesIO(img_format(output))
                    imageFile.name = f'Pixscaled_{filesname}.{extension}'

                    # Send back the processed image to the user
                    sendtry = 0
                    while sendtry <= 3:
                        try:
                            sendtry += 1
                            bot.send_document(userID, document=imageFile, timeout=10000)
                        except ApiTelegramException:
                            sleep(0.2)
                            pass

                    # Remove the image metadat from database queue and remove image from local directory storage
                    if os.path.exists(image_directory):
                        os.remove(image_directory)
                    db.remove_image_from_queue(dt_string, fileID, userID)
        else:
            error_log('memory', format_exc(), userID)
            bot.send_message(
                userID, f"There was an error processing your image {fileName}. Please try again.")
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

            # Remove the image metadat from database queue and remove image from local directory storage
            if os.path.exists(image_directory):
                os.remove(image_directory)
            db.add_troubled_image(
                dt_string, fileID, fileName, fileSize, fileExt, userID)
            db.remove_image_from_queue(dateTime, fileID, userID)

    except RuntimeError:
        pass


def main():
    while True:
        try:
            try:
                latest = db.get_latest_queue_item()
                dateTime = latest[0]
                fileID = latest[1]
                fileName = latest[2]
                conversionAttempts = latest[3]
                fileSize = latest[4]
                fileExt = latest[5]
                userID = str(latest[6])
                run_ai(fileID, conversionAttempts,
                       fileName, fileSize, fileExt, userID, dateTime)
            except (RuntimeError, TypeError, UnboundLocalError):
                pass
        except:
            error_log('ai_que_handler.py', format_exc(), None)
            logger.warning(format_exc())
            notifications(
                f"[SERVER ENCOUNTERED] Pixscale Error: \n{format_exc()}")


if __name__ == '__main__':
    main()

