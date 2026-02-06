import asyncio, random, os, json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from fractions import Fraction

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'
ADMIN_ID = "6032049080"

async def handle(r): return web.Response(text="Mega Enot Ultimate Alive")
async def start_web():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    try: await web.TCPSite(runner, '0.0.0.0', 10000).start()
    except: pass

user_data = {}
TITLES = {
    "редкие": ["Енот пляжный", "Абобус", "Крутыш", "Зарядник"],
    "сверхредкие": ["Стив", "Мишка Фредди", "Игроман", "Школьник читер666"],
    "мифические": ["Перкусрак", "Роблоксиан", "Майнкрафтер", "Бизнес енот", "Студент читер 777"],
    "легендарные": ["Енот Бармен", "Ручка Без башни", "Легомен", "Босс 67"],
    "ультралегендарные": ["Енот шлепа", "Тюлень", "Тюлень 2.0"]
}
JOBS = [
    {"name": "🧹 Дворник", "pay": 50, "goal": 70},
    {"name": "📦 Доставщик", "pay": 80, "goal": 140},
    {"name": "🪓 Лесоруб", "pay": 100, "goal": 500},
    {"name": "💻 Программист", "pay": 110, "goal": 210},
    {"name": "💰 Бизнесмен", "pay": 160, "goal": 9999}
]

def load_data():
    global user_data
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r") as f: user_data = json.load(f)
        except: user_data = {}

def save_all():
    try:
        with open("users.json", "w") as f: json.dump(user_data, f)
    except: pass

def get_user(uid, name="Енотик"):
    uid = str(uid)
    if uid not in user_data:
        is_admin = (uid == ADMIN_ID)
        user_data[uid] = {'name': name, 'coins': 10000 if is_admin else 100, 'title': "Енот Полоскун" if is_admin else "🦴 Новичок", 'job_lvl': 0, 'work_count': 0, 'items': []}
    if uid == ADMIN_ID:
        user_data[uid]['title'] = "Енот Полоскун"
        if user_data[uid]['coins'] < 10000: user_data[uid]['coins'] = 10000
    return user_data[uid]

def get_main_menu(uid):
    u = get_user(uid); b = InlineKeyboardBuilder()
    b.button(text="👤 Профиль", callback_data="open_profile")
    b.button(text="🛠 Работа", callback_data="go_work")
    b.button(text="🎮 Игры", callback_data="open_games")
    b.button(text="🛒 Магазин", callback_data="open_shop")
    b.button(text="🧮 Калькулятор", callback_data="st_calc")
    b.button(text="📦 Кейс (100)", callback_data="open_case")
    if str(uid) == ADMIN_ID: b.button(text="💎 VIP СКЛАД", callback_data="admin_shop")
    return b.adjust(1, 2, 2, 1, 1).as_markup()

