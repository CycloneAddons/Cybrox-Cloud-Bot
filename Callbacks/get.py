
callback_data = "get"

def handle_callback(bot, call):
    cmd = bot.commands.get('/get')
    cmd.execute(bot, call.message, call.message.chat.id)