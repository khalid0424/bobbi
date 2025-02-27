import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from config import TOKEN, BITRIX_WEBHOOK_URL, manager_username, BITRIX_FIELDS, courses

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

def create_payment_method_keyboard(course_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("💳 Оплатить онлайн", callback_data=f"payment_online_{course_id}"),
        InlineKeyboardButton("👨‍💼 Связаться с менеджером", url=f"https://t.me/{manager_username.replace('@', '')}"),
        InlineKeyboardButton("◀️ Назад к курсам", callback_data="back_to_courses")
    )
    return keyboard

def create_tariffs_keyboard(course_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for tariff_id, tariff_info in courses[course_id]["tariffs"].items():
        button_text = f"{tariff_info['name']} "
        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"tariff_{course_id}_{tariff_id}"))
    keyboard.add(InlineKeyboardButton("◀️ Назад к курсам", callback_data="back_to_courses"))
    return keyboard

@bot.message_handler(commands=["start"])
def start_handler(message):
    referrer = message.text.split(" ")[-1] if " " in message.text else None
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = telebot.types.KeyboardButton(text="📱 Отправьте свой номер телефона", request_contact=True)
    keyboard.add(button_phone)

    # Сохраняем имя пользователя и referrer
    user_states[message.from_user.id] = {
        "referrer": referrer,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name if message.from_user.last_name else ""
    }
    
    bot.send_message(
        message.chat.id,
        "👋 АссаламуАъалкум! Мы предлагаем курсы по работе на маркетплейсах. Пожалуйста, отправьте свой номер телефона чтобы продолжить:",
        reply_markup=keyboard
    )

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
            "referrer": None
        }
    
    user_states[user_id]["phone"] = phone

    bot.send_message(
        message.chat.id,
        "✅ Номер принят!", 
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )

    bot.send_message(
        message.chat.id,
        "📚 Выберите интересующий вас курс:",
        reply_markup=create_courses_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data == "back_to_courses")
