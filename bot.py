import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import re
from config import TOKEN, BITRIX_WEBHOOK_URL, manager_username, BITRIX_FIELDS, courses ,BITRIX_DEAL_SETTINGS  
from text import MESSAGES, BUTTONS
import random


bot = telebot.TeleBot(TOKEN)

user_states = {}


def create_courses_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for course_id, course_info in courses.items():
        row = [
            InlineKeyboardButton(course_info["name"], callback_data=f"course_{course_id}"),
        ]
        keyboard.add(*row)
    return keyboard

def create_payment_method_keyboard(course_id, language="ru"):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(BUTTONS[language]["online_payment"], callback_data=f"payment_online_{course_id}"),
        InlineKeyboardButton(BUTTONS[language]["manager_consultation"], callback_data=f"payment_manager_{course_id}"),
        InlineKeyboardButton(BUTTONS[language]["back_to_courses"], callback_data="back_to_courses")
    )
    return keyboard

def create_tariffs_keyboard(course_id, language="ru"):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for tariff_id, tariff_info in courses[course_id]["tariffs"].items():
        button_text = f"{tariff_info['name']} "
        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"tariff_{course_id}_{tariff_id}"))
    keyboard.add(InlineKeyboardButton(BUTTONS[language]["back_to_courses"], callback_data="back_to_courses"))
    return keyboard

def get_random_manager(course_id):
    """Функция для выбора случайного менеджера из списка ответственных за курс"""
    if course_id in courses and "responsible_managers" in courses[course_id]:
        return random.choice(courses[course_id]["responsible_managers"])
    return {"name": "Менеджер", "bitrix_id": "1"} 

@bot.message_handler(commands=['start'])
def start_handler(message):
    referrer = message.text.split(" ")[-1] if " " in message.text else None
    
    # Создаем инлайн клавиатуру для выбора языка
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_tj = InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="lang_tj")
    btn_ru = InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    keyboard.add(btn_tj, btn_ru)
    
    user_states[message.from_user.id] = {
        "referrer": referrer,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name if message.from_user.last_name else ""
    }
    
    # Отправляем приветственное сообщение с выбором языка
    bot.send_message(
        message.chat.id,
        "👋 Ассалому алейкум!\n\nЗабони худро интихоб кунед / Выберите ваш язык:",
        reply_markup=keyboard
    )

# Добавляем новый обработчик для инлайн кнопок выбора языка
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def language_callback(call):
    user_id = call.from_user.id
    language = call.data.split("_")[1]
    
    if user_id not in user_states:
        user_states[user_id] = {}
    
    user_states[user_id]["language"] = language
    user_states[user_id]["waiting_for_phone"] = True
    user_states[user_id]["last_message_id"] = None  # Илова кардани ID-и паёми охирин
    
    # Нест кардани паёми интихоби забон
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Сохтани клавиатура барои рақами телефон
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = telebot.types.KeyboardButton(text=BUTTONS[language]["send_phone"], request_contact=True)
    keyboard.add(button_phone)
    
    # Фиристодани паёми нав ва сабти ID-и он
    sent_message = bot.send_message(
        call.message.chat.id,
        MESSAGES[language]["welcome"],
        reply_markup=keyboard
    )
    user_states[user_id]["last_message_id"] = sent_message.message_id

