import threading
from rapidfuzz import fuzz, process
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException

pagination_state = {}
name = "search"


def execute(bot, message, chat_id):
  a = bot.send_message(chat_id, "Please enter what you want to search ??")

  def handler(msg):  
    bot.delete_message(chat_id, msg.message_id)

    search_results = ai_based_search(bot.dbuser, msg.text, field="fileName", limit=5000)
    pagination_state[f"{chat_id}_{a.message_id}"] = {'search_results': search_results, 'current_page': 1, 'query': msg.text}
    total_files = len(search_results)
    total_pages = (total_files // 10) + (1 if total_files % 10 > 0 else 0)

    results_page = paginate_search_results(search_results, page=1)
    total_files_text = f"Query: {msg.text} - {total_files} Files Found\n"
    results_text = "\n".join(
        [
            f"{idx + 1}. [{result['fileName']} ](https://t.me/cybroxcloudbot?start=get_{result['uniqueCode']}) \n                                              - {result['codeUsage']} Views\n"
            for idx, result in enumerate(results_page)
        ]
    )
    current_page_text = f"\nPage: 1/{total_pages}"

    page_text = f"{total_files_text}\n{results_text}{current_page_text}"
    keyboard = generate_pagination_buttons(1, total_pages)
    bot.edit_message_text(chat_id=chat_id, message_id=a.message_id, text=page_text, reply_markup=keyboard, parse_mode="Markdown")

    reset_timer(bot, chat_id, a.message_id, page_text)

  bot.register_next_step_handler_by_chat_id(chat_id, handler)  




# Handle pagination button presses
def handle_pagination(bot, update):
    chat_id = update.message.chat.id
    page_number = int(update.data.split("_")[1])
    
    search_results = pagination_state.get(f"{chat_id}_{update.message.message_id}", {}).get("search_results", [])
    if not search_results:
        bot.send_message(chat_id, "No results found.")
        return

    total_files = len(search_results)
    total_pages = (total_files // 10) + (1 if total_files % 10 > 0 else 0)

    results_page = paginate_search_results(search_results, page=page_number)
    pagination_state[f"{chat_id}_{update.message.message_id}"]['current_page'] = page_number

    total_files_text = f"Query: {pagination_state[f'{chat_id}_{update.message.message_id}']['query']} - {total_files} Files Found\n"
    global_index_start = (page_number - 1) * 10 + 1
    results_text = "\n".join(
        [
            f"{global_index_start + idx}. [{result['fileName']}](https://t.me/cybroxcloudbot?start=get_{result['uniqueCode']}) \n                                             - {result['codeUsage']} Views\n"
            for idx, result in enumerate(results_page)
        ]
    )
    current_page_text = f"\nPage: {page_number}/{total_pages}"

    page_text = f"{total_files_text}\n{results_text}{current_page_text}"
    keyboard = generate_pagination_buttons(page_number, total_pages)

    try:
        sent_message = bot.edit_message_text(
            chat_id=chat_id,
            message_id=update.message.message_id,
            text=page_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

        # Reset and schedule a new expiration timer after successful page update
        reset_timer(bot, chat_id, update.message.message_id, page_text)

    except ApiTelegramException as e:
        if "message is not modified" in str(e):
            pass  # Ignore the exception


def ai_based_search(collection, query, field="fileName", limit=10, threshold=70):
    
    

    exact_match = list(collection.aggregate([
    {"$unwind": "$files"},  # Flatten the 'files' array
    {"$match": {"files.uniqueCode": query, "files.isPublic": True}},  # Filter files where isPublic is True
    {"$addFields": {"files.uploader_id": "$_id"}},  # Add uploader_id to the files
    {"$replaceRoot": {"newRoot": "$files"}}  # Replace root to return the entire file object
]))
    
    if exact_match:
        return [{ **exact_match[0], "score": 100 }]
    
    query = query.lower()
    documents = list(collection.aggregate([
    {"$unwind": "$files"},  # Flatten the 'files' array
    {"$match": {"files.isPublic": True}},  # Filter files where isPublic is True
    {"$addFields": {"files.uploader_id": "$_id"}},  # Add uploader_id to the files
    {"$replaceRoot": {"newRoot": "$files"}}  # Replace root to return the entire file object
]))
    
    choices = [(doc.get(field, "").lower(), i) for i, doc in enumerate(documents)]  

    results = process.extract(
        query,
        [choice[0] for choice in choices],
        scorer=fuzz.partial_ratio,
        limit=limit,
    )

    filtered_results = [
        {**documents[idx], "score": score} 
        for _, score, idx in results
        if score >= threshold
    ]

    return filtered_results

def paginate_search_results(results, page=1, per_page=10):
    start_idx = (page - 1) * per_page
    return results[start_idx:start_idx + per_page]

def generate_pagination_buttons(current_page, total_pages):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("First", callback_data="page_1"),
            InlineKeyboardButton("Back", callback_data=f"page_{max(1, current_page - 1)}"),
            InlineKeyboardButton("Next", callback_data=f"page_{min(total_pages, current_page + 1)}"),
            InlineKeyboardButton("Last", callback_data=f"page_{total_pages}")
        ]
    ])

def expire_buttons(bot, chat_id, message_id, page_text):
    expired_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Expired", callback_data="expired"),
        ]
    ])
    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=page_text,
            reply_markup=expired_keyboard,
            parse_mode="Markdown"
        )
    except ApiTelegramException:
        pass  # Ignore any errors like "message is not modified"

# Reset and create a new timer
def reset_timer(bot, chat_id, message_id, page_text):
    # Cancel the previous timer if it exists
    if 'timer' in pagination_state.get(f"{chat_id}_{message_id}", {}):
        pagination_state[f"{chat_id}_{message_id}"]['timer'].cancel()

    # Create and set the new timer
    timer = threading.Timer(30, expire_buttons, args=(bot, chat_id, message_id, page_text))
    pagination_state[f"{chat_id}_{message_id}"]['timer'] = timer
    timer.start()

# Execute search command