import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from config import TOKEN, BITRIX_WEBHOOK_URL, manager_username, BITRIX_FIELDS ,courses

bot = telebot.TeleBot(TOKEN)

user_states = {}


def create_courses_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for course_id, course_info in courses.items():
        row = [
            InlineKeyboardButton(course_info["name"], callback_data=f"course_{course_id}"),
            InlineKeyboardButton("ИНФО", callback_data=f"info_{course_id}")
        ]
        keyboard.add(*row)
    return keyboard

def create_tariffs_keyboard(course_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for tariff_id, tariff_info in courses[course_id]["tariffs"].items():
        button_text = f"{tariff_info['name']} - {tariff_info['price']} руб 💰"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"tariff_{course_id}_{tariff_id}"))
    keyboard.add(InlineKeyboardButton("◀️ Назад к курсам", callback_data="back_to_courses"))
    return keyboard

@bot.message_handler(commands=["start"])
def start_handler(message):
    referrer = message.text.split(" ")[-1] if " " in message.text else None
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = telebot.types.KeyboardButton(text="📱 Отправьте свой номер телефона", request_contact=True)
    keyboard.add(button_phone)

    user_states[message.from_user.id] = {"referrer": referrer}
    bot.send_message(
        message.chat.id,
        "👋 Привет! Мы предлагаем курсы по работе на маркетплейсах. Пожалуйста, отправьте свой номер телефона чтобы продолжить:",
        reply_markup=keyboard
    )

@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    user_id = message.from_user.id
    phone = message.contact.phone_number.replace(" ", "")
    if not phone.startswith("+"):
        phone = f"+{phone}"
    user_states[user_id]["phone"] = phone

    # Переключаемся на inline клавиатуру для выбора курса
    bot.send_message(
        message.chat.id,
        "📚 Пожалуйста, выберите интересующий вас курс:",
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
    course_name = courses[course_id]["name"]
    user_states[user_id]["selected_course"] = course_id

    # Сразу показываем тарифы курса
    # Сначала отправляем изображение курса
    try:
        with open(courses[course_id]["image"], 'rb') as photo:
            bot.send_photo(
                call.message.chat.id,
                photo,
                caption=f"🎟 Тарифы курса {course_name}:"
            )
    except Exception as e:
        # Если изображение недоступно, просто отправляем текст
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

@bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
def course_info_callback(call):
    course_id = call.data.split("_")[1]
    course_name = courses[course_id]["name"]
    
    # Информация о курсе в зависимости от выбранного курса
    course_info_text = {
        "course1": f"ℹ️ Информация о курсе '{course_name}':\n\n"
                  f"Wildberries - крупнейший маркетплейс в России. Наш курс поможет вам:\n"
                  f"• Создать и оптимизировать карточки товаров\n"
                  f"• Настроить рекламные кампании\n"
                  f"• Увеличить продажи и доходность\n"
                  f"• Выстроить логистическую цепочку",
        "course2": f"ℹ️ Информация о курсе '{course_name}':\n\n"
                  f"Ozon - один из лидирующих маркетплейсов. В нашем курсе:\n"
                  f"• Секреты эффективного продвижения на Ozon\n"
                  f"• Работа с отзывами и рейтингами\n"
                  f"• Аналитика продаж и конкурентов\n"
                  f"• Масштабирование бизнеса на площадке",
        "course3": f"ℹ️ Информация о курсе '{course_name}':\n\n"
                  f"Avito - популярная платформа объявлений. Вы узнаете:\n"
                  f"• Стратегии создания привлекательных объявлений\n"
                  f"• Методы повышения конверсии\n"
                  f"• Особенности продаж различных категорий товаров\n"
                  f"• Инструменты автоматизации работы"
    }
    
    # Создаем клавиатуру с кнопкой назад
    back_keyboard = InlineKeyboardMarkup()
    back_keyboard.add(InlineKeyboardButton("◀️ Назад к курсам", callback_data="back_to_courses"))
    
    # Отправляем информацию о курсе с кнопкой назад
    bot.edit_message_text(
        course_info_text[course_id],
        call.message.chat.id,
        call.message.message_id,
        reply_markup=back_keyboard
    )
@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff_"))
def tariff_callback(call):
    user_id = call.from_user.id
    _, course_id, tariff_id = call.data.split("_")
    course_name = courses[course_id]["name"]
    tariff_info = courses[course_id]["tariffs"][tariff_id]

    if "phone" not in user_states[user_id]:
        bot.send_message(user_id, "⚠️ Пожалуйста, введите номер телефона!")
        return
    
    # Сохраняем выбранный тариф
    user_states[user_id]["selected_tariff"] = tariff_id
    
    bot.send_message(
        call.message.chat.id,
        f"🎓 Тариф: {tariff_info['name']}\n💰 Стоимость: {tariff_info['price']} руб.\n\nДля оплаты перейдите по ссылке или обратитесь к менеджеру."
    )
    
    # Создаем клавиатуру с кнопками оплаты
    payment_keyboard = InlineKeyboardMarkup(row_width=2)
    payment_keyboard.add(
        InlineKeyboardButton("💳 Оплатить онлайн", url=tariff_info["link"]),
        InlineKeyboardButton("👨‍💼 Связаться с менеджером", url=f"https://t.me/{manager_username.replace('@', '')}")
    )
    
    bot.send_message(
        call.message.chat.id,
        "Выберите способ оплаты:",
        reply_markup=payment_keyboard
    )
    
    # Создаем сделку в Битрикс
    try:
        referrer = user_states[user_id].get("referrer")
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
                        "NAME": f"User {user_id}",
                        "PHONE": [{"VALUE": user_states[user_id]["phone"], "VALUE_TYPE": "WORK"}],
                    }
                }, 
                timeout=10
            )
            contact_create.raise_for_status()
            contact_id = contact_create.json().get("result")

        deal_data = {
            "fields": {
                BITRIX_FIELDS["title"]: f"🛒 Покупка курса - {course_name}",
                BITRIX_FIELDS["type"]: "GOODS",
                BITRIX_FIELDS["stage"]: "NEW",
                BITRIX_FIELDS["price"]: int(tariff_info["price"]),
                "CONTACT_ID": contact_id,
                BITRIX_FIELDS["course"]: course_name,
                BITRIX_FIELDS["tariff_name"]: tariff_info["name"],
                BITRIX_FIELDS["referral"]: referrer if referrer else "Нет реферера"
            }
        }

        response = requests.post(
            f"{BITRIX_WEBHOOK_URL}/crm.deal.add", 
            json=deal_data, 
            timeout=10
        )
        response.raise_for_status()
    except requests.RequestException:
        bot.send_message(
            user_id, 
            f"❌ Ошибка связи с CRM. Попробуйте позже. 😞 Обратитесь к поддержке: {manager_username}"
        )
    except Exception as e:
        bot.send_message(
            user_id, 
            f"⚠️ Произошла ошибка. Обратитесь к поддержке: {manager_username}"
        )

if __name__ == "__main__":
    bot.polling(none_stop=True)