@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    user_id = message.from_user.id
    phone = message.contact.phone_number.replace(" ", "")
    if not phone.startswith("+"):
        phone = f"+{phone}"
    
    if user_id not in user_states:
        user_states[user_id] = {
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name if message.from_user.last_name else "",
            "referrer": None,
            "language": "ru"  # язык по умолчанию
        }
    
    language = user_states[user_id].get("language", "ru")
    user_states[user_id]["phone"] = phone
    user_states[user_id]["waiting_for_phone"] = False

    # Нест кардани паёми қаблӣ агар вуҷуд дошта бошад
    if "last_message_id" in user_states[user_id]:
        try:
            bot.delete_message(message.chat.id, user_states[user_id]["last_message_id"])
        except:
            pass
    
    # Фиристодани паёми нав ва сабти ID-и он
    sent_message = bot.send_message(
        message.chat.id,
        MESSAGES[language]["phone_accepted"], 
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )
    user_states[user_id]["last_message_id"] = sent_message.message_id

    sent_message = bot.send_message(
        message.chat.id,
        MESSAGES[language]["choose_course"],
        reply_markup=create_courses_keyboard()
    )
    user_states[user_id]["last_message_id"] = sent_message.message_id

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id].get("waiting_for_phone", False))
def manual_phone_handler(message):
    user_id = message.from_user.id
    language = user_states[user_id].get("language", "ru")
    
    # Очищаем номер телефона от всего, кроме цифр
    phone_text = re.sub(r'\D', '', message.text)
    
    # Проверяем, является ли введенный текст номером телефона
    if not phone_text:
        bot.send_message(
            message.chat.id,
            MESSAGES[language]["phone_invalid"]
        )
        return
    
    # Проверяем длину номера телефона (обычно от 10 до 15 цифр)
    if len(phone_text) < 10 or len(phone_text) > 15:
        bot.send_message(
            message.chat.id,
            MESSAGES[language]["phone_invalid_length"]
        )
        return
    
    # Форматируем номер телефона в международном формате
    if not phone_text.startswith("7") and not phone_text.startswith("8"):
        phone = f"+{phone_text}"
    elif phone_text.startswith("8"):
        phone = f"+7{phone_text[1:]}"
    else:
        phone = f"+{phone_text}"
    
    # Сохраняем номер телефона
    if user_id not in user_states:
        user_states[user_id] = {
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name if message.from_user.last_name else "",
            "referrer": None,
            "language": "ru"  # язык по умолчанию
        }
    
    user_states[user_id]["phone"] = phone
    user_states[user_id]["waiting_for_phone"] = False
    
    bot.send_message(
        message.chat.id,
        MESSAGES[language]["phone_accepted"], 
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )
    
    bot.send_message(
        message.chat.id,
        MESSAGES[language]["choose_course"],
        reply_markup=create_courses_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data == "back_to_courses")
def back_to_courses_callback(call):
    user_id = call.from_user.id
    language = user_states[user_id].get("language", "ru")
    
    # Нест кардани паёми ҷорӣ
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Фиристодани паёми нав ва сабти ID-и он
    sent_message = bot.send_message(
        call.message.chat.id,
        MESSAGES[language]["choose_course"],
        reply_markup=create_courses_keyboard()
    )
    user_states[user_id]["last_message_id"] = sent_message.message_id

@bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
def course_callback(call):
    user_id = call.from_user.id
    language = user_states[user_id].get("language", "ru")
    course_id = call.data.split("_")[1]
    
    if course_id not in courses:
        bot.answer_callback_query(call.id, MESSAGES[language]["course_not_found"])
        return
        
    course_name = courses[course_id]["name"]
    
    if user_id not in user_states:
        user_states[user_id] = {
            "first_name": call.from_user.first_name,
            "last_name": call.from_user.last_name if call.from_user.last_name else "",
            "language": language
        }
    
    user_states[user_id]["selected_course"] = course_id
    
    random_manager = get_random_manager(course_id)
    user_states[user_id]["assigned_manager"] = random_manager
    
    # Нест кардани паёми қаблӣ
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Фиристодани паёми нав ва сабти ID-и он
    sent_message = bot.send_message(
        call.message.chat.id,
        MESSAGES[language]["choose_payment"],
        reply_markup=create_payment_method_keyboard(course_id, language)
    )
    user_states[user_id]["last_message_id"] = sent_message.message_id

@bot.callback_query_handler(func=lambda call: call.data.startswith("payment_online_"))
def payment_online_callback(call):
    user_id = call.from_user.id
    language = user_states[user_id].get("language", "ru")
    course_id = call.data.split("_")[2]
    
    if course_id not in courses:
        bot.answer_callback_query(call.id, MESSAGES[language]["course_not_found"])
        return
        
    course_name = courses[course_id]["name"]
    
    # Проверяем, есть ли номер телефона пользователя
    if user_id not in user_states or "phone" not in user_states[user_id]:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = telebot.types.KeyboardButton(text=BUTTONS[language]["online_payment"], request_contact=True)
        keyboard.add(button_phone)
        
        user_states[user_id]["waiting_for_phone"] = True
        
        bot.send_message(
            call.message.chat.id, 
            MESSAGES[language]["phone_required"],
            reply_markup=keyboard
        )
        return
    
    try:
        with open(courses[course_id]["image"], 'rb') as photo:
            bot.send_photo(
                call.message.chat.id,
                photo,
                caption=MESSAGES[language]["tariffs_title"].format(course_name=course_name)
            )
    except Exception as e:
        bot.send_message(
            call.message.chat.id,
            MESSAGES[language]["tariffs_title"].format(course_name=course_name)
        )
    
    # Отправляем список тарифов с указанием языка
    bot.send_message(
        call.message.chat.id,
        MESSAGES[language]["choose_tariff"],
        reply_markup=create_tariffs_keyboard(course_id, language)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("payment_manager_"))
