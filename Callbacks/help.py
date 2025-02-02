
callback_data = "help"

def handle_callback(bot, call):
    cmd = bot.commands.get('/help')
    cmd.execute(bot, call.message, call.message.chat.id)