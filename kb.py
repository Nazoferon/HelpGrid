from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

# Кнопки в нижній панелі
kb_main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
k1 = KeyboardButton('Зв\'язок з спеціалістом')
k2 = KeyboardButton('Новини')
k3 = KeyboardButton('Тарифи')
k4 = KeyboardButton('Як оплатити?')
k5 = KeyboardButton('Додаткові послуги')
k6 = KeyboardButton('Зв\'язок з нами')
k7 = KeyboardButton('Сайт ТТІ', url='http://ttinv.org.ua')
kb_main_menu.add(k2).insert(k3).add(k4).insert(k5).add(k6).insert(k7).add(k1)

kb_news_menu = ReplyKeyboardMarkup(resize_keyboard=True)
k1_news = KeyboardButton('Усі новини')
k2_news = KeyboardButton('Свіжі новини')
k3_news = KeyboardButton('Головне меню')
kb_news_menu.add(k1_news).insert(k2_news).add(k3_news)

kb_pay_menu = ReplyKeyboardMarkup(resize_keyboard=True)
k1_pay = KeyboardButton('Приват24')
k2_pay = KeyboardButton('Ощад24')
k3_pay = KeyboardButton('Монобанк')
k4_pay = KeyboardButton('Реквізити')
k5_pay = KeyboardButton('Оплата через Telegram')
k6_pay = KeyboardButton('Головне меню')
kb_pay_menu.add(k1_pay).insert(k2_pay).add(k3_pay).insert(k4_pay).add(k5_pay).add(k6_pay)

# Кнопки під певними діалогами
ikeyboard_tariffs = InlineKeyboardMarkup()
ikb_tariffs = InlineKeyboardButton(text='Тарифи на сайті',
                                   url='http://ttinv.org.ua/rates/')
ikb_connect_the_internet = InlineKeyboardButton(text='Бажаю підключити інтернет', callback_data='connect_the_internet')
ikb_connect_the_tv = InlineKeyboardButton(text='Бажаю підключити телебачення', callback_data='connect_the_tv')
ikeyboard_tariffs.add(ikb_tariffs).add(ikb_connect_the_internet).add(ikb_connect_the_tv)
#=========================================================================

#=========================================================================
ikeyboard_site = InlineKeyboardMarkup()
ik_site = InlineKeyboardButton(text='Сайт ТТІ',
                                url='http://ttinv.org.ua')
ikeyboard_site.add(ik_site)
#=========================================================================
ikeyboard_services = InlineKeyboardMarkup()
ik_services = InlineKeyboardButton(text='Додаткові послуги ТТІ',
                                url='http://ttinv.org.ua/services/')
ikeyboard_services.add(ik_services)
#=========================================================================
ikeyboard_communication = InlineKeyboardMarkup()
ik_communication = InlineKeyboardButton(text='Зв\'язок з нами',
                                url='http://ttinv.org.ua/contacts/')
ikeyboard_communication.add(ik_communication)
#=========================================================================
# ikeyboard_prices = InlineKeyboardMarkup()
# ik_prices_inet1 = InlineKeyboardButton(text='Оптимальний', callback_data='internet_Оптимальний')
# ik_prices_inet2 = InlineKeyboardButton(text='Шалений NET', callback_data='internet_Шалений')
# ik_prices_inet3 = InlineKeyboardButton(text='PON', callback_data='internet_PON')
# ik_prices_tv1 = InlineKeyboardButton(text='Пільговий', callback_data='tv_Пільговий')
# ik_prices_tv2 = InlineKeyboardButton(text='Базовий', callback_data='tv_Базовий')
# ikeyboard_prices.add(ik_prices_inet1, ik_prices_inet2, ik_prices_inet3, ik_prices_tv1, ik_prices_tv2)
ikeyboard_prices = InlineKeyboardMarkup()
ikeyboard_prices.row(
    InlineKeyboardButton(text='Оптимальний', callback_data='_Оптимальний'),
    InlineKeyboardButton(text='Шалений NET', callback_data='_Шалений'),
    InlineKeyboardButton(text='PON', callback_data='_PON')
)
ikeyboard_prices.row(
    InlineKeyboardButton(text='Пільговий', callback_data='_Пільговий'),
    InlineKeyboardButton(text='Базовий', callback_data='_Базовий')
)
ikeyboard_prices.row(
    InlineKeyboardButton(text='PON + ТБ', callback_data='_PON+Телебачення'),
    InlineKeyboardButton(text='Оптимальний + ТБ', callback_data='_Оптимальний+Телебачення'),
    InlineKeyboardButton(text='Шалений + ТБ', callback_data='_Шалений+Телебачення')
)
#=========================================================================