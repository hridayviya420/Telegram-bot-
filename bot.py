import telebot
from telebot import types
import json
import time
import uuid
from config import 7685911102:AAHw1OMUR88gfzdgy3UAsAjSspYVLSpo-Gk, ADMIN_ID

bot = telebot.TeleBot(7685911102:AAHw1OMUR88gfzdgy3UAsAjSspYVLSpo-Gk)

# Data functions
def load_data():
    with open("data.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data["users"]:
        data["users"][user_id] = {"coins": 0, "referrer": None}
        if " " in message.text:
            ref = message.text.split()[1]
            if ref in data["users"] and ref != user_id:
                data["users"][ref]["coins"] += 1
                data["users"][user_id]["referrer"] = ref
                bot.send_message(ref, "🎁 আপনি ১ কয়েন রেফার বোনাস পেয়েছেন!")
    save_data(data)
    bot.send_message(message.chat.id, "👋 স্বাগতম! আপনি বিজ্ঞাপন দেখে আয় করতে পারেন।", reply_markup=main_menu())

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👁 বিজ্ঞাপন দেখুন", "💰 আমার কয়েন", "📤 উত্তোলন", "👥 রেফার লিঙ্ক")
    return markup

# View Ad
@bot.message_handler(func=lambda m: m.text == "👁 বিজ্ঞাপন দেখুন")
def view_ads(message):
    data = load_data()
    ad = data["ads"][0]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 বিজ্ঞাপন দেখুন", url=ad["url"]))
    markup.add(types.InlineKeyboardButton("✅ আমি দেখেছি", callback_data=f"seen_{ad['id']}"))
    bot.send_message(message.chat.id, f"{ad['title']}\n\nদয়া করে বিজ্ঞাপনটি ১০ সেকেন্ড দেখুন।", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("seen_"))
def seen_ad(call):
    user_id = str(call.from_user.id)
    data = load_data()
    ad_id = int(call.data.split("_")[1])
    ad = next((a for a in data["ads"] if a["id"] == ad_id), None)
    if ad:
        data["users"][user_id]["coins"] += ad["reward"]
        save_data(data)
        bot.answer_callback_query(call.id, "✅ বিজ্ঞাপন দেখার জন্য ধন্যবাদ!")
        bot.send_message(call.message.chat.id, f"🎉 আপনি {ad['reward']} কয়েন পেয়েছেন!")
    else:
        bot.answer_callback_query(call.id, "❌ বিজ্ঞাপন খুঁজে পাওয়া যায়নি।")

# Coin Balance
@bot.message_handler(func=lambda m: m.text == "💰 আমার কয়েন")
def my_coins(message):
    user_id = str(message.from_user.id)
    data = load_data()
    coins = data["users"].get(user_id, {}).get("coins", 0)
    bot.send_message(message.chat.id, f"💰 আপনার বর্তমান কয়েন: {coins}")

# Referral
@bot.message_handler(func=lambda m: m.text == "👥 রেফার লিঙ্ক")
def referral(message):
    user_id = str(message.from_user.id)
    bot.send_message(message.chat.id, f"🔗 আপনার রেফার লিঙ্ক:\nhttps://t.me/{bot.get_me().username}?start={user_id}")

# Withdraw
@bot.message_handler(func=lambda m: m.text == "📤 উত্তোলন")
def withdraw(message):
    user_id = str(message.from_user.id)
    msg = bot.send_message(message.chat.id, "🧾 আপনার বিকাশ/নগদ নাম্বার দিন:")
    bot.register_next_step_handler(msg, process_withdraw)

def process_withdraw(message):
    user_id = str(message.from_user.id)
    number = message.text.strip()
    data = load_data()
    coins = data["users"][user_id]["coins"]
    if coins < 10:
        bot.send_message(message.chat.id, "❌ উত্তোলনের জন্য ন্যূনতম ১০ কয়েন দরকার।")
        return
    data["users"][user_id]["coins"] -= 10
    data["withdrawals"].append({"user": user_id, "number": number, "id": str(uuid.uuid4())})
    save_data(data)
    bot.send_message(message.chat.id, "✅ উত্তোলনের অনুরোধ গ্রহণ করা হয়েছে। ২৪ ঘণ্টার মধ্যে প্রসেস হবে।")
    bot.send_message(ADMIN_ID, f"📥 নতুন উত্তোলনের অনুরোধ:\n👤 User: {user_id}\n📱 Number: {number}")

bot.polling()
