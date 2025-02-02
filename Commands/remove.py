name = "remove"

def execute(bot, message, chat_id):
    result = bot.dbuser.delete_one({"_id": message.from_user.id})
    
    if result.deleted_count > 0:
        print(f"User with chat_id {chat_id} has been removed.")
    else:
        print(f"No user found with chat_id {chat_id}.")
