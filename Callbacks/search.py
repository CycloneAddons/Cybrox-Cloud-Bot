
callback_data = "search"

def handle_callback(bot, call):
    cmd = bot.commands.get('/search')
    cmd.execute(bot, call.message, call.message.chat.id)