import google.generativeai as genai
import os
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from datetime import datetime, timedelta

# --- CONFIGURATION ---
BOT_TOKEN = "7921219930:AAHT2t0RY55MVVYc7nbZqYa-BExCfvFOEB8"
GEMINI_API_KEY = "AIzaSyCqhrPEFerqKf-0_UL4x1lD9CNkVScBaEk"
ADMIN_ID = "5508936383"  # Admin User ID)
GROUP_ID = "-1002592040832" # Telegram Group ID

# Gemini AI Setup
genai.configure(api_key=AIzaSyCqhrPEFerqKf-0_UL4x1lD9CNkVScBaEk)
ai_model = genai.GenerativeModel('gemini-pro')

# 1. Web Server for Render
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Online!')

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), handler)
    server.serve_forever()

# 2. MLBB Hero Randomizer (Full List)
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

async def random_hero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hero = random.choice(MLBB_HEROES)
    await update.message.reply_text(f"🎁 Random MLBB Hero: {hero}")

# 3. Calculator Function
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

# 4. Admin Broadcast
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    msg = " ".join(context.args)
    await context.bot.send_message(chat_id=GROUP_ID, text=f"📢 **ADMIN BROADCAST**\n\n{msg}", parse_mode='Markdown')

# 5. Anti-Spam
async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.chat.type == 'private': return
    user_id = update.effective_user.id
    if user_id == 5508936383: return # Admin ကို ချန်ထားတာပါ
    
    now = datetime.now()
    if user_id not in user_messages: user_messages[user_id] = []
    
    # ၅ စက္ကန့်အတွင်းက စာရင်းကိုပဲ ယူမယ်
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < timedelta(seconds=5)]
    user_messages[user_id].append(now)
    count = len(user_messages[user_id])

    # ၄ စက္ကန့်အတွင်း ၅ ခုဆိုရင် Warning
    if count == 5:
        await update.message.reply_text(f"⚠️ @{update.effective_user.username} ရေ မ spam ပါနဲ့ဗျ။")

    # ၅ စက္ကန့်အတွင်း ၇ ခုဆိုရင် 10 မိနစ် Mute
    elif count >= 7:
        until = datetime.now() + timedelta(minutes=10)
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, 
              permissions={"can_send_messages": False}, until_date=until)
        await update.message.reply_text(f"🚫 @{update.effective_user.username} ကို ၁၀ မိနစ် Mute လိုက်ပါပြီ။")


# 6. Team Splitter (Red/Blue)
async def split_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"⚔️ Team ခွဲလိုက်ပါပြီ -\n\n🟦 Blue Team: {random.randint(1,5)} ယောက်\n🟥 Red Team: {random.randint(1,5)} ယောက်")

# 7. AI Auto Message (Love & Friendship)
async def send_auto_ai_message(context: ContextTypes.DEFAULT_TYPE):
    try:
        prompt = "Write a short, heart-touching love or relationship quote or a sweet message for friends in Myanmar language. Use emojis."
        response = ai_model.generate_content(prompt)
        await context.bot.send_message(chat_id=GROUP_ID, text=response.text)
    except Exception as e:
        print(f"AI Error: {e}")

# --- MAIN ---
if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 1 Hour Timer
    if app.job_queue:
        app.job_queue.run_repeating(send_auto_ai_message, interval=3600, first=10)

    # Handlers
    app.add_handler(CommandHandler('random', random_hero))
    app.add_handler(CommandHandler('broadcast', admin_broadcast))
    app.add_handler(CommandHandler('split', split_teams))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & (~filters.COMMAND), calculate))
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, anti_spam))
    
    print("Bot is starting...")
    app.run_polling()
