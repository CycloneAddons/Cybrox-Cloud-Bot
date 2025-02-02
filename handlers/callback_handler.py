def handle_callback(bot, call):
    callback_prefix = call.data.split('_')[0]


    if callback_prefix == "page":
        cmd = bot.commands.get('/search')
        cmd.handle_pagination(bot, call)
    elif callback_prefix == "mpage":
        page = int(call.data.split('_')[1])
        ccmd = bot.commands.get('/myfiles')
        ccmd.execute(bot, call.message, call.message.chat.id, call.message.message_id, page)

    elif callback_prefix == "lpage":
            page, user_id = call.data.split('_')[1], call.data.split('_')[2]
            page = int(page)
            ccmds = bot.commands.get('/logfiles')
            ccmds.handleLfile(bot, page, user_id, call, call.message.chat.id,  call.message.message_id)
    elif callback_prefix == "summary":
            pagee = int(call.data.split("_")[-1])
            ccmsds = bot.commands.get('/notify')
            ccmsds.display_summary(bot, call.message.chat.id, pagee, call.message.message_id)
    else:
        callback = bot.callbacks.get(callback_prefix)
        if callback:
            callback.handle_callback(bot, call)
        else:
            print(f"No handler for callback prefix: {callback_prefix}")
