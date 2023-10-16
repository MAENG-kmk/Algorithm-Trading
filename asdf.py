import telegram
from telegram.ext import CommandHandler, Updater

tele_token = "5210226721:AAG95BNFRPXRME5MU_ytI_JIx7wgiW1XASU"
chat_id = 5135122806

updater = Updater(token=tele_token, use_context=True)
dispatcher = updater.dispatcher

def check(update, context):
  context.bot.send_message(chat_id=update.effective_chat.id, text="뭐요")
    

check_handler = CommandHandler('check', check)
dispatcher.add_handler(check_handler)

updater.start_polling()