def back_to_courses_callback(call):
    bot.edit_message_text(
        "📚 Пожалуйста, выберите интересующий вас курс:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=create_courses_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
def course_callback(call):
    user_id = call.from_user.id
    course_id = call.data.split("_")[1]
    
    if course_id not in courses:
        bot.answer_callback_query(call.id, "Курс не найден. Попробуйте выбрать другой.")
        return
        
    course_name = courses[course_id]["name"]
    
    if user_id not in user_states:
        user_states[user_id] = {
            "first_name": call.from_user.first_name,
            "last_name": call.from_user.last_name if call.from_user.last_name else ""
        }
    
    user_states[user_id]["selected_course"] = course_id

    
    
    bot.send_message(
        call.message.chat.id,
        "Выберите способ оплаты:",
        reply_markup=create_payment_method_keyboard(course_id)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("payment_online_"))
def payment_online_callback(call):
    user_id = call.from_user.id
    course_id = call.data.split("_")[2]
    
    # Проверяем, существует ли курс с таким ID
    if course_id not in courses:
        bot.answer_callback_query(call.id, "Курс не найден. Попробуйте выбрать другой.")
        return
        
    course_name = courses[course_id]["name"]
    
    # Проверяем, есть ли номер телефона пользователя
    if user_id not in user_states or "phone" not in user_states[user_id]:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = telebot.types.KeyboardButton(text="📱 Отправьте свой номер телефона", request_contact=True)
        keyboard.add(button_phone)
        
        bot.send_message(
            call.message.chat.id, 
            "⚠️ Пожалуйста, отправьте свой номер телефона чтобы продолжить:",
            reply_markup=keyboard
        )
        return
    
    try:
        with open(courses[course_id]["image"], 'rb') as photo:
            bot.send_photo(
                call.message.chat.id,
                photo,
                caption=f"🎟 Тарифы курса {course_name}:"
            )
    except Exception as e:
        bot.send_message(
            call.message.chat.id,
            f"🎟 Тарифы курса {course_name}:"
        )
    
    # Отправляем список тарифов
    bot.send_message(
        call.message.chat.id,
        "Выберите подходящий тариф:",
        reply_markup=create_tariffs_keyboard(course_id)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("payment_manager_"))
def payment_manager_callback(call):
    user_id = call.from_user.id
    course_id = call.data.split("_")[2]
    
    if course_id not in courses:
        bot.answer_callback_query(call.id, "Курс не найден. Попробуйте выбрать другой.")
        return
        
    if user_id not in user_states or "phone" not in user_states[user_id]:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = telebot.types.KeyboardButton(text="📱 Отправьте свой номер телефона", request_contact=True)
        keyboard.add(button_phone)
        
        bot.send_message(
            call.message.chat.id, 
            "⚠️ Пожалуйста, отправьте свой номер телефона чтобы продолжить:",
            reply_markup=keyboard
        )
        return
    
    course_name = courses[course_id]["name"]
    
    bot.send_message(
        call.message.chat.id,
        f"Вы выбрали оплату через менеджера для курса «{course_name}».\n"
        f"Наш менеджер свяжется с вами в ближайшее время.\n"
        f"Если у вас есть вопросы, вы можете связаться с ним напрямую: {manager_username}"
    )
    
    # Добавляем кнопку для возврата к выбору курсов
    back_keyboard = InlineKeyboardMarkup(row_width=1)
    back_keyboard.add(InlineKeyboardButton("◀️ Назад к курсам", callback_data="back_to_courses"))
    
    bot.send_message(
        call.message.chat.id,
        "Спасибо за интерес к нашему курсу!",
        reply_markup=back_keyboard
    )
    
    # Создаем сделку в Битрикс с дефолтным тарифом (или без тарифа)
    create_bitrix_deal(user_id, course_id, None, "Через менеджера")

@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff_"))
def tariff_callback(call):
    user_id = call.from_user.id
    _, course_id, tariff_id = call.data.split("_")
    
    if course_id not in courses or tariff_id not in courses[course_id]["tariffs"]:
        bot.answer_callback_query(call.id, "Тариф не найден. Попробуйте выбрать другой.")
        return
    
    course_name = courses[course_id]["name"]
    tariff_info = courses[course_id]["tariffs"][tariff_id]

    # Проверяем, есть ли номер телефона пользователя
    if user_id not in user_states or "phone" not in user_states[user_id]:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = telebot.types.KeyboardButton(text="📱 Отправьте свой номер телефона", request_contact=True)
        keyboard.add(button_phone)
        
        bot.send_message(
            call.message.chat.id, 
            "⚠️ Пожалуйста, отправьте свой номер телефона чтобы продолжить:",
            reply_markup=keyboard
        )
        return
    
    user_states[user_id]["selected_tariff"] = tariff_id
    
    bot.send_message(
        call.message.chat.id,
        f"🎓 Тариф: {tariff_info['name']}\n💰 Стоимость: {tariff_info['price']} руб.\n\n"
        f"{tariff_info['info']}\n\nДля оплаты перейдите по ссылке ниже."
    )
    
    # Создаем клавиатуру только с кнопкой оплаты
    payment_keyboard = InlineKeyboardMarkup(row_width=1)
    payment_keyboard.add(
        InlineKeyboardButton("💳 Оплатить онлайн", url=tariff_info["link"]),
        InlineKeyboardButton("◀️ Назад к курсам", callback_data="back_to_courses")
    )
    
    bot.send_message(
        call.message.chat.id,
        "↘️🔽🔽🔽🔽🔽🔽↙️",
        reply_markup=payment_keyboard
    )
    
    # Создаем сделку в Битрикс
    create_bitrix_deal(user_id, course_id, tariff_id, "Онлайн")

def create_bitrix_deal(user_id, course_id, tariff_id, payment_method):
    if user_id not in user_states or "phone" not in user_states[user_id]:
        return
        
    course_name = courses[course_id]["name"]
    
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
        
        # Формируем имя пользователя
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

        # Формируем данные для сделки
        deal_data = {
            "fields": {
                BITRIX_FIELDS["title"]: f"🛒 Покупка курса - {course_name}",
                BITRIX_FIELDS["type"]: "GOODS",
                BITRIX_FIELDS["stage"]: "NEW",
                BITRIX_FIELDS["price"]: tariff_price,
                "CONTACT_ID": contact_id,
                BITRIX_FIELDS["course"]: course_name,
                BITRIX_FIELDS["tariff_name"]: tariff_name,
                BITRIX_FIELDS["referral"]: referrer if referrer else "Нет реферера",
                BITRIX_FIELDS.get("payment_method", "UF_CRM_PAYMENT_METHOD"): payment_method
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
            f"❌ Ошибка связи с сервером. Попробуйте позже. Обратитесь к поддержке: {manager_username}"
        )
    except Exception as e:
        bot.send_message(
            user_id, 
            f"⚠️ Произошла ошибка. Обратитесь к поддержке: {manager_username}"
        )

if __name__ == "__main__":
    bot.polling(none_stop=True)