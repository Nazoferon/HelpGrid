import kb, text_info, logging, json, asyncio, requests, re, bd_connect
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import PreCheckoutQuery, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN_API, user_id, PAYMENTS_TOKEN, LIQPAY_PRIVATE_KEY, LIQPAY_PUBLIC_KEY
from news import check_news_update_json, search_news
from bs4 import BeautifulSoup
from time import sleep
from aioliqpay import LiqPay
from datetime import datetime, timedelta


# підключаємо бота
bot = Bot(token=TOKEN_API, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def on_startup(_):
    print('Бот успішно запущений')

# Клас зі станами підключення інтернету
class TextState_connect_internet(StatesGroup):
    waiting_for_text = State()
# Клас зі станами підключення телебачення
class TextState_connect_tv(StatesGroup):
    waiting_for_text = State()
# Клас зі станами зв'язку з спеціалістом
class TextState_spec(StatesGroup):
    waiting_for_text = State()

# ID 
ADMIN_CHAT_ID = 6172627661
ADMIN_CONF_ID = -1001744484840

# Метод перевірки користувача на наявність його ID в Чорному списку
def is_user_in_blacklist(user_id):
    conn = bd_connect.sqlite3.connect('usersID.db')
    c = conn.cursor()
    c.execute("SELECT * FROM blacklist WHERE id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Метод перевірки користувача на наявність його ID в базі даних клієнтів
def is_user_in_bd(user_id):
    conn = bd_connect.sqlite3.connect('usersID.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Метод перевірки на введення чисел замість букв
def is_number(input_text):
    return input_text.isdigit()

#===========================START===================================

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
    else:
        await message.answer('Ласкаво просимо до нашого бота 👋\nВикористовуйте команду /help або плитки для керування.', 
        reply_markup=kb.kb_main_menu)
        # await bot.send_sticker(message.from_user.id,
        #                        sticker='CAACAgIAAxkBAAEHm6dj4Q2eNiL4v-vpqPwp86LJYYdSxgACbRQAAvh48Ev_35tLbqKxRy4E',
        #                        reply_markup=kb.kb_main_menu)
        # Перевірка, чи користувач уже збережений в базі даних
        bd_connect.cursor.execute('SELECT * FROM users WHERE id=?', (message.from_user.id,))
        result = bd_connect.cursor.fetchone()
        if result:
            registered = await message.reply('Ви вже зареєстровані в базі даних бота.')
            await asyncio.sleep(3)
            await registered.delete()
        else:
            # Збереження нового користувача в базі даних, якщо його не виявлено
            bd_connect.cursor.execute('INSERT INTO users (id, username, fullname) VALUES (?, ?, ?)', (message.from_user.id, message.from_user.username, message.from_user.full_name))
            bd_connect.conn.commit()
            not_registered = await message.reply('Ваш ID буде зареєстровано в базі даних бота.')
            await asyncio.sleep(3)
            await not_registered.delete()

#===========================HELP=================================
@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
    else:
        await message.answer(text=text_info.HELP_COMMAND, parse_mode='HTML')
        await message.delete()
@dp.message_handler(text='Допомога')
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
    else:
        await message.answer(text=text_info.HELP_COMMAND, parse_mode='HTML')

#=========================TARIFFS================================
@dp.message_handler(commands=['tariffs'])
async def tariffs_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.TARIFFS_TTI, parse_mode='HTML', reply_markup=kb.ikeyboard_tariffs)
@dp.message_handler(text='Тарифи')
async def tariffs_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.TARIFFS_TTI, parse_mode='HTML', reply_markup=kb.ikeyboard_tariffs)    

#підключення послуг

# Функція, яка буде викликатися після натискання кнопки
async def button_callback_handler(message: types.CallbackQuery):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await bot.send_message(chat_id=message.from_user.id, text="Напишіть адресу, за якою буде підключення інтернету(Приклад: Нововолинськ, вулиця\вул. Сагайдачного 37, під'їзд 2, квартира\кв.43)", reply_markup=None)
    # Встановлення стану "очікування тексту"
    await TextState_connect_internet.waiting_for_text.set()

# Реєструємо обробник InlineKeyboardButton
dp.register_callback_query_handler(button_callback_handler, text='connect_the_internet')

# Обробка текстових повідомлень про інтернет
@dp.message_handler(state=TextState_connect_internet.waiting_for_text)
async def send_to_admin_conference(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    # Отримання тексту з повідомлення та перевірка на довжину речення
    text = message.text
    if len(text) < 10:
        await bot.send_message(chat_id=message.from_user.id, text='Ви ввели мало слів для корректного опису підключення послуг. Поновіть ваш текст після натиску на кнопку "Бажаю підключити послугу".', reply_markup=kb.kb_main_menu)
        await state.finish()
    else:
        admin_message = f"👤 Користувач {message.from_user.full_name} (<code>{message.from_user.id}</code>) надіслав повідомлення про підключення інтернету через чат-бота.\n\nТекст повідомлення: <b>{text}</b>"
        await bot.send_message(chat_id=ADMIN_CONF_ID, text=f"<b>ПІДКЛЮЧЕННЯ ПОСЛУГ - ІНТЕРНЕТ</b>\n\n{admin_message}\n\n Щоб відповісти користувачу {message.from_user.id} - Вам потрібно ввести <code>/answ {message.from_user.id}</code> текст...")
        await bot.send_message(chat_id=message.from_user.id, text="Дякуємо за повідомлення, очікуйте подальших інструкцій! ♥", reply_markup=kb.kb_main_menu)
        # Скидання стану
        await state.finish()

# Функція, яка буде викликатися після натискання кнопки
async def button_callback_handler(message: types.CallbackQuery):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await bot.send_message(chat_id=message.from_user.id, text="Напишіть адресу, за якою буде підключення телебачення(Приклад: Нововолинськ, вулиця\вул. Сагайдачного 37, під'їзд 2, квартира\кв.43)", reply_markup=None)
    # Встановлення стану "очікування тексту"
    await TextState_connect_tv.waiting_for_text.set()

# Реєструємо обробник InlineKeyboardButton
dp.register_callback_query_handler(button_callback_handler, text='connect_the_tv')

# Обробка текстових повідомлень про телебачення
@dp.message_handler(state=TextState_connect_tv.waiting_for_text)
async def send_to_admin_conference(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    # Отримання тексту з повідомлення та перевірка на довжину речення
    text = message.text
    if len(text) < 10:
        await bot.send_message(chat_id=message.from_user.id, text='Ви ввели мало слів для корректного опису підключення послуг. Поновіть ваш текст після натиску на кнопку "Бажаю підключити послугу".', reply_markup=kb.kb_main_menu)
        await state.finish()
    else:
        admin_message = f"👤 Користувач {message.from_user.full_name} (<code>{message.from_user.id}</code>) надіслав повідомлення про підключення телебачення через чат-бота.\n\nТекст повідомлення: <b>{text}</b>"
        await bot.send_message(chat_id=ADMIN_CONF_ID, text=f"<b>ПІДКЛЮЧЕННЯ ПОСЛУГ - ТЕЛЕБАЧЕННЯ</b>\n\n{admin_message}\n\n Щоб відповісти користувачу {message.from_user.id} - Вам потрібно ввести <code>/answ {message.from_user.id}</code> текст...")
        await bot.send_message(chat_id=message.from_user.id, text="Дякуємо за повідомлення, очікуйте подальших інструкцій! ♥", reply_markup=kb.kb_main_menu)
        # Скидання стану
        await state.finish()



#============================SERVICES==============================

@dp.message_handler(commands=['services'])
async def services_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.SERVICES, parse_mode='HTML', reply_markup=kb.ikeyboard_services)
@dp.message_handler(text='Додаткові послуги')
async def services_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.SERVICES, parse_mode='HTML', reply_markup=kb.ikeyboard_services)

#=================================COMMUNICATION=============================

@dp.message_handler(commands=['communication'])
async def communication_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.COMMUNICATION, parse_mode='HTML', reply_markup=kb.ikeyboard_communication)
@dp.message_handler(text='Зв\'язок з нами')
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.COMMUNICATION, parse_mode='HTML', reply_markup=kb.ikeyboard_communication)

