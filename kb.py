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