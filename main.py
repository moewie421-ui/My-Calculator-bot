import os
from flask import Flask
from threading import Thread

# Flask App ဆောက်ပြီး Port တစ်ခု ဖွင့်ပေးထားခြင်း (Render အတွက်)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render က ပေးတဲ့ Port ကို ယူသုံးမယ်၊ မရှိရင် 8080 သုံးမယ်
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Bot ရဲ့ အဓိက Code အပေါ်နားမှာ ဒါကို ခေါ်သုံးပေးပါ ---
keep_alive()

# ဒီအောက်မှာမှ သင့်ရဲ့ Bot code တွေကို ဆက်ရေးပါ (bot.infinity_polling အထိ)

import telebot
import random
import time
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler
from collections import defaultdict
from simpleeval import simple_eval

# --- CONFIGURATION ---
BOT_TOKEN = "8704752796:AAFnZ4mn3CIpnD_0oqGvOkYxtJXeKI6Hwug"
GEMINI_API_KEY = "AIzaSyDnpzNG40_OuLTdyWqmyn1HK7lKXbz5MCY"
GROUP_CHAT_ID = "-1002592040832"
ADMIN_ID = "5508936383"

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(BOT_TOKEN)

# --- ၁၂၆ ကောင်သော MLBB HEROES စာရင်း အပြည့်အစုံ ---
HEROES = [
    "Miya", "Balmond", "Saber", "Alice", "Nana", "Tigreal", "Alucard", "Karina", "Akai", "Franco", "Bruno", "Clint", "Rafaela", "Eudora", "Zilong", "Fanny", "Layla", "Minotaur", "Lolita", "Hayabusa", "Freya", "Gord", "Natalia", "Kagura", "Chou", "Sun", "Alpha", "Ruby", "Yi Sun-shin", "Moskov", "Johnson", "Cyclops", "Estes", "Hilda", "Aurora", "Lapu-Lapu", "Vexana", "Roger", "Karrie", "Grock", "Irithel", "Harley", "Odette", "Lancelot", "Diggie", "Hylos", "Zhask", "Helcurt", "Pharsa", "Lesley", "Jawhead", "Angela", "Gusion", "Valir", "Martis", "Uranus", "Hanabi", "Chang'e", "Selena", "Aldous", "Claude", "Vale", "Leomord", "Lunox", "Hanzo", "Belerick", "Kimmy", "Thamuz", "Harith", "Kadita", "Faramis", "Badang", "Khufra", "Granger", "Guinevere", "Esmeralda", "Terizla", "X.Borg", "Lylia", "Baxia", "Masha", "Wanwan", "Silvanna", "Cecilion", "Carmilla", "Atlas", "Popol and Kupa", "Yu Zhong", "Khaleed", "Barats", "Brody", "Benedetta", "Mathilda", "Paquito", "Beatrix", "Gloo", "Phoveus", "Natan", "Aulus", "Aamon", "Valentina", "Edith", "Yin", "Melissa", "Xavier", "Julian", "Fredrinn", "Joy", "Arlott", "Novaria", "Ixia", "Nolan", "Cici", "Chip", "Zhuxin", "Suyou"
]

# --- MLBB RULES (သင်ပေးထားသော အချက်အားလုံး) ---
RULES_TEXT = """
 **MLBB MID ONLY RULE**

 **Creep သတ်မှတ်ချက်:**
Mid LANE CREEP သာစားရမည်။ အပေါ်အောက် SECOND TOWER ကျိုးလျှင် LANE ရှင်းနိုင်သည်။

 **Lane ရှင်းခြင်း:**
LANE ရှင်းရာတွင် SECOND TOWER အကျော်က ချုံပုတ်ကျော်ပြီး မရှင်းရ။

 **Mega Tower & Ending:**
MID MEGA TOWER ကျိုးပါက LANE သုံး LANE စုရှင်းတာကို ခံရမည်။ MID MEGA ကျိုးပါက ကြိုက်တဲ့ CREEP နဲ့ END လို့ရသည်။

 **အရေးကြီးချက်များ:**
 [REMAP] LINE မကောင်းလျှင် 1MIN အတွင်း SURR ချပါ။
 [UNSEE] ပွဲတွေအတွက်သာ ရရှိနိုင်သည်။
 အပြင်ပွဲများ % ပြန်မအမ်းပါ။
 **RULE COPY မလုပ်ပါနဲ့။**
"""

# Anti-Spam မှတ်တမ်း
user_spam_data = defaultdict(lambda: {"count": 0, "start_time": time.time()})

# --- FUNCTIONS ---
def send_ai_quote():
    try:
        prompt = "မင်းက MLBB Group Admin ပါ။ အဖွဲ့ဝင်တွေအတွက် အချစ်၊ အလွမ်း၊ ဒါမှမဟုတ် ခံစားချက်ရသပါတဲ့ မြန်မာစာသားတိုလေးတစ်ကြောင်း စဉ်းစားပေးပါ။ စာသားသက်သက်ပဲ ပို့ပါ။"
        response = model.generate_content(prompt)
        bot.send_message(GROUP_CHAT_ID, response.text)
    except:
        pass

scheduler = BackgroundScheduler()
scheduler.add_job(send_ai_quote, 'interval', minutes=45)
scheduler.start()

# --- HANDLERS ---
@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.from_user.id == ADMIN_ID)
def handle_broadcast(message):
    bot.send_message(GROUP_CHAT_ID, message.text)
    bot.reply_to(message, " Group ထဲကို စာပို့လိုက်ပါပြီ။")

@bot.message_handler(commands=['cal'])
def do_calc(message):
    try:
        msg_parts = message.text.split(maxsplit=1)
        if len(msg_parts) < 2:
            bot.reply_to(message, " တွက်ချက်လိုသည့် ဂဏန်းများကို ရိုက်ထည့်ပါ။\nဥပမာ- `/cal 100 + 500`")
            return
        result = simple_eval(msg_parts[1])
        bot.reply_to(message, f" **ရလဒ်:** {result}")
    except:
        bot.reply_to(message, " တွက်ချက်မှု မှားယွင်းနေပါသည်။")

@bot.message_handler(commands=['rule'])
def show_rules(message):
    bot.reply_to(message, RULES_TEXT)

@bot.message_handler(commands=['random'])
def random_hero(message):
    bot.reply_to(message, f" သင်ဆော့ရမယ့် Hero: **{random.choice(HEROES)}**")

@bot.message_handler(content_types=['text', 'sticker'])
def monitor_messages(message):
    if message.chat.type != 'private':
        uid = message.from_user.id
        now = time.time()
        u_data = user_spam_data[uid]

        if now - u_data["start_time"] > 6:
            u_data["count"] = 1
            u_data["start_time"] = now
        else:
            u_data["count"] += 1

        if u_data["count"] == 5 and (now - u_data["start_time"]) <= 5:
            bot.send_message(message.chat.id, f" @{message.from_user.username} Sticker/Text/Emoji မ Spam ပါနဲ့ဦး။")

        if u_data["count"] >= 7 and (now - u_data["start_time"]) <= 6:
            try:
                bot.restrict_chat_member(message.chat.id, uid, until_date=int(time.time() + 600))
                bot.send_message(message.chat.id, f" @{message.from_user.username} ကို ၁၀ မိနစ် Mute လိုက်ပါပြီ။")
            except: pass
            return

        if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
            try:
                ai_res = model.generate_content(message.text)
                bot.reply_to(message, ai_res.text)
            except: pass

bot.infinity_polling()
