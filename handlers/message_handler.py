def handle_message(bot, message):
    chat_id = message.chat.id
    user = bot.dbuser.find_one({"_id": message.from_user.id})

    if user is None or not user.get("password"): 
        try:
            bot.delete_message(chat_id, message.message_id)
        except Exception:
            pass
        start = bot.commands.get('/start')
        start.execute(bot, message, chat_id)
    else:
        if message.content_type == 'document':
            cmd = bot.commands.get('/upload')
            if cmd:
                cmd.upload(bot, message, chat_id)
        else:
            command_name = message.text.split(' ')[0]
            command = bot.commands.get(command_name)
            if command:
                args = message.text.split(' ')[1:]
                command.execute(bot, message, chat_id)
