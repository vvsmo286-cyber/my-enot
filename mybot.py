import asyncio, random, os, json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'
ADMIN_ID = "6032049080"

# --- ФИКС RENDER ---
async def handle(r): return web.Response(text="Enot 3.5: Profile & Career")
async def start_web():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    try: await web.TCPSite(runner, '0.0.0.0', 10000).start()
    except: pass

# --- ДАННЫЕ ---
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

def get_user(uid, name="Неизвестный енот"):
    uid = str(uid)
    if uid not in user_data:
        is_admin = (uid == ADMIN_ID)
        user_data[uid] = {
            'name': name,
            'coins': 10000 if is_admin else 100,
            'title': "Енот Полоскун" if is_admin else "🦴 Новичок",
            'job_lvl': 0, 'work_count': 0, 'items': []
        }
    if uid == ADMIN_ID:
        if user_data[uid]['coins'] < 10000: user_data[uid]['coins'] = 10000
        user_data[uid]['title'] = "Енот Полоскун"
    return user_data[uid]

# --- КЛАВИАТУРЫ ---
def get_main_menu(uid):
    u = get_user(uid); b = InlineKeyboardBuilder()
    b.button(text="👤 Мой Профиль", callback_data="open_profile")
    b.button(text="🛠 Работа", callback_data="go_work")
    b.button(text="🎮 Игры", callback_data="open_games")
    b.button(text="🛒 Магазин", callback_data="open_shop")
    b.button(text="📦 Кейс (100)", callback_data="open_case")
    if str(uid) == ADMIN_ID: b.button(text="💎 VIP СКЛАД", callback_data="admin_shop")
    b.adjust(1, 2, 2, 1); return b.as_markup()