def payment_manager_callback(call):
    user_id = call.from_user.id
    language = user_states[user_id].get("language", "ru")  # Гирифтани забони корбар
    course_id = call.data.split("_")[2]
    
    if course_id not in courses:
        bot.answer_callback_query(call.id, MESSAGES[language]["course_not_found"])
        return
        
    if user_id not in user_states or "phone" not in user_states[user_id]:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = telebot.types.KeyboardButton(text=BUTTONS[language]["manager_consultation"], request_contact=True)
        keyboard.add(button_phone)
        
        user_states[user_id]["waiting_for_phone"] = True
        
        bot.send_message(
            call.message.chat.id, 
            MESSAGES[language]["phone_required"],
            reply_markup=keyboard
        )
        return
    
    course_name = courses[course_id]["name"]
    
    if "assigned_manager" not in user_states[user_id]:
        user_states[user_id]["assigned_manager"] = get_random_manager(course_id)
    
    responsible_manager_name = user_states[user_id]["assigned_manager"]["name"]
    
    create_bitrix_deal(user_id, course_id, None, "Через менеджера")
    
    manager_chat_url = f"https://t.me/{manager_username.replace('@', '')}"
    predefined_message = MESSAGES[language]["manager_predefined_message"].format(
        manager_name=responsible_manager_name,
        course_name=course_name
    )
    direct_chat_url = f"{manager_chat_url}?start={course_id}&text={requests.utils.quote(predefined_message)}"
    
    bot.send_message(
        call.message.chat.id,
        MESSAGES[language]["manager_consultation"].format(course_name=course_name)
    )
    
    redirect_keyboard = InlineKeyboardMarkup()
    redirect_keyboard.add(InlineKeyboardButton(BUTTONS[language]["chat_with_manager"], url=direct_chat_url))
    redirect_keyboard.add(InlineKeyboardButton(BUTTONS[language]["request_call"], callback_data=f"call_request_{course_id}"))
    redirect_keyboard.add(InlineKeyboardButton(BUTTONS[language]["back_to_courses"], callback_data="back_to_courses"))

    bot.send_message(
        call.message.chat.id,
        MESSAGES[language]["choose_contact_method"],
        reply_markup=redirect_keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("call_request_"))
def call_request_callback(call):
    user_id = call.from_user.id
    language = user_states[user_id].get("language", "ru")  # Гирифтани забони корбар
    course_id = call.data.split("_")[2]
    
    if course_id not in courses:
        bot.answer_callback_query(call.id, MESSAGES[language]["course_not_found"])
        return
    
    if user_id not in user_states or "phone" not in user_states[user_id]:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = telebot.types.KeyboardButton(text=BUTTONS[language]["manager_consultation"], request_contact=True)
        keyboard.add(button_phone)
        
        user_states[user_id]["waiting_for_phone"] = True
        
        bot.send_message(
            call.message.chat.id, 
            MESSAGES[language]["phone_required"],
            reply_markup=keyboard
        )
        return
    
    course_name = courses[course_id]["name"]
    
    # Создаем сделку в Битрикс с отметкой о запросе звонка
    create_bitrix_deal(user_id, course_id, None, "Через менеджера", call_requested=True)
    
    bot.send_message(
        call.message.chat.id,
        MESSAGES[language]["call_request_success"],
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(BUTTONS[language]["back_to_courses"], callback_data="back_to_courses")
        )
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff_"))
def tariff_callback(call):
    user_id = call.from_user.id
    _, course_id, tariff_id = call.data.split("_")
    
    language = user_states[user_id].get("language", "ru")
    
    if course_id not in courses or tariff_id not in courses[course_id]["tariffs"]:
        bot.answer_callback_query(call.id, MESSAGES[language]["tariff_not_found"])
        return
    
    course_name = courses[course_id]["name"]
    tariff_info = courses[course_id]["tariffs"][tariff_id]

    if user_id not in user_states or "phone" not in user_states[user_id]:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = telebot.types.KeyboardButton(text=BUTTONS[language]["send_phone"], request_contact=True)
        keyboard.add(button_phone)
        
        user_states[user_id]["waiting_for_phone"] = True
        
        bot.send_message(
            call.message.chat.id, 
            MESSAGES[language]["phone_required"],
            reply_markup=keyboard
        )
        return
    
    user_states[user_id]["selected_tariff"] = tariff_id
    
    bot.send_message(
        call.message.chat.id,
        MESSAGES[language]["tariff_details"].format(
            tariff_name=tariff_info['name'],
            tariff_price=tariff_info['price'],
            tariff_info=tariff_info['info'][language]
        )
    )
    
    payment_keyboard = InlineKeyboardMarkup(row_width=1)
    payment_keyboard.add(
        InlineKeyboardButton(BUTTONS[language]["pay_online"], url=tariff_info["link"]),
        InlineKeyboardButton(BUTTONS[language]["back_to_courses"], callback_data="back_to_courses")
    )
    
    bot.send_message(
        call.message.chat.id,
        MESSAGES[language]["payment_buttons"],
        reply_markup=payment_keyboard
    )
    
    create_bitrix_deal(user_id, course_id, tariff_id, "Онлайн")

