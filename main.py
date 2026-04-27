import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ။ Calculator Bot ပါ။\nဥပမာ - 10+5 ဒါမှမဟုတ် 20*2 လို့ ပို့ပါ။")

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    allowed_chars = "0123456789+-*/.() "
    if all(char in allowed_chars for char in user_input):
        try:
            result = eval(user_input)
            await update.message.reply_text(f"အဖြေမှာ: {result}")
        except:
            await update.message.reply_text("တွက်ချက်မှု မှားယွင်းနေပါတယ်။")
    else:
        await update.message.reply_text("ဂဏန်းနဲ့ သင်္ကေတ (+, -, *, /) သာ ရိုက်ပါ။")

if __name__ == '__main__':
    TOKEN = "ဒီနေရာမှာ_သင့်_TOKEN_ထည့်ပါ"
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), calculate))
    application.run_polling()

