import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Render အတွက် Dummy Web Server ဆောက်ခြင်း
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Running')

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), handler)
    server.serve_forever()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ။ Calculator Bot ပါ။\nဥပမာ - 10+5 လို့ ပို့ပါ။")

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    allowed_chars = "0123456789+-*/.() "
    if all(char in allowed_chars for char in user_input):
        try:
            result = eval(user_input)
            await update.message.reply_text(f"အဖြေမှာ: {result}")
        except:
            await update.message.reply_text("တွက်ချက်မှု မှားယွင်းနေပါတယ်။")

if name == 'main':
    # Web Server ကို Thread နဲ့ Run ရန်
    threading.Thread(target=run_web_server, daemon=True).start()
    
    TOKEN = "8478248117:AAGFO8JK1AnUvtw5k8cQXzWHxUgqU8jCaMw"
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), calculate))
    application.run_polling()
