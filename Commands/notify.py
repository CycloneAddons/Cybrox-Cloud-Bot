from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

name = "notify"
# Array to store all user results with statuses
user_results = []

def execute(bot, message, chat_id):
    bot.send_message(chat_id, "Fetching users and preparing to broadcast the message...")

    # Fetch all users from the database
    users = list(bot.dbuser.find())

    
    def handler(msg):
        for user in users:
            target_chat_id = user.get('_id')  # Get the chat ID
            first_name = user.get('first_name', 'Unknown')  # Get the first name or 'Unknown' if not available

            if target_chat_id:
                try:
                    # Forward the user's message to the chat ID
                    bot.copy_message(target_chat_id, msg.chat.id, msg.message_id)
                    # Add to user results with success status
                    user_results.append({'firstname': first_name, 'id': target_chat_id, 'status': "Success"})
                except Exception as e:
                    # Log failure and add to user results with failed status
                    print(f"Failed to send message to chat ID {target_chat_id}: {e}")
                    user_results.append({'firstname': first_name, 'id': target_chat_id, 'status': "Failed"})

        # Start displaying results with pagination
        display_summary(bot, chat_id, 1, message_id=None)



    # Register the handler for the next user input
    bot.register_next_step_handler_by_chat_id(chat_id, handler)



def display_summary(bot, chat_id, page, message_id=None):
        per_page = 10
        total_pages = (len(user_results) // per_page) + (1 if len(user_results) % per_page > 0 else 0)

        # Paginate user results for the current page
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_results = user_results[start_index:end_index]

        # Calculate total success and failure counts
        total_success = sum(1 for user in user_results if user['status'] == "Success")
        total_failed = sum(1 for user in user_results if user['status'] == "Failed")

        # Generate the summary message for the current page
        response_message = f"Broadcast Summary (Page {page}/{total_pages}):\n\n"
        response_message += f"✅ Total Success: {total_success}\n❌ Total Failed: {total_failed}\n\n"

        for idx, user in enumerate(paginated_results, start=start_index + 1):
            response_message += f"{idx}. {user['firstname']} (ID: {user['id']}) - {user['status']}\n"

        # Generate pagination buttons
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("⏮️ First", callback_data="summary_page_1"),
            InlineKeyboardButton("⬅️ Previous", callback_data=f"summary_page_{max(page - 1, 1)}"),
            InlineKeyboardButton("➡️ Next", callback_data=f"summary_page_{min(page + 1, total_pages)}"),
            InlineKeyboardButton("⏭️ Last", callback_data=f"summary_page_{total_pages}")
        )

        if message_id:
            # Edit the existing message
            bot.edit_message_text(response_message, chat_id, message_id, reply_markup=markup)
        else:
            # Send a new message
            sent_message = bot.send_message(chat_id, response_message, reply_markup=markup)
            return sent_message.message_id