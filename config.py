
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# Токен Telegram бота
TOKEN = '7874300047:AAH4esOCS-fjUVxVxb_WRg9Za60PnvFcCXo'

# URL вебхука Битрикс24
BITRIX_WEBHOOK_URL = "https://b24-7jrcyg.bitrix24.ru/rest/1/at06gb8ol8h2h6a1/"

# Имя пользователя менеджера (для контакта с клиентами)
manager_username = "@Bobo_76"

# Сопоставление полей в Битрикс24
BITRIX_FIELDS = {
    "title": "TITLE",
    "type": "TYPE_ID",
    "stage": "STAGE_ID",
    "price": "OPPORTUNITY",
    "phone": "UF_CRM_1739701799",
    "course": "UF_CRM_1739701903",
    "tariff_name": "UF_CRM_1739701953",
    "referral": "UF_CRM_1740017868"
}
courses = {
    "course1": {
        "name": "Wildberries",
        "image": os.path.join(BASE_DIR, "images", "wildberis.jpg"), 
        "tariffs": {
            "tariff1": {
                "name": "ВБ Менеджер", 
                "price": 24900,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_7m2q3/"
            },
            "tariff2": {
                "name": "ВБ Вип", 
                "price": 49900,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_iuvev/"
            },
            "tariff3": {
                "name": "ВБ Наставничество", 
                "price": 84900,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_ajfvs/"
            },
            "tariff4": {
                "name": "ВБ Офлайн", 
                "price": 115000,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_wcuqu/"
            }
        }
    },
    "course2": {
        "name": "OZON",
        "image": os.path.join(BASE_DIR, "images", "ozon.jpg"),
        "tariffs": {
            "tariff1": {
                "name": "Озон Менеджер", 
                "price": 20000,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_vwygw/"
            },
            "tariff2": {
                "name": "Озон Вип", 
                "price": 34900,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_aq0vp/"
            },
            "tariff3": {
                "name": "Озон Наставничество", 
                "price": 74900,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_vj9gy/"
            },
            "tariff4": {
                "name": "Озон Офлайн", 
                "price": 94900,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_gcrim/"
            }
        }
    },
    "course3": {
        "name": "AVITO",
        "image": os.path.join(BASE_DIR, "images", "avito.jpg"),
        "tariffs": {
            "tariff1": {
                "name": "Авито Стандарт", 
                "price": 20000,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_tdvv4/"
            },
            "tariff2": {
                "name": "Авито Премиум", 
                "price": 30000,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_kavrj/"
            },
            "tariff3": {
                "name": "Авито Наставничество", 
                "price": 64900,
                "link": "https://b24-c4qbje.bitrix24site.ru/crm_form_sdeyk/"
            }
        }
    }
}
# Примечание: Курсы и тарифы теперь определены в файле основного кода бота
# для более простого управления связями между курсами и соответствующими тарифами
    # Информация о курсе в зависимости от выбранного курса