def create_bitrix_deal(user_id, course_id, tariff_id, payment_method, call_requested=False):
    if user_id not in user_states or "phone" not in user_states[user_id]:
        return
        
    course_name = courses[course_id]["name"]
    
    # Если менеджер еще не назначен, назначаем случайного
    if "assigned_manager" not in user_states[user_id]:
        user_states[user_id]["assigned_manager"] = get_random_manager(course_id)
    
    responsible_manager_id = user_states[user_id]["assigned_manager"]["bitrix_id"]
    
    # Получаем информацию о тарифе, если он указан
    tariff_name = "Не указан"
    tariff_price = 0
    if tariff_id and tariff_id in courses[course_id]["tariffs"]:
        tariff_info = courses[course_id]["tariffs"][tariff_id]
        tariff_name = tariff_info["name"]
        tariff_price = int(tariff_info["price"])
    
    try:
        # Получаем данные пользователя
        referrer = user_states[user_id].get("referrer")
        first_name = user_states[user_id].get("first_name", "")
        last_name = user_states[user_id].get("last_name", "")
        
        user_name = f"{first_name} {last_name}".strip()
        if not user_name:
            user_name = f"User {user_id}"
        
        contact_response = requests.get(
            f"{BITRIX_WEBHOOK_URL}/crm.contact.list", 
            params={"FILTER[PHONE]": user_states[user_id]["phone"]}, 
            timeout=10
        )
        contact_response.raise_for_status()
        contact_data = contact_response.json()

        contact_id = None
        if "result" in contact_data and len(contact_data["result"]) > 0:
            contact_id = contact_data["result"][0]["ID"]
        else:
            contact_create = requests.post(
                f"{BITRIX_WEBHOOK_URL}/crm.contact.add", 
                json={
                    "fields": {
                        "NAME": first_name,
                        "LAST_NAME": last_name,
                        "PHONE": [{"VALUE": user_states[user_id]["phone"], "VALUE_TYPE": "WORK"}],
                    }
                }, 
                timeout=10
            )
            contact_create.raise_for_status()
            contact_id = contact_create.json().get("result")
        
        deal_data = {
            "fields": {
                BITRIX_FIELDS["title"]: f"{BITRIX_DEAL_SETTINGS['title_prefix']}{course_name}",
                BITRIX_FIELDS["type"]: BITRIX_DEAL_SETTINGS["deal_type"],
                BITRIX_FIELDS["stage"]: BITRIX_DEAL_SETTINGS["new_stage"],
                BITRIX_FIELDS["price"]: tariff_price,
                "CONTACT_ID": contact_id,
                BITRIX_FIELDS["course"]: course_name,
                BITRIX_FIELDS["tariff_name"]: tariff_name,
                BITRIX_FIELDS["referral"]: referrer if referrer else BITRIX_DEAL_SETTINGS["no_referrer_text"],
                BITRIX_FIELDS.get("payment_method", "UF_CRM_PAYMENT_METHOD"): payment_method,
                "ASSIGNED_BY_ID": responsible_manager_id,
                # Добавляем новое поле для запроса звонка
                BITRIX_FIELDS.get("call_requested"): BITRIX_DEAL_SETTINGS["call_request_text"] if call_requested else BITRIX_DEAL_SETTINGS["no_call_request_text"]
            }
        }

        response = requests.post(
            f"{BITRIX_WEBHOOK_URL}/crm.deal.add", 
            json=deal_data, 
            timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as e:
        bot.send_message(
            user_id, 
            MESSAGES["server_error"].format(manager_username=manager_username)
        )
    except Exception as e:
        bot.send_message(
            user_id, 
            MESSAGES["general_error"].format(manager_username=manager_username)
        )

if __name__ == "__main__":
    bot.polling(none_stop=True)