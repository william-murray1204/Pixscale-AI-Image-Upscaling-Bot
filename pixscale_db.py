#!/usr/bin/env python3
from mysql.connector import pooling
import pandas as pd
from dotenv import load_dotenv
import os

# Retrieves sensitive data from .env file
load_dotenv()
SERVER_IP = os.getenv('SERVER_IP')
DATABASE_PORT = int(os.getenv('DATABASE_PORT'))
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')
POOL_NAME = os.getenv('POOL_NAME')
POOL_SIZE = int(os.getenv('POOL_SIZE'))


class DBHelper:
    # Connects to the 'edwin_server' mysql database
    def __init__(self):
        self.cnxpool = pooling.MySQLConnectionPool(pool_name=POOL_NAME, pool_size=POOL_SIZE, pool_reset_session=True,
                                                    host=SERVER_IP, user=DATABASE_USER, passwd=DATABASE_PASSWORD, db=DATABASE_NAME, port=DATABASE_PORT, autocommit=True)

    # Creates the necessary pixscale tables if they do not already exist
    def setup(self):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)

        # Creates pixscale_free_actions table
        tblstmt = "CREATE TABLE IF NOT EXISTS pixscale_free_actions (dateTime DATETIME, action INTEGER, userID TEXT, id INTEGER AUTO_INCREMENT PRIMARY KEY)"
        cursor.execute(tblstmt)

        # Creates pixscale_paid_actions table
        tblstmt1 = "CREATE TABLE IF NOT EXISTS pixscale_paid_actions (dateTime DATETIME, action INTEGER, userID TEXT, id INTEGER AUTO_INCREMENT PRIMARY KEY)"
        cursor.execute(tblstmt1)

        # Creates pixscale_users table
        tblstmt2 = "CREATE TABLE IF NOT EXISTS pixscale_users (paymentDateTime DATETIME, paymentStatus INTEGER, paymentPeriod INTEGER, trialStatus INTEGER, userID TEXT, id INTEGER AUTO_INCREMENT PRIMARY KEY)"
        cursor.execute(tblstmt2)

        # Creates pixscale_payments table
        tblstmt3 = "CREATE TABLE IF NOT EXISTS pixscale_payments (paymentDateTime DATETIME, paymentPeriod INTEGER, paymentAmount FLOAT, paymentMethod TEXT, paymentBillingCountry TEXT, userID TEXT, id INTEGER AUTO_INCREMENT PRIMARY KEY)"
        cursor.execute(tblstmt3)

        # Creates pixscale_error_log table
        tblstmt4 = "CREATE TABLE IF NOT EXISTS pixscale_error_log (dateTime DATETIME, component TEXT, error TEXT, userID TEXT, id INTEGER AUTO_INCREMENT PRIMARY KEY)"
        cursor.execute(tblstmt4)

        # Creates pixscale_ai_image_queue table
        tblstmt5 = "CREATE TABLE IF NOT EXISTS pixscale_ai_image_queue (dateTime DATETIME, fileID TEXT, fileName TEXT, conversionAttempts INTEGER, fileSize FLOAT, fileExt TEXT, userID TEXT, id INTEGER AUTO_INCREMENT PRIMARY KEY)"
        cursor.execute(tblstmt5)

        # Creates pixscale_troubled_ai_images table
        tblstmt6 = "CREATE TABLE IF NOT EXISTS pixscale_troubled_ai_images (dateTime DATETIME, fileID TEXT, fileName TEXT, fileSize FLOAT, fileExt TEXT, userID TEXT, id INTEGER AUTO_INCREMENT PRIMARY KEY)"
        cursor.execute(tblstmt6)

        # Creates pixscale_user_settings table
        tblstmt7 = "CREATE TABLE IF NOT EXISTS pixscale_user_settings (outputFormat TEXT, upsamplingScale FLOAT, animated INTEGER, facePresent INTEGER, userID TEXT, id INTEGER AUTO_INCREMENT PRIMARY KEY)"
        cursor.execute(tblstmt7)

        # Creates pixscale_feedback table
        tblstmt8 = "CREATE TABLE IF NOT EXISTS pixscale_feedback (dateTime DATETIME, feedback TEXT, userID TEXT, id INTEGER AUTO_INCREMENT PRIMARY KEY)"
        cursor.execute(tblstmt8)

        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Adds an entry to the 'pixscale_free_actions' table
    def add_free_action(self, dateTime, action, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "INSERT INTO pixscale_free_actions (dateTime, action, userID) VALUES (%s, %s, %s)"
        args = (dateTime, action, userID)
        cursor.execute(stmt, args)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Adds an entry to the 'pixscale_payments' table
    def add_paid_action(self, dateTime, action, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "INSERT INTO pixscale_paid_actions (dateTime, action, userID) VALUES (%s, %s, %s)"
        args = (dateTime, action, userID)
        cursor.execute(stmt, args)

        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Adds a user to the 'pixscale_users' table
    def add_user(self, paymentDateTime, paymentStatus, paymentPeriod, trialStatus, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "INSERT INTO pixscale_users (paymentDateTime, paymentStatus, paymentPeriod, trialStatus, userID) VALUES (%s, %s, %s, %s, %s)"
        args = (paymentDateTime, paymentStatus,
                paymentPeriod, trialStatus, userID)
        cursor.execute(stmt, args)

        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Checks if a user given by the variable 'userID' already exists in the 'pixscale_users' table (Returns False if the user does not exist)
    def check_user_exists_db(self, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "SELECT userID FROM pixscale_users WHERE userID = (%s)"
        args = (userID,)
        cursor.execute(stmt, args)
        user = cursor.fetchone()
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()
        if user == None:
            return False
        else:
            return True

    # Checks a users payment status in the 'pixscale_users' table (Returns True or False depending on variable 'number')

    def check_user_status(self, number, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "SELECT paymentStatus FROM pixscale_users WHERE userID = (%s)"
        args = (userID,)
        cursor.execute(stmt, args)
        status = cursor.fetchone()[0]
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()
        if status == number:
            return True
        else:
            return False

    # Checks if a users payment status in the 'pixscale_users' table is outdated (Returns False if not outdated)
    def payment_outdated(self, now, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        pdtstmt = "SELECT paymentDateTime FROM pixscale_users WHERE userID = (%s)"
        ppstmt = "SELECT paymentPeriod FROM pixscale_users WHERE userID = (%s)"
        args = (userID,)
        cursor.execute(pdtstmt, args)
        paymentDateTime = pd.to_datetime(cursor.fetchone()[0])
        cursor.execute(ppstmt, args)
        paymentPeriod = cursor.fetchone()[0]
        nowtime = pd.to_datetime(now)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()
        if paymentDateTime <= nowtime <= paymentDateTime + pd.DateOffset(months=paymentPeriod):
            return False
        else:
            return True

    # Updates a users payment status in the 'pixscale_users' table with the variable 'Status'
    def update_user_status(self, Status, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "UPDATE pixscale_users SET paymentStatus = (%s) WHERE userID = (%s)"
        args = (Status, userID)
        cursor.execute(stmt, args)

        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Updates a users payment date, payment status and payment period in the 'pixscale_users' to the variables specified (payment period is added to the current payment period incase multiple purchases are made)
    def update_user(self, now, DateTime, Status, Period, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Checks if the payment is outdated
        pdtstmt1 = "SELECT paymentDateTime FROM pixscale_users WHERE userID = (%s)"
        ppstmt1 = "SELECT paymentPeriod FROM pixscale_users WHERE userID = (%s)"
        args1 = (userID,)
        cursor.execute(pdtstmt1, args1)
        paymentDateTime = pd.to_datetime(cursor.fetchone()[0])
        cursor.execute(ppstmt1, args1)
        paymentPeriod = cursor.fetchone()[0]
        nowtime = pd.to_datetime(now)
        # If the payment is outdated, the payment period is reset to 0 and the date isnt updated
        if paymentDateTime <= nowtime <= paymentDateTime + pd.DateOffset(months=paymentPeriod):
            usedsubtime = nowtime - paymentDateTime
            newPeriod = (int(paymentPeriod) + int(Period))
            newDateTime = paymentDateTime - usedsubtime
            stmt = "UPDATE pixscale_users SET paymentDateTime = (%s), paymentStatus = (%s), paymentPeriod = (%s) WHERE userID = (%s)"
            args = (newDateTime, Status, newPeriod, userID)
            cursor.execute(stmt, args)

        else:
            newPeriod = int(Period)
            stmt = "UPDATE pixscale_users SET paymentDateTime = (%s), paymentStatus = (%s), paymentPeriod = (%s) WHERE userID = (%s)"
            args = (DateTime, Status, newPeriod, userID)
            cursor.execute(stmt, args)

        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Adds a payment and its details to the 'pixscale_payments' table

    def add_payment(self, paymentDateTime, paymentPeriod, paymentAmount, paymentMethod, paymentBillingCountry, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "INSERT INTO pixscale_payments (paymentDateTime,  paymentPeriod, paymentAmount, paymentMethod, paymentBillingCountry, userID) VALUES (%s, %s, %s, %s, %s, %s)"
        args = (paymentDateTime, paymentPeriod, paymentAmount,
                paymentMethod, paymentBillingCountry, userID)
        cursor.execute(stmt, args)

        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Checks the 'pixscale_free_actions' table for the number of free actions a user has performed (Returns False has performed all 10 of their free actions)
    def check_free_actions(self, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "SELECT SUM(action) FROM pixscale_free_actions WHERE userID = (%s)"
        args = (userID,)
        cursor.execute(stmt, args)
        sum = cursor.fetchone()[0]
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()
        if sum is None:
            return True
        else:
            if sum < 10:
                return True
            else:
                return False

    # Checks 'pixscale_users' table for the status of a user (Returns True if the user is a trial user)
    def check_trial_status(self, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "SELECT trialStatus FROM pixscale_users WHERE userID = (%s)"
        args = (userID,)
        cursor.execute(stmt, args)
        status = cursor.fetchone()[0]
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()
        if status == 0:
            return True
        else:
            return False

    # Updates the 'pixscale_users' table with the trial status of '1' given a userID and deletes the all of that users actions from the 'pixscale_free_actions' table
    def format_user_trial(self, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)

        # Execute the query
        updtstmt = "UPDATE pixscale_users SET trialStatus = 1 WHERE userID = (%s)"
        dltstmt = "DELETE FROM pixscale_free_actions WHERE userID = (%s)"
        args = (userID,)
        cursor.execute(updtstmt, args)
        cursor.execute(dltstmt, args)

        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Returns the amount of time left a user has until their payment period ends
    def check_subscription_length(self, now, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)

        # Execute the query
        pdtstmt = "SELECT paymentDateTime FROM pixscale_users WHERE userID = (%s)"
        ppstmt = "SELECT paymentPeriod FROM pixscale_users WHERE userID = (%s)"
        args = (userID,)
        cursor.execute(pdtstmt, args)
        paydate = cursor.fetchone()[0]
        paymentDateTime = pd.to_datetime(paydate)
        cursor.execute(ppstmt, args)
        paymentPeriod = cursor.fetchone()[0]
        nowtime = pd.to_datetime(now)
        subtimeleft = (paymentDateTime +
                       pd.DateOffset(months=paymentPeriod)) - nowtime
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()
        return str(subtimeleft.days)

    # Logs into the 'pixscale_error_log' table an error message including the dateTime, component from which the error came from, the full error message and the userID who encountered the error
    def log_error(self, dateTime, component, error, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "INSERT INTO pixscale_error_log (dateTime, component, error, userID) VALUES (%s, %s, %s, %s)"
        args = (dateTime, component, error, userID)
        cursor.execute(stmt, args)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Adds an images details to the 'pixscale_ai_image_queue' table
    def add_image_to_queue(self, dateTime, fileID, fileName, fileSize, fileExt, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "INSERT INTO pixscale_ai_image_queue (dateTime, fileID, fileName, conversionAttempts, fileSize, fileExt, userID) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        args = (dateTime, fileID, fileName, 0, fileSize, fileExt, userID)
        cursor.execute(stmt, args)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Removes an image from the 'pixscale_ai_image_queue' table
    def remove_image_from_queue(self, dateTime, fileID, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "DELETE FROM pixscale_ai_image_queue WHERE dateTime = (%s) and fileID = (%s) and userID = (%s)"
        args = (dateTime, fileID, userID)
        cursor.execute(stmt, args)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Returns the latest image from the "pixscale_ai_image_queue" table by oldest dateTime
    def get_latest_queue_item(self):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "SELECT * FROM pixscale_ai_image_queue ORDER BY dateTime ASC LIMIT 1"
        cursor.execute(stmt)
        image_data = cursor.fetchone()
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()
        return image_data

    # Adds a conversion attempt to an image in the "pixscale_ai_image_queue" table and if resetTime is specified as True, the datetime will be set to now to put it at the back of the queue
    def add_conversion_attempt(self, dateTime, fileID, resetTime, now, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        updt = "UPDATE pixscale_ai_image_queue SET conversionAttempts = conversionAttempts + 1 WHERE dateTime = (%s) and fileID = (%s) and userID = (%s)"
        args = (dateTime, fileID, userID)
        cursor.execute(updt, args)
        if resetTime == True:
            updt2 = "UPDATE pixscale_ai_image_queue SET dateTime = (%s) WHERE dateTime = (%s) and fileID = (%s) and userID = (%s)"
            args2 = (now, dateTime, fileID, userID)
            cursor.execute(updt2, args2)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # If there are more than 3 conversion attempts on an image, this image is 'troubled' and is added to the pixscale_troubled_ai_images table for investigation
    def add_troubled_image(self, dateTime, fileID, fileName, fileSize, fileExt, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "INSERT INTO pixscale_troubled_ai_images (dateTime, fileID, fileName, fileSize, fileExt, userID) VALUES (%s, %s, %s, %s, %s, %s)"
        args = (dateTime, fileID, fileName, fileSize, fileExt, userID)
        cursor.execute(stmt, args)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Adds a user with defualt settings to the pixscale_user_settings table
    def add_user_setting(self, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "INSERT INTO pixscale_user_settings (outputFormat, upsamplingScale, animated, facePresent, userID) VALUES (%s, %s, %s, %s, %s)"
        args = ("Auto", float(2), 0, 0, userID)
        cursor.execute(stmt, args)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Checks if a user given by the variable 'userID' already exists in the 'pixscale_user_settings' table (Returns False if the user does not exist)
    def check_user_settings_exists_db(self, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "SELECT userID FROM pixscale_user_settings WHERE userID = (%s)"
        args = (userID,)
        cursor.execute(stmt, args)
        user = cursor.fetchone()
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()
        if user == None:
            return False
        else:
            return True

    # Modifies the 'pixscale_user_settings' table with newly specified value, unless value "None" is given in which case the
    def modify_user_settings(self, outputFormat, upsamplingScale, animated, facePresent, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the querys
        if outputFormat != None:
            updt = "UPDATE pixscale_user_settings SET outputFormat = (%s) WHERE userID = (%s)"
            args = (outputFormat, userID)
            cursor.execute(updt, args)
        if upsamplingScale != None:
            updt1 = "UPDATE pixscale_user_settings SET upsamplingScale = (%s) WHERE userID = (%s)"
            args1 = (upsamplingScale, userID)
            cursor.execute(updt1, args1)
        if animated != None:
            updt2 = "UPDATE pixscale_user_settings SET animated = (%s) WHERE userID = (%s)"
            args2 = (animated, userID)
            cursor.execute(updt2, args2)
        if facePresent != None:
            updt3 = "UPDATE pixscale_user_settings SET facePresent = (%s) WHERE userID = (%s)"
            args3 = (facePresent, userID)
            cursor.execute(updt3, args3)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()

    # Retrieves a users application settings as an array from the 'pixscale_user_settings' table given their "userID"
    def retrieve_user_settings(self, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "SELECT * FROM pixscale_user_settings WHERE userID = (%s)"
        args = (userID,)
        cursor.execute(stmt, args)
        settings = cursor.fetchone()
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()
        return settings
    
    # Adds a users feedback to the pixscale_feedback table
    def add_user_feedback(self, now, feedback, userID):
        # Get a connection from the pool
        cnx = self.cnxpool.get_connection()
        # Get the cursor for the connection
        cursor = cnx.cursor(buffered=True)
        # Execute the query
        stmt = "INSERT INTO pixscale_feedback (dateTime, feedback, userID) VALUES (%s, %s, %s)"
        args = (now, feedback, userID)
        cursor.execute(stmt, args)
        # Close the cursor
        cursor.close()
        # Close the connection (return it back to the pool)
        cnx.close()


    # def get_items(self, user
    # def get_items(self, userID, \sd.as,dnasdasdna,dn,as,dbn
    # shbdkjasjkdhajksdjkasdhasjk
        # def get_items(self, user
    # def get_items(self, userID, \sd.as,dnasdasdna,dn,as,dbn
    # shbdkjasjkdhajksdjkasdhasjk
        # def get_items(self, user
    # def get_items(self, userID, \sd.as,dnasdasdna,dn,as,dbn
    # shbdkjasjkdhajksdj