import os
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# Render Environment Variables ထဲမှာ BOT_TOKEN ကို သေချာထည့်ထားပေးပါ
BOT_TOKEN ="7921219930:AAHT2t0RY55MVVYc7nbZqYa-BExCfvFOEB8"
ADMIN_ID = 5508936383
GROUP_ID = "-1002592040832"

# MLBB Hero Full List
MLBB_HEROES = [
    "Miya", "Balmond", "Saber", "Alice", "Nana", "Tigreal", "Alucard", "Karina", "Akai", "Franco", 
    "Bruno", "Clint", "Rafaela", "Eudora", "Zilong", "Fanny", "Layla", "Minotaur", "Lolita", "Hayabusa", 
    "Freya", "Gord", "Natalia", "Kagura", "Chou", "Sun", "Alpha", "Ruby", "Yi Sun-shin", "Moskov", 
    "Johnson", "Cyclops", "Estes", "Hilda", "Aurora", "Lapu-Lapu", "Vexana", "Roger", "Karrie", "Grock", 
    "Irithel", "Harley", "Odette", "Lancelot", "Diggie", "Hylos", "Zhask", "Helcurt", "Pharsa", "Lesley", 
    "Jawhead", "Angela", "Gusion", "Valir", "Martis", "Uranus", "Hanabi", "Chang'e", "Selena", "Aldous", 
    "Claude", "Vale", "Leomord", "Lunox", "Hanzo", "Belerick", "Minsitthar", "Kadita", "Badang", "Guinevere", 
    "Khufra", "Esmeralda", "Granger", "Terizla", "X.Borg", "Lylia", "Baxia", "Masha", "Wanwan", "Silvanna", 
    "Cecilion", "Carmilla", "Atlas", "Popol and Kupa", "Yu Zhong", "Khaleed", "Barats", "Brody", "Benedetta", 
    "Mathilda", "Paquito", "Beatrix", "Gloo", "Phoveus", "Natan", "Aulus", "Aamon", "Valentina", "Edith", 
    "Yin", "Melissa", "Xavier", "Julian", "Fredrinn", "Joy", "Arlott", "Novaria", "Ixia", "Nolan", "Cici"
]

# Web Server for Render
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Online!')

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), handler)
    server.serve_forever()

# 1. Anti-Spam (4s 5 warnings, 5s 7 mutes)
user_messages = {}
async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.chat.type == 'private': return
    user_id = update.effective_user.id
    if user_id == ADMIN_ID: return
    
    now = datetime.now()
    if user_id not in user_messages: user_messages[user_id] = []
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < timedelta(seconds=5)]
    user_messages[user_id].append(now)
    count = len(user_messages[user_id])

    if count == 5:
        await update.message.reply_text(f"⚠️ @{update.effective_user.username or update.effective_user.first_name} ရေ မ spam ပါနဲ့ဗျ။")
    elif count >= 7:
        until = datetime.now() + timedelta(minutes=10)
        try:
            await context.bot.restrict_chat_member(update.effective_chat.id, user_id, 
                  permissions={"can_send_messages": False}, until_date=until)
            await update.message.reply_text(f"🚫 @{update.effective_user.username or update.effective_user.first_name} ကို ၁၀ မိနစ် Mute လိုက်ပါပြီ။")
        except: pass

# 2. Calculator
async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text
    if any(op in text for op in ['+', '-', '*', '/', '÷', '×']):
        try:
            expr = text.replace('÷', '/').replace('×', '*').replace('x', '*')
            if all(c in "0123456789+-*/(). " for c in expr):
                res = eval(expr)
                await update.message.reply_text(f"🔢 အဖြေ: {res}")
        except: pass

# 3. Admin Broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    msg = " ".join(context.args)
    await context.bot.send_message(chat_id=GROUP_ID, text=f"📢 **ADMIN MESSAGE:**\n\n{msg}")

# --- MAIN ---
if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables!")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        # Handlers
        app.add_handler(CommandHandler('random', lambda u, c: u.message.reply_text(f"🎁 Random Hero: {random.choice(MLBB_HEROES)}")))
        app.add_handler(CommandHandler('split', lambda u, c: u.message.reply_text(f"⚔️ Team ခွဲလိုက်ပါပြီ -\n\n🟦 Blue: {random.randint(1,5)}\n🟥 Red: {random.randint(1,5)}")))
        app.add_handler(CommandHandler('broadcast', broadcast))
        app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & (~filters.COMMAND), calculate))
        app.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, anti_spam))
        
        print("Bot is starting correctly without AI module...")
        app.run_polling()
