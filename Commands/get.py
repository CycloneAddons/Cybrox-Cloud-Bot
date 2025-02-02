name = "get"
in_msg = {}  # This will hold the state for each user's message collection

def execute(bot, message, chat_id):
    # Send a message asking for the unique code
    bot.send_message(chat_id, "Please enter the unique code to get the file.")

    def handler(msg):
         files = bot.dbfiles.find_one({"uniqueCode": msg.text})  
         if files:
              bot.send_document(chat_id, files['_id'])
         else:
              bot.send_message(chat_id, "Wrong Code Provided...")

    bot.register_next_step_handler_by_chat_id(chat_id, handler)

