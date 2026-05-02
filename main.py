import telebot
import random
import time
from flask import Flask
from threading import Thread
import google.generativeai as genai

# --- CONFIGURATION ---
BOT_TOKEN = "8617312989:AAGP5eW_7AY7VsThFzhRFaX8QVSgGhHR-Aw"
GEMINI_API_KEY = "AIzaSyDnpzNG40_OuLTdyWqmyn1HK7lKXbz5MCY"
ADMIN_ID = "5508936383"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# MLBB Hero List
HEROES = HEROES = [
    "Miya", "Balmond", "Saber", "Alice", "Nana", "Tigreal", "Alucard", "Karina", "Akai", "Franco", 
    "Bane", "Bruno", "Clint", "Rafaela", "Eudora", "Zilong", "Fanny", "Layla", "Minotaur", "Lolita", 
    "Hayabusa", "Freya", "Gord", "Natalia", "Kagura", "Chou", "Sun", "Alpha", "Ruby", "Yi Sun-shin", 
    "Moskov", "Johnson", "Cyclops", "Estes", "Hilda", "Aurora", "Lapu-Lapu", "Vexana", "Roger", "Karrie", 
    "Gatotkaca", "Harley", "Irithel", "Grock", "Argus", "Odette", "Lancelot", "Diggie", "Hylos", "Lesley", 
    "Pharsa", "Jawhead", "Angela", "Gusion", "Valir", "Martis", "Uranus", "Hanabi", "Chang'e", "Selena", 
    "Kaja", "Aldous", "Claude", "Vale", "Leomord", "Lunox", "Hanzo", "Belerick", "Kimmy", "Thamuz", 
    "Harith", "Kadita", "Faramis", "Badang", "Guinevere", "Khufra", "Granger", "Esmeralda", "Terizla", "X.Borg", 
    "Lylia", "Dyrroth", "Baxia", "Masha", "Wanwan", "Silvanna", "Cecilion", "Carmilla", "Atlas", "Popol and Kupa", 
    "Yu Zhong", "Khaleed", "Barats", "Brody", "Benedetta", "Mathilda", "Paquito", "Beatrix", "Phoveus", "Glo", 
    "Natan", "Aulus", "Floryn", "Valentina", "Edith", "Yin", "Melissa", "Xavier", "Julian", "Terizla", 
    "Fredrinn", "Joy", "Arlott", "Novaria", "Ixia", "Nolan", "Cici", "Chip"
]


# Spam control data
user_spam_data = {}

# --- FLASK SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=10000)

# --- BOT COMMANDS ---

# 1. Random Hero Command
@bot.message_handler(commands=['random'])
def random_hero(message):
    hero = random.choice(HEROES)
    bot.reply_to(message, f"🎮 သင့်အတွက် Random Hero ကတော့: **{hero}** ဖြစ်ပါတယ်ဗျ။")

# 2. Team Splitter (Blue/Red)
@bot.message_handler(commands=['split'])
def split_teams(message):
    text = message.text.replace('/split', '').strip()
    if not text:
        bot.reply_to(message, "အသုံးပြုပုံ: `/split နာမည်၁ နာမည်၂ နာမည်၃ ...` (နာမည်များကို ခြားပြီးရိုက်ပါ)")
        return
    
    players = text.split()
    if len(players) < 2:
        bot.reply_to(message, "အနည်းဆုံး လူ ၂ ယောက် အမည်ထည့်ပေးပါဗျ။")
        return
    
    random.shuffle(players)
    mid = len(players) // 2
    blue_team = players[:mid]
    red_team = players[mid:]
    
    res = f"🔵 **Blue Team:** {', '.join(blue_team)}\n"
    res += f"🔴 **Red Team:** {', '.join(red_team)}"
    bot.reply_to(message, res)

# 3. Admin Broadcast
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        msg_to_send = message.text.replace('/broadcast', '').strip()
        if msg_to_send:
            # ဤနေရာတွင် Chat ID ကို သင့် Group ID ဖြင့် အစားထိုးနိုင်သည်
            # လောလောဆယ် Admin ဆီပဲ ပြန်ပို့ပြထားသည်
            bot.send_message(message.chat.id, f"📣 **Admin Message:**\n\n{msg_to_send}")
    else:
        bot.reply_to(message, "ဒီ Command ကို Admin သာ သုံးခွင့်ရှိပါတယ်။")

# 4. Anti-Spam (Warning & Mute) & Gemini Chat
@bot.message_handler(content_types=['text', 'sticker', 'photo'])
def monitor_messages(message):
    if message.chat.type != 'private':
        uid = message.from_user.id
        now = time.time()
        
        if uid not in user_spam_data:
            user_spam_data[uid] = {"count": 0, "start_time": now}
            
        u_data = user_spam_data[uid]
        
        # Reset counter after 6 seconds
        if now - u_data["start_time"] > 6:
            u_data["count"] = 1
            u_data["start_time"] = now
        else:
            u_data["count"] += 1
            
        # Warning at 5 messages
        if u_data["count"] == 5:
            bot.reply_to(message, "⚠️ Spam မလုပ်ပါနဲ့ဦး။ နောက်ထပ်စာပို့ရင် ၁၀ မိနစ် Mute ခံရပါမယ်။")
            
        # Mute at 8 messages
        if u_data["count"] >= 8:
            try:
                until = int(time.time() + 600) # 10 mins
                bot.restrict_chat_member(message.chat.id, uid, until_date=until)
                bot.send_message(message.chat.id, f"🚫 @{message.from_user.username} ကို Spamming ကြောင့် ၁၀ မိနစ် Mute လိုက်ပါပြီ။")
            except:
                pass
            return

        # 5. Gemini AI Reply (Bot စာကို Reply ပြန်မှ အလုပ်လုပ်မည်)
        if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
            try:
                response = model.generate_content(message.text)
                bot.reply_to(message, response.text)
            except Exception as e:
                print(f"AI Error: {e}")

# Start Server & Bot
t = Thread(target=run)
t.start()

print("Bot is starting...")
bot.infinity_polling()