#==================================SITE===============================

@dp.message_handler(commands=['site'])
async def site_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer('<a href="http://ttinv.org.ua">Сайт ТзОВ "Нововолинське ТТІ (натиснути)"</a>',
                        parse_mode='HTML', reply_markup=kb.ikeyboard_site)
@dp.message_handler(text='Сайт ТТІ')
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer('<a href="http://ttinv.org.ua">Сайт ТзОВ "Нововолинське ТТІ"</a>',
                        parse_mode='HTML', reply_markup=kb.ikeyboard_site)

#===========================================MAIN MENU========================================================

@dp.message_handler(text='Головне меню')
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer('Ви перейшли до головного меню', reply_markup=kb.kb_main_menu)

#===========================================PAY MENU========================================================

@dp.message_handler(text='Як оплатити?')
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer('Ви перейшли до меню з оплатою', reply_markup=kb.kb_pay_menu)
@dp.message_handler(text='Приват24')
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.PRIVAT24, reply_markup=kb.kb_pay_menu)
@dp.message_handler(text='Ощад24')
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.OSHCHAD24, reply_markup=kb.kb_pay_menu)
@dp.message_handler(text='Монобанк')
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.MONOBANK, reply_markup=kb.kb_pay_menu)
@dp.message_handler(text='Реквізити')
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=text_info.REKVIZYTY, reply_markup=kb.kb_pay_menu)