async def main():
    load_data(); await start_web()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(F.text.lower().in_(["профиль", "енот", "/start", "меню"]))
    async def cmd_start(m: types.Message):
        get_user(m.from_user.id, m.from_user.first_name)
        save_all()
        await m.answer(f"🦝 Мега-Енот готов к чилу!", reply_markup=get_main_menu(m.from_user.id))

    # --- ЛОГИКА ПРОФИЛЯ ---
    @dp.callback_query(F.data == "open_profile")
    async def profile(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        job = JOBS[u['job_lvl']]
        items_str = ", ".join(u['items']) if u['items'] else "Пусто"
        res = (
            f"👤 **ПРОФИЛЬ ЕНОТА**\n"
            f"━━━━━━━━━━━━━━\n"
            f"🏷 **Ник:** {u.get('name', 'Друг')}\n"
            f"🆔 **ID:** `{c.from_user.id}`\n"
            f"🏆 **Титул:** {u['title']}\n"
            f"💰 **Баланс:** {u['coins']} монет\n\n"
            f"🛠 **Работа:** {job['name']}\n"
            f"📈 **Смены:** {u['work_count']}/{job['goal']}\n"
            f"🎒 **Вещи:** {items_str}\n"
            f"━━━━━━━━━━━━━━"
        )
        b = InlineKeyboardBuilder(); b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text(res, reply_markup=b.as_markup(), parse_mode="Markdown")

    # --- ЛОГИКА РАБОТЫ ---
    @dp.callback_query(F.data == "go_work")
    async def work_choice(c: types.CallbackQuery):
        u = get_user(c.from_user.id); b = InlineKeyboardBuilder()
        b.button(text=f"🏢 {JOBS[u['job_lvl']]['name']}", callback_data="work_normal")
        b.button(text="🤫 Контрабанда", callback_data="work_smuggle")
        b.button(text="🔙 Назад", callback_data="to_menu")
        b.adjust(1); await c.message.edit_text("Куда пойдем работать?", reply_markup=b.as_markup())

    @dp.callback_query(F.data == "work_normal")
    async def work_normal(c: types.CallbackQuery):
        u = get_user(c.from_user.id); job = JOBS[u['job_lvl']]
        if job['name'] == "🪓 Лесоруб":
            b = InlineKeyboardBuilder(); b.button(text="🪓 УДАРИТЬ!", callback_data="wood_hit")
            await c.message.edit_text("🌲 Жди момента...", reply_markup=b.as_markup())
            await asyncio.sleep(random.uniform(1, 3))
            await c.message.edit_text("🪵 УДАРЯЙ СЕЙЧАС!", reply_markup=b.as_markup())
        else:
            multi = 2.0 if "Корона" in u['items'] else 1.0
            pay = int(job['pay'] * multi); u['coins'] += pay; u['work_count'] += 1
            if u['work_count'] >= job['goal'] and u['job_lvl'] < 4: u['job_lvl'] += 1; u['work_count'] = 0
            save_all(); await c.answer(f"+{pay}💰"); await c.message.edit_text("Смена окончена!", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "wood_hit")
    async def wood_hit(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if "УДАРЯЙ СЕЙЧАС" in c.message.text:
            u['coins'] += 100; u['work_count'] += 1; save_all()
            await c.answer("🎯 +100💰", show_alert=True)
        else: await c.answer("🛑 Мимо!", show_alert=True)
        await c.message.edit_text("Возвращаемся...", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "work_smuggle")
    async def smuggle(c: types.CallbackQuery):
        u = get_user(c.from_user.id); b = InlineKeyboardBuilder()
        sw = random.choice(["Лес", "Мост", "Тоннель"])
        hint = f"\n💡 Очки подсказывают: {sw}" if "Очки" in u['items'] else ""
        for w in ["Лес", "Мост", "Тоннель"]: b.button(text=w, callback_data=f"sm_{w}_{sw}")
        b.adjust(1); await c.message.edit_text(f"📦 Выбери путь:{hint}", reply_markup=b.as_markup())

    @dp.callback_query(F.data.startswith("sm_"))
    async def smug_res(c: types.CallbackQuery):
        u = get_user(c.from_user.id); d = c.data.split("_")
        if d == d: u['coins'] += 300; m = "✅ Успех! +300💰"
        else: u['coins'] -= 100; m = "💢 Облава! -100💰"
        save_all(); await c.answer(m, show_alert=True); await c.message.edit_text(m, reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_shop")
    async def shop(c: types.CallbackQuery):
        b = InlineKeyboardBuilder()
        b.button(text="🧤 Перчатки (500)", callback_data="buy_перчатки")
        b.button(text="🚲 Велик (1350)", callback_data="buy_велосипед")
        b.button(text="🎒 Рюкзак (6000)", callback_data="buy_рюкзак")
        b.button(text="🔙 Назад", callback_data="to_menu")
        b.adjust(1); await c.message.edit_text("🛒 МАГАЗИН:", reply_markup=b.as_markup())

    @dp.callback_query(F.data == "admin_shop")
    async def admin(c: types.CallbackQuery):
        if str(c.from_user.id) != ADMIN_ID: return
        b = InlineKeyboardBuilder()
        b.button(text="🧼 Золотой Тазик (10к)", callback_data="buy_тазик")
        b.button(text="👓 Инж. Очки (5к)", callback_data="buy_очки")
        b.button(text="👑 Корона (25к)", callback_data="buy_корона")
        b.button(text="🔙 Назад", callback_data="to_menu")
        b.adjust(1); await c.message.edit_text("💎 VIP СКЛАД:", reply_markup=b.as_markup())

    @dp.callback_query(F.data.startswith("buy_"))
    async def buying(c: types.CallbackQuery):
        u = get_user(c.from_user.id); item = c.data.split("_")
        p = {"перчатки": 500, "велосипед": 1350, "рюкзак": 6000, "тазик": 10000, "очки": 5000, "корона": 25000}
        it_name = item.capitalize()
        if u['coins'] < p[item]: return await c.answer("Мало монет!", show_alert=True)
        if it_name in u['items']: return await c.answer("Уже есть!", show_alert=True)
        u['coins'] -= p[item]; u['items'].append(it_name); save_all()
        await c.answer(f"Куплено: {it_name}!"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_case")
    async def open_c(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 100: return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= 100; r = random.choices(list(TITLES.keys()), weights=); u['title'] = random.choice(TITLES[r]); save_all()
        await c.answer(f"📦 Твой титул: {u['title']}", show_alert=True); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "to_menu")
    async def back(c: types.CallbackQuery): await c.message.edit_text("🦝 Меню:", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_games")
    async def g_menu(c: types.CallbackQuery):
        b = InlineKeyboardBuilder(); b.button(text="🎰 Слоты", callback_data="st_slots")
        b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🎮 Игры:", reply_markup=b.as_markup())

    print("🚀 ЕНОТ 3.5 С ПРОФИЛЕМ ЗАПУЩЕН!"); await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
