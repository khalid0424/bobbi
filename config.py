
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# Токен Telegram бота
TOKEN = '7531821089:AAFPz7CsBZ7S_OPQTiVW7aTT25bAZ96QL00'

# URL вебхука Битрикс24
BITRIX_WEBHOOK_URL = "https://b24-kzukab.bitrix24.ru/rest/1/nh2jwi33nolk3xkx/"

# Имя пользователя менеджера (для контакта с клиентами)
manager_username = "@menej_tj"

# Сопоставление полей в Битрикс24
BITRIX_FIELDS = {
    "title": "TITLE",
    "type": "TYPE_ID",
    "stage": "STAGE_ID",
    "price": "OPPORTUNITY",
    "phone": "UF_CRM_1740629049",
    "course": "UF_CRM_1740629005",
    "tariff_name": "UF_CRM_1740628975",
    "referral": "UF_CRM_1740629032"
}

# Добавление 5 ответственных менеджеров для каждого курса с их Bitrix ID
courses = {
    "course1": {
        "name": "Wildberries",
        "image": os.path.join(BASE_DIR, "images", "wildberis.jpg"),
        "responsible_managers": [
            {"name": "Бузургхон Бобоев", "bitrix_id": "2241"},
            {"name": "Махмудов Фатхуллоходжа ", "bitrix_id": "4783"},
            {"name": "Давлатбек Ахмедов", "bitrix_id": "5043"},
            {"name": "Нуров Икбол", "bitrix_id": "5557"},
        ],
        "tariffs": {
            "tariff1": {
                "name": "Менеджер", 
                "price": 24900,
                "info": "🔹 Тариф <Менеджер>\n\n📌 После обучения сможете работать менеджером на маркетплейсах.\n📌 Возможность вести несколько магазинов и зарабатывать достойные деньги.",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_7m2q3/"
            },
            "tariff2": {
                "name": "VIP", 
                "price": 49900,
                "info": "🔹 Тариф <VIP>\n\n🔥 Идеально для тех, кто хочет запустить свой бизнес на Wildberries.\n📍 Онлайн-формат: учитесь из любой точки мира и совмещайте с работой!",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_iuvev/"
            },
            "tariff3": {
                "name": "Наставничество", 
                "price": 84900,
                "info": "🔹 Тариф <Наставничество>\n\n🎓 Проходите обучение онлайн и 2 раза в неделю приходите в офис для живого общения с наставником.\n📌 Возможность задать любые вопросы и получить персональные рекомендации.",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_ajfvs/"
            },
            "tariff4": {
                "name": "Офлайн", 
                "price": 115000,
                "info": "🔹 Тариф <Офлайн>\n\n🏢 Включает всё, что в других тарифах, но с 3 очными встречами в офисе с наставником.\n📌 От старта до запуска бизнеса под руководством опытного куратора.",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_wcuqu/"
            }
        }
    },
    "course2": {
        "name": "OZON",
        "image": os.path.join(BASE_DIR, "images", "ozon.jpg"),
        "responsible_managers": [
            {"name": "Нуралишох Сатторов ", "bitrix_id": "301"},
            {"name": "Юнус Рахимов "      , "bitrix_id": "4977"},
            {"name": "Фирдавс Розиков"    , "bitrix_id": "5289"},
            {"name": "Хусниддин Кабиров " , "bitrix_id": "1793"},
            {"name": "Фуркат Азимов"      , "bitrix_id": "5553"}
        ],
        "tariffs": {
            "tariff1": {
                "name": "Менеджер", 
                "price": 20000,
                "info": "🔹 Тариф <Менеджер>\n\n📌 После обучения сможете работать менеджером на маркетплейсах.\n📌 Возможность вести несколько магазинов и зарабатывать достойные деньги.",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_vwygw/"
            },
            "tariff2": {
                "name": "VIP", 
                "price": 34900,
                "info": "🔹 Тариф <ВИП>\n\n🔥 Идеально для тех, кто хочет запустить свой бизнес на Ozon.\n📍 Онлайн-формат: учитесь из любой точки мира и совмещайте с работой!",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_aq0vp/"
            },
            "tariff3": {
                "name": "Наставничество", 
                "price": 74900,
                "info": "🔹 Тариф <Наставничество>\n\n🎓 Проходите обучение онлайн и 2 раза в неделю приходите в офис для живого общения с наставником.\n📌 Возможность задать любые вопросы и получить персональные рекомендации.",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_vj9gy/"
            },
            "tariff4": {
                "name": "Офлайн", 
                "price": 94900,
                "info": "🔹 Тариф <Офлайн>\n\n🏢 Включает всё, что в других тарифах, но с 3 очными встречами в офисе с наставником.\n📌 От старта до запуска бизнеса под руководством опытного куратора.",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_gcrim/"
            }
        }
    },
    "course3": {
        "name": "AVITO",
        "image": os.path.join(BASE_DIR, "images", "avito.jpg"),
        "responsible_managers": [
            {"name": "Нуралишох Сатторов ", "bitrix_id": "301"},
            {"name": "Юнус Рахимов "      , "bitrix_id": "4977"},
            {"name": "Фирдавс Розиков"    , "bitrix_id": "5289"},
            {"name": "Хусниддин Кабиров " , "bitrix_id": "1793"},
            {"name": "Фуркат Азимов"      , "bitrix_id": "5553"}
        ],
        "tariffs": {
            "tariff1": {
                "name": "Стандарт", 
                "price": 20000,
                "info": "🔹 Тариф <Стандарт>\n\n📚 Обучение онлайн.\n📌 Возможность задать любые вопросы и получить персональные рекомендации.",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_tdvv4/"
            },
            "tariff2": {
                "name": "Премиум", 
                "price": 30000,
                "info": "🔹 Тариф <Премиум>\n\n🏢 Включает всё, что в тарифе <Стандарт>, но с 1 очными встречами в офисе с наставником.\n📌 От старта до запуска бизнеса под руководством опытного куратора.",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_kavrj/"
            },
            "tariff3": {
                "name": "Наставничество", 
                "price": 64900,
                "info": "🔹 Тариф <Наставничество Avito>\n\n🎓 Обучение + поддержка наставника.\n📌 Проходите онлайн-курс + 2 раза в неделю посещаете офис для живого общения.\n📌 Разбор ошибок, ответы на вопросы и индивидуальные рекомендации.\n📌 Подходит для тех, кто хочет быстро и эффективно освоить Avito.",
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_sdeyk/"
            }
        }
    }
}