async def main():
    load_data(); await start_web()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(lambda m: m.text and m.text.lower() in ["игры", "меню", "енот", "/start", "профиль"])
    async def cmd_start(m: types.Message):
        get_user(m.from_user.id, m.from_user.first_name); save_all()
        await m.answer(f"🦝 **Енот на чиле ULTIMATE** запущен!", reply_markup=get_main_menu(m.from_user.id))

    @dp.callback_query(F.data == "open_profile")
    async def profile(c: types.CallbackQuery):
        u = get_user(c.from_user.id); job = JOBS[u['job_lvl']]; items_str = ", ".join(u['items']) if u['items'] else "Пусто"
        res = f"👤 **ПРОФИЛЬ**\n🏆 Титул: {u['title']}\n💰 Баланс: {u['coins']}\n🛠 Работа: {job['name']}\n📈 Смены: {u['work_count']}/{job['goal']}\n🎒 Вещи: {items_str}"
        await c.message.edit_text(res, reply_markup=InlineKeyboardBuilder().button(text="🔙 Назад", callback_data="to_menu").as_markup())

    @dp.callback_query(F.data == "go_work")
    async def work_choice(c: types.CallbackQuery):
        u = get_user(c.from_user.id); b = InlineKeyboardBuilder()
        b.button(text=f"🏢 {JOBS[u['job_lvl']]['name']}", callback_data="work_normal")
        b.button(text="🤫 Контрабанда", callback_data="work_smuggle")
        b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("Выбери путь:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data == "work_normal")
    async def work_normal(c: types.CallbackQuery):
        u = get_user(c.from_user.id); job = JOBS[u['job_lvl']]
        if job['name'] == "🪓 Лесоруб":
            await c.message.edit_text("🌲 Жди...", reply_markup=InlineKeyboardBuilder().button(text="🪓 УДАР!", callback_data="wood_hit").as_markup())
            await asyncio.sleep(random.uniform(1.2, 2.5))
            await c.message.edit_text("🪵 УДАРЯЙ СЕЙЧАС!", reply_markup=InlineKeyboardBuilder().button(text="🪓 УДАР!", callback_data="wood_hit").as_markup())
        else:
            pay = int((job['pay'] + (150 if "Рюкзак" in u['items'] else 0)) * (2.0 if "Корона" in u['items'] else 1.0))
            u['coins'] += pay; u['work_count'] += 1
            if u['work_count'] >= job['goal'] and u['job_lvl'] < 4: u['job_lvl'] += 1; u['work_count'] = 0
            save_all(); await c.answer(f"+{pay}💰"); await c.message.edit_text("Готово!", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "wood_hit")
    async def wood_hit(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if "УДАРЯЙ СЕЙЧАС" in c.message.text:
            u['coins'] += 100; u['work_count'] += 1; save_all(); await c.answer("🎯 +100", show_alert=True)
        else: await c.answer("🛑 Рано!", show_alert=True)
        await c.message.edit_text("Меню:", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "work_smuggle")
    async def smuggle(c: types.CallbackQuery):
        u = get_user(c.from_user.id); b = InlineKeyboardBuilder(); sw = random.choice(["Лес", "Мост", "Тоннель"])
        hint = f"\n💡 Очки: {sw}" if "Очки" in u['items'] else ""
        for w in ["Лес", "Мост", "Тоннель"]: b.button(text=w, callback_data=f"sm_{w}_{sw}")
        await c.message.edit_text(f"Куда везем?{hint}", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data.startswith("sm_"))
    async def smug_res(c: types.CallbackQuery):
        u = get_user(c.from_user.id); d = c.data.split("_")
        if d[1] == d[2]: u['coins'] += 300; m = "✅ +300"
        else: u['coins'] -= 100; m = "💢 -100"
        save_all(); await c.answer(m, show_alert=True); await c.message.edit_text(m, reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "st_calc")
    async def calc_m(c: types.CallbackQuery): await c.answer("🔢 Просто пиши пример (например 2+2 или 1/2+1/3)", show_alert=True)

    @dp.message(F.text.regexp(r"^(\d+[\+\-\*\/]\d+)$"))
    async def s_calc(m: types.Message):
        try: await m.answer(f"🧩 Ответ: {eval(m.text)}")
        except: pass

    @dp.message(F.text.regexp(r"^(\d+\/\d+[\+\-\*\/]\d+\/\d+)$"))
    async def f_calc(m: types.Message):
        try:
            t = m.text.replace(" ", ""); op = next(o for o in "+-*/" if o in t)
            p = t.split(op); f1, f2 = Fraction(p[0]), Fraction(p[1])
            if op == "+": r = f1 + f2
            elif op == "-": r = f1 - f2
            elif op == "*": r = f1 * f2
            elif op == "/": r = f1 / f2
            await m.answer(f"🍰 Дробь: {r}")
        except: pass

    @dp.callback_query(F.data == "open_shop")
    async def shop(c: types.CallbackQuery):
        b = InlineKeyboardBuilder().button(text="🧤 Перчатки (500)", callback_data="buy_перчатки").button(text="🎒 Рюкзак (6000)", callback_data="buy_рюкзак").button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🛒 Магазин:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data == "admin_shop")
    async def admin(c: types.CallbackQuery):
        if str(c.from_user.id) != ADMIN_ID: return
        b = InlineKeyboardBuilder().button(text="🧼 Тазик (10к)", callback_data="buy_тазик").button(text="👓 Очки (5к)", callback_data="buy_очки").button(text="👑 Корона (25к)", callback_data="buy_корона").button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("💎 VIP:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data.startswith("buy_"))
    async def buy(c: types.CallbackQuery):
        u = get_user(c.from_user.id); item = c.data.split("_")[1]; p = {"перчатки": 500, "рюкзак": 6000, "тазик": 10000, "очки": 5000, "корона": 25000}
        if u['coins'] < p[item]: return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= p[item]; u['items'].append(item.capitalize()); save_all(); await c.answer("Куплено!"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "to_menu")
    async def to_m(c: types.CallbackQuery): await c.message.edit_text("🦝 Меню:", reply_markup=get_main_menu(c.from_user.id))

    print("🚀 ЕНОТ ULTIMATE ЗАПУЩЕН!"); await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
