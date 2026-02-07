import asyncio, random, os, json
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'
ADMIN_ID = "6032049080"

# --- СЕРВЕР ---
async def handle(r): return web.Response(text="Enot 100k Final")
async def start_web():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    try: await web.TCPSite(runner, '0.0.0.0', 10000).start()
    except: pass

user_data = {}
TITLES = {
    "редкие": ["Абобус", "Крутыш"],
    "мифические": ["Майнкрафтер", "Бизнес енот"],
    "ультралегендарные": ["Тюлень 2.0"]
}
JOBS = [{"name": "🧹 Дворник", "pay": 50, "goal": 70}, {"name": "🪓 Лесоруб", "pay": 100, "goal": 500}]

def load_data():
    global user_data
    if os.path.exists("users.json"):
        try: with open("users.json", "r") as f: user_data = json.load(f)
        except: user_data = {}

def save_all():
    try: 
        with open("users.json", "w") as f: json.dump(user_data, f)
    except: pass

def get_user(uid):
    uid = str(uid); is_admin = (uid == ADMIN_ID)
    if uid not in user_data:
        user_data[uid] = {'coins': 100000 if is_admin else 100, 'title': "Енот Полоскун" if is_admin else "Новичок", 'job_lvl': 0, 'work_count': 0, 'items': []}
    if is_admin:
        user_data[uid]['coins'] = 100000
        user_data[uid]['title'] = "Енот Полоскун"
    return user_data[uid]

def get_main_menu(uid):
    u = get_user(uid); b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text=f"👤 {u['title']} | 💰 {int(u['coins'])}", callback_data="none"))
    b.button(text="🛠 Работа", callback_data="go_work")
    b.button(text="🎮 Игры", callback_data="open_games")
    b.button(text="📦 Кейс (100💰)", callback_data="open_case")
    return b.adjust(1, 2, 1).as_markup()

async def main():
    load_data(); await start_web()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message()
    async def cmd_all(m: types.Message):
        get_user(m.from_user.id); save_all()
        await m.answer(f"🦝 **Енот на чиле 100К**!", reply_markup=get_main_menu(m.from_user.id))

    @dp.callback_query(F.data == "open_case")
    async def open_case(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 100: return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= 100
        # Исправленные шансы выпадения
        r_key = random.choices(list(TITLES.keys()), weights=[60, 30, 10])[0]
        u['title'] = random.choice(TITLES[r_key]); save_all()
        await c.message.answer(f"📦 Выпал статус: **{u['title']}**")
        await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "go_work")
    async def work(c: types.CallbackQuery):
        u = get_user(c.from_user.id); job = JOBS[u['job_lvl']]
        u['coins'] += job['pay']; u['work_count'] += 1; save_all()
        await c.answer(f"+{job['pay']}💰"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_games")
    async def games(c: types.CallbackQuery):
        u = get_user(c.from_user.id); u['coins'] -= 50; m = await c.message.answer_dice(emoji="🎰"); await asyncio.sleep(3)
        if m.dice.value in [1, 22, 43, 64]: u['coins'] += 1000; await c.message.answer("💎 ДЖЕКПОТ!")
        save_all(); await c.message.answer("Меню:", reply_markup=get_main_menu(c.from_user.id))

    print("🚀 ЕНОТ ЗАПУЩЕН!"); await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