#PRICE
LIQPAY_PUBLIC_KEY = "sandbox_i51470674466"  # Публічний ключ LiqPay
LIQPAY_PRIVATE_KEY = "sandbox_NeqL8uNMwQ0X7EOmDzascREFGpea0ComaTbjCdKI"  # Приватний ключ LiqPay

liqpay = LiqPay(public_key=LIQPAY_PUBLIC_KEY, private_key=LIQPAY_PRIVATE_KEY)

@dp.message_handler(text='Оплата через Telegram')
async def process_buy_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return

    if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, text='Оберіть послугу для оплати:', reply_markup=kb.ikeyboard_prices)

def get_price_for_tariff(tariff):
    prices = {
        '_Оптимальний': '110',
        '_Шалений': '130',
        '_PON': '170',
        '_Пільговий': '70',
        '_Базовий': '99',
        '_PON+Телебачення': '200',
        '_Оптимальний+Телебачення': '170',
        '_Шалений+Телебачення': '190'
    }
    return prices.get(tariff, '0')

@dp.callback_query_handler(lambda c: c.data.startswith('_'))
async def process_tariff_selection(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if is_user_in_blacklist(user_id):
        await bot.send_message(user_id, "Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return

    selected_tariff = callback_query.data
    selected_price = get_price_for_tariff(selected_tariff)
    await bot.send_message(callback_query.from_user.id, f"Ви вибрали тариф <b>{selected_tariff}</b>. Ціна: <b>{selected_price}</b>грн.")

    prices = [
        types.LabeledPrice(
            label='Ціна тарифу',
            amount=int(selected_price) * 100
        )
    ]


    invoice_message = await bot.send_invoice(
        callback_query.from_user.id,
        title=selected_tariff,
        description=' ',
        provider_token=PAYMENTS_TOKEN,
        currency='uah',
        photo_url='https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/LIQPAY_logos.svg/2560px-LIQPAY_logos.svg.png',
        photo_height=100,
        photo_width=250,
        photo_size=100,
        is_flexible=False,
        prices=prices,
        start_parameter='time-machine-example',
        payload='service-payment',
        need_name=True,
        need_phone_number=True,
        need_email=True
    )

@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    payment_info = message.successful_payment
    payment_id = payment_info.provider_payment_charge_id
    payer_name = payment_info.order_info.name
    phone_number = payment_info.order_info.phone_number
    email = payment_info.order_info.email

    payment_info_text = f"ПРОЙШЛА ОПЛАТА\n\n" \
                        f"ID оплати: <b><code>{payment_id}</code></b>\n" \
                        f"Ім'я платника: {payer_name}\n" \
                        f"Мобільний номер платника: <code>+{phone_number}</code>\n" \
                        f"Електронна пошта платника: <code>{email}</code>"

    await bot.send_message(ADMIN_CONF_ID, text=payment_info_text)
    await bot.send_message(message.chat.id, "Дякуємо за оплату! Платіж успішно оброблено.", reply_markup=kb.kb_main_menu)



#===========================================ID===============================================================

@dp.message_handler(commands=['id'])
async def id_commands(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text=f'Ваш ID: <code>{message.from_user.id}</code>')

#===========================================NEWS=============================================================

@dp.message_handler(commands=['news'])
async def news_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    with open("news_dict.json") as file:
        news_dict = json.load(file)
    for k, v in sorted(news_dict.items()):
        news = f"<i><u>{v['news_date']}</u></i>\n" \
            f"{v['news_title']}\n\n" \
            f"{v['news_content']}"
        img = f"{v['news_img']}"
        news_link = f"{v['news_link']}"

        # Плаваюче посилання на новини
        ikeyboard_news = kb.InlineKeyboardMarkup()
        ik_news = kb.InlineKeyboardButton(text=(f"Посилання на повні новини(тиць)"), url=news_link)
        ikeyboard_news.add(ik_news)

        # Повідомлення бота
        await bot.send_photo(chat_id=message.chat.id, photo=img, reply_markup=kb.kb_news_menu)
        await message.answer(news, reply_markup=ikeyboard_news) 

    # await bot.send_photo(chat_id=message.chat.id, photo=search_news.news_img)
    # await message.answer(f"<i><u>{search_news.news_date}</u></i>\n{search_news.news_title}\n\n{search_news.news_content}",
    # parse_mode='HTML', reply_markup=search_news.ikeyboard_news)

@dp.message_handler(text='Новини')
async def news_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer(text='Ви перейшли до меню новин', reply_markup=kb.kb_news_menu)

@dp.message_handler(text='Усі новини')
async def news_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    with open("news_dict.json") as file:
        news_dict = json.load(file)
            
    for k, v in news_dict.items():
        news = f"<i><u>{v['news_date']}</u></i>\n" \
            f"{v['news_title']}\n\n" \
            f"{v['news_content']}"
        img = f"{v['news_img']}"
        news_link = f"{v['news_link']}"

        # Плаваюче посилання на новини
        ikeyboard_news = kb.InlineKeyboardMarkup()
        ik_news = kb.InlineKeyboardButton(text=(f"Посилання на повні новини(тиць)"), url=news_link)
        ikeyboard_news.add(ik_news)

        # Повідомлення бота
        await bot.send_photo(chat_id=message.chat.id, photo=img, reply_markup=kb.kb_news_menu)
        await message.answer(news, reply_markup=ikeyboard_news)
    # await bot.send_photo(chat_id=message.chat.id, photo=search_news.news_img)
    # await message.answer(f"<i><u>{search_news.news_date}</u></i>\n{search_news.news_title}\n\n{search_news.news_content}",
    # parse_mode='HTML', reply_markup=search_news.ikeyboard_news)

@dp.message_handler(text='Свіжі новини')
async def news_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    fresh_news = check_news_update_json()

    if len(fresh_news) >= 1:
        for k, v in fresh_news.items():
            news = f"<i><u>{v['news_date']}</u></i>\n" \
                f"{v['news_title']}\n\n" \
                f"{v['news_content']}"
            img = f"{v['news_img']}"
            news_link = f"{v['news_link']}"

        # Плаваюче посилання на новини
        ikeyboard_news = kb.InlineKeyboardMarkup()
        ik_news = kb.InlineKeyboardButton(text=(f"Посилання на повні новини(тиць)"), url=news_link)
        ikeyboard_news.add(ik_news)

        # Повідомлення бота
        await bot.send_photo(chat_id=message.chat.id, photo=img)
        await message.answer(news, reply_markup=ikeyboard_news)
    else:
        await message.answer(datetime.now().strftime("До %d.%m.%Y %T") + " немає свіжих новин")


async def news_every_minute():
    while True:
        fresh_news = check_news_update_json()
        if len(fresh_news) >= 1:
            for k, v in fresh_news.items():
                news = f"<i><u>{v['news_date']}</u></i>\n" \
                    f"{v['news_title']}\n\n" \
                    f"{v['news_content']}\n"
                img = f"{v['news_img']}"
                news_link = f"{v['news_link']}"

                ikeyboard_news = kb.InlineKeyboardMarkup()
                ik_news = kb.InlineKeyboardButton(text=(f"Посилання на повні новини(тиць)"), url=news_link)
                ikeyboard_news.add(ik_news)
                await bot.send_photo(user_id, photo=img, disable_notification=True)
                await bot.send_message(user_id, news, disable_notification=True, reply_markup=ikeyboard_news)
        else:
            await bot.send_message(user_id, datetime.now().strftime("До %d.%m.%Y %T") + " немає свіжих новин", disable_notification=True)
        await asyncio.sleep(1200)


#====================================================================================================================================================================

# Обробка текстової команди для введення тексту
@dp.message_handler(text='Зв\'язок з спеціалістом')
async def send_text_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer("Ви можете описати свою проблему і вона буде передана спеціалісту 👨‍🏭", reply_markup=None)
    # Встановлення стану "очікування тексту"
    await TextState_spec.waiting_for_text.set()
# Обробка команди для введення тексту
@dp.message_handler(commands=['spec'])
async def send_text_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    await message.answer("Ви можете описати свою проблему і вона буде передана спеціалісту 👨‍🏭", reply_markup=None)
    # Встановлення стану "очікування тексту"
    await TextState_spec.waiting_for_text.set()

# Обробка текстових повідомлень
@dp.message_handler(state=TextState_spec.waiting_for_text)
async def send_to_admin_conference(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    # Отримання тексту з повідомлення та перевірка на довжину речення
    text = message.text
    if len(text) < 10:
        await message.answer('Ви ввели мало слів для корректного опису вашої проблеми. Поновіть вашу проблему після натиску на кнопку "Зв\'язок з спеціалістом" або введення команди /spec')
        await state.finish()
    else:
        admin_message = f"👤 Користувач {message.from_user.full_name} (<code>{message.from_user.id}</code>) надіслав повідомлення через чат-бота.\n\nТекст повідомлення: <b>{text}</b>"
        await bot.send_message(chat_id=ADMIN_CONF_ID, text=f"<b>ТЕХ.НЕПОЛАДКИ</b>\n\n{admin_message}\n\n Щоб відповісти користувачу {message.from_user.id} - Вам потрібно ввести <code>/answ {message.from_user.id}</code> текст...")
        await message.reply("Дякуємо за повідомлення, очікуйте відповіді спеціаліста! ♥")
        # Скидання стану
        await state.finish()

#=================================================ADMINS=======================================================================================

# Відповідь клієнту
@dp.message_handler(commands=["answ"])
async def bot_send_to_client(message: types.Message, command: Text):
    user_id = message.from_user.id
    if is_user_in_blacklist(user_id):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    chat_id = message.chat.id
    user = await bot.get_chat_member(chat_id, user_id)
    if user.is_chat_admin():
        if command.args:
            id_clients = re.findall(r'\d+', command.args)
            if len(id_clients) > 0:
                id_client = id_clients[0]
                client_text = command.args.replace(id_client, '')
                if is_user_in_bd(id_client):
                    if client_text == '':
                        await bot.send_message(chat_id=ADMIN_CONF_ID, text="Ви не ввели ніякого тексту")
                    else:
                        if len(client_text) < 10:
                            await bot.send_message(chat_id=ADMIN_CONF_ID, text="Ви ввели замало слів")
                        else:
                            await bot.send_message(chat_id=id_client, text=f"👨‍🏭 [Спеціаліст]: {client_text}")
                            await bot.send_message(chat_id=ADMIN_CONF_ID, text=f"Відповідь користувачу <code>{id_client}</code> відправлена!")
                else:
                    await bot.send_message(chat_id=ADMIN_CONF_ID, text="Користувач не є нашим клієнтом, перевірте введений ID❗")
            else:
                await bot.send_message(chat_id=ADMIN_CONF_ID, text="Ви ввели некоректний ID клієнта")
        else:
            await bot.send_message(chat_id=ADMIN_CONF_ID, text="Ви не ввели ID клієнта")
    else:
        await message.answer("Помилка доступу до команд❗")


# Додавання ID користувача в Чорний список
@dp.message_handler(commands=['addbl'])
async def add_to_blacklist(message: types.Message, command: Text):
    chat_id = message.chat.id
    user_id_a = message.from_user.id
    user_a = await bot.get_chat_member(chat_id, user_id_a)
    if is_user_in_blacklist(user_id_a):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    else:
        if user_a.is_chat_admin():
            if command.args:
                # Отримуємо ID користувача після команди додавання в ЧС
                client_bl_id = re.findall(r'\d+', command.args)
                if len(client_bl_id) > 0:
                    client_bl_id = client_bl_id[0]
                    if client_bl_id == '':
                        await bot.send_message(chat_id=ADMIN_CONF_ID, text="Ви не ввели ID клієнта")
                    else:
                        # Підключаємося до бази даних SQLite
                        bd_connect.cursor.execute('SELECT * FROM blacklist WHERE id=?', (client_bl_id,))
                        result = bd_connect.cursor.fetchone()
                        if result:
                            registered = await message.reply('Користувач вже знаходиться в Чорному списку.')
                            await asyncio.sleep(3)
                            await registered.delete()
                        else:
                            # Збереження нового користувача в базі даних, якщо його не виявлено
                            bd_connect.cursor.execute('INSERT INTO blacklist (id) VALUES (?)', (client_bl_id,))
                            bd_connect.conn.commit()
                            await message.reply(f"Користувач {client_bl_id} успішно доданий до Чорного списку!")
                else:
                    await bot.send_message(chat_id=ADMIN_CONF_ID, text="Ви ввели некоректний ID клієнта")
            else:
                await bot.send_message(chat_id=ADMIN_CONF_ID, text="Ви не ввели ID клієнта")
        else:
            await message.answer("Помилка доступу до команд❗")



# Команда для перегляду вмісту БД обох таблиць
@dp.message_handler(commands=['view'])
async def view_tables(message: types.Message):
    chat_id = message.chat.id
    user_id_a = message.from_user.id
    user_a = await bot.get_chat_member(chat_id, user_id_a)
    if is_user_in_blacklist(user_id_a):
        await message.reply("Ви знаходитесь в Чорному списку і не можете використовувати функціонал бота.")
        return
    else:
        if user_a.is_chat_admin():
            conn = bd_connect.conn
            cursor = bd_connect.cursor

            cursor.execute("SELECT * FROM users")
            users_data = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count_users = cursor.fetchone()[0]

            response = f"<b>Таблиця ID користувачів[{user_count_users}]:</b>\n"
            for row in users_data:
                response += str(row) + "\n"

            cursor.execute("SELECT * FROM blacklist")
            blacklist_data = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM blacklist")
            user_count_blacklist = cursor.fetchone()[0]
            response += f"\n<b>Таблиця Чорного списку[{user_count_blacklist}]:</b>\n"
            for row in blacklist_data:
                response += str(row) + "\n"

            await bot.send_message(chat_id=chat_id, text=response, parse_mode='HTML')
        else:
            await message.answer("Помилка доступу до команд❗")

#====================================================================================================================================================================
#================================================================GET_ID_GROUP========================================================================================
# @dp.message_handler(commands=['idgr'])
# async def commands_id(message: types.Message):
#         await message.answer(text=f"id вашої групи: {message.chat.id}")
#====================================================================================================================================================================

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    #loop.create_task(news_every_minute())
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)