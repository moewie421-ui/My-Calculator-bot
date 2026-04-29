import google.generativeai as genai
import logging
import os
import random
import threading
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from datetime import timedelta, datetime

# --- CONFIGURATION ---
BOT_TOKEN = "8478248117:AAGFO8JK1AnUvtw5k8cQXzWHxUgqU8jCaMw"
GEMINI_API_KEY = "AIzaSyCqhrPEFerqKf-0_UL4x1lD9CNkVScBaEk"
ADMIN_ID = 5508936383
GROUP_ID = -1002592040832

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# Web Server for Rendering/Koyeb
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Online with Sticker & Emoji Anti-Spam!')

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), handler)
    server.serve_forever()

# ၁။ AI Auto Message (၁ နာရီတစ်ခါ)
async def send_ai_message(context: ContextTypes.DEFAULT_TYPE):
    try:
        prompt = "Write a short Myanmar gaming message for an MLBB group. Cool and friendly."
        response = ai_model.generate_content(prompt)
        await context.bot.send_message(chat_id="-1002592040832", text=response.text)
    except: pass

# ၂။ Advanced Calculator
async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text
    operators = ['+', '-', '*', '/', '÷', '×']
    if any(op in text for op in operators) and all(c in "0123456789+-*/.() " for c in text.replace('÷', '/').replace('×', '*')):
        try:
            res = eval(text.replace('÷', '/').replace('×', '*'))
            await update.message.reply_text(f"🔢 အဖြေ: {round(res, 2) if isinstance(res, float) else res}")
        except: pass

# ၃။ Anti-Spam (စာ၊ Sticker၊ Emoji အကုန်မိစေရန်)
user_data = {}

async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Chat type စစ်ဆေးခြင်း
    if not update.message or update.message.chat.type == 'private': return
    
    user = update.message.from_user
    if not user or user.id == ADMIN_ID: return
    
    user_id = user.id
    now = datetime.now()

    if user_id not in user_data:
        user_data[user_id] = {"count": 1, "last_time": now}
    else:
        # စာပို့တဲ့ အချိန်ခြားနားချက်ကို တွက်ခြင်း
        elapsed = (now - user_data[user_id]["last_time"]).total_seconds()
        
        if elapsed < 3.0: # ၃ စက္ကန့်အတွင်း ပို့ရင် Count တိုးမယ်
            user_data[user_id]["count"] += 1
        else:
            user_data[user_id]["count"] = 1
        
        user_data[user_id]["last_time"] = now

    count = user_data[user_id]["count"]

    if count == 5:
        await update.message.reply_text(f"⚠️ @{user.username or user.first_name} ရေ စာတွေ/Stickers တွေ အရမ်းမြန်နေပြီ။ လျှော့ပါဦး။")
    
    elif count >= 8:
        user_data[user_id]["count"] = 0
        try:
            # ၁၀ မိနစ် Mute ခြင်း
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user.id,
                permissions={"can_send_messages": False},
                until_date=datetime.now() + timedelta(minutes=10)
            )
            await update.message.reply_text(f"🚫 @{user.username or user.first_name} ကို Spam (Text/Sticker/Emoji) လုပ်လွန်းလို့ ၁၀ မိနစ် Mute လိုက်ပါပြီ။")
        except: pass

# ၄။ Admin Broadcast
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID and update.message.chat.type == 'private':
        await context.bot.send_message(chat_id=GROUP_ID, text=f"📢 **ADMIN MESSAGE**\n\n{update.message.text}", parse_mode='Markdown')
        await update.message.reply_text("✅ ပို့ပြီးပါပြီ။")

HEROES = ["Miya", "Balmond", "Saber", "Alice", "Nana", "Tigreal", "Alucard", "Karina", "Akai", "Franco", "Bane", "Bruno", "Clint", "Rafaela", "Eudora", "Zilong", "Fanny", "Layla", "Minotaur", "Lolita", "Hayabusa", "Freya", "Gord", "Natalia", "Kagura", "Chou", "Sun", "Alpha", "Ruby", "Yi Sun-shin", "Moskov", "Johnson", "Cyclops", "Estes", "Hilda", "Aurora", "Lapu-Lapu", "Vexana", "Roger", "Karrie", "Gatotkaca", "Harley", "Irithel", "Grook", "Argus", "Odette", "Lancelot", "Diggie", "Hylos", "Zhask", "Helcurt", "Pharsa", "Lesley", "Jawhead", "Angela", "Gusion", "Valir", "Martis", "Uranus", "Hanabi", "Chang'e", "Selina", "Aldous", "Claude", "Vale", "Leomord", "Lunox", "Hanzo", "Belerick", "Minsitthar", "Kadita", "Badang", "Guinevere", "Esmeralda", "Khufra", "Granger", "Faramis", "Terizla", "X.Borg", "Lylia", "Baxia", "Masha", "Wanwan", "Silvanna", "Cecilion", "Carmilla", "Atlas", "Popol and Kupa", "Yu Zhong", "Khaleed", "Barats", "Brody", "Benedetta", "Mathilda", "Paquito", "Yve", "Beatrix", "Phoveus", "Natan", "Aulus", "Floryn", "Valentina", "Edith", "Yin", "Melissa", "Xavier", "Julian", "Fredrinn", "Joy", "Arlott", "Novaria", "Ixia", "Nolan", "Cici", "Chip", "Zhu Xin", "Suyou", "Lukas", "Aamon", "Gloo"]

# --- MAIN ---
if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.job_queue.run_repeating(send_ai_message, interval=60, first=10)

    # Command Handlers
    app.add_handler(CommandHandler('random', lambda u, c: u.message.reply_text(f"🎁 Hero: {random.choice(HEROES)}")))
    app.add_handler(CommandHandler('side', lambda u, c: u.message.reply_text(f"ဘက်ရွေး: {random.choice(['🟦 Blue', '🟥 Red'])}")))
    app.add_handler(CommandHandler('flip', lambda u, c: u.message.reply_text(f"ရလဒ်: {random.choice(['🪙 ခေါင်း', '🪙 ပန်း'])}")))
    app.add_handler(CommandHandler('dice', lambda u, c: u.message.reply_dice()))
    
    # Message Handlers
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & (~filters.COMMAND), admin_broadcast))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & (~filters.COMMAND), calculate))
    
    # Anti-Spam ကို filters.ALL သုံးထားလို့ Sticker ရော၊ Emoji ရော၊ စာရော အကုန်မိမှာပါ
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, anti_spam), group=1)
    
    print("Bot is starting...")
    app.run_polling()
