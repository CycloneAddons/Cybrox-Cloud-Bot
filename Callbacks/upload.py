
callback_data = "upload"

def handle_callback(bot, call):
    cmd = bot.commands.get('/upload')
    cmd.execute(bot, call.message, call.message.chat.id)