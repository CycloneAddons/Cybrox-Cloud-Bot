name = "help"

def execute(bot, message, chat_id):
 public_files = bot.dbuser.aggregate([
    {"$unwind": "$files"},  # Flatten the 'files' array
    {"$match": {"files.isPublic": True}},  # Filter files where isPublic is True
    {"$addFields": {"files.uploader_id": "$_id"}},  # Add uploader_id to the files
    {"$replaceRoot": {"newRoot": "$files"}}  # Replace root to return the entire file object
])

# Convert results to a list
 result = list(public_files)

# Print or return the result
 for file in result:
    print(file)
 bot.send_message(message.chat.id, '''Welcome to Cybrox Cloud Bot Help.

How to Use:
1. /upload : Upload files to Cybrox Cloud.
2. /search : Search for files by name or code.
3. /myfiles : View and manage your uploaded files.
4. /get : Retrieve public files using their unique code.

---

Need Help?
For assistance, contact:
- @aionix for general support
- @CycloneFrenzy for technical issues

Thank you for using Cybrox Cloud
 ''' )