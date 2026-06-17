# sherlock_ban_bot.py
# Telegram Bot version for @Gothbreach

import asyncio
import random
import os
import glob
import io
from datetime import datetime
from typing import List, Optional
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

# Telethon imports
from telethon import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonOther,
    InputReportReasonIllegalDrugs,
    InputReportReasonPersonalDetails,
)
from telethon.errors import FloodWaitError, RPCError, UserDeactivatedError, AuthKeyDuplicatedError

# --- Константы ---
BOT_TOKEN = "8796050973:AAFt5rayNVvFIqe1mMM6PfIJtVj0rx1o1bE"
SESSIONS_DIR = './session'

# ТВОИ API ДАННЫЕ
API_ID = 33728218
API_HASH = "2c416c3a6e867f9c67169a6c8506990b"

COMPLAINT_CATEGORIES = {
    'personal_data': {
        'reasons': [InputReportReasonPersonalDetails(), InputReportReasonSpam(), InputReportReasonOther()],
        'texts': [
            "Бот публикует персональные данные граждан: ФИО, дата рождения, номера паспортов, СНИЛС, ИНН. Выдаёт адреса регистрации и фактического проживания по запросу. Это прямое нарушение статьи 137 УК РФ и Terms of Service Telegram. Требую немедленной блокировки → https://telegram.org/tos",
            "Открытый доксинг: бот сливает базы данных с ФИО, номерами телефонов, адресами проживания, паспортными данными. Создаёт угрозу безопасности граждан, возможность шантажа и мошенничества. Прошу срочно заблокировать за нарушение → https://telegram.org/tos",
            "Бот используется для деанонимизации пользователей без их согласия. Распространяет конфиденциальную информацию и частные данные. Нарушение политики конфиденциальности Telegram.",
            "Данный ресурс является инструментом для незаконного сбора и распространения ПД. В базах присутствуют данные несовершеннолетних. Срочная блокировка за нарушение прав человека.",
            "Бот нарушает GDPR и местного законодательство о защите данных, предоставляя доступ к закрытым реестрам и слитым базам. Это создает риск физической расправы над людьми.",
            "Систематический слив личной информации через этот бот нарушает базовые принципы безопасности мессенджера. Прошу принять меры.",
            "Данный бот является инструментом для киберпреследования (stalking). Он предоставляет доступ к частным фотографиям, адресам и контактам без согласия владельцев. Это прямое нарушение права на частную жизнь.",
            "Бот распространяет данные сотрудников правоохранительных органов и их семей, что создает прямую угрозу их жизни и здоровью. Требую немедленного удаления ресурса.",
            "В этом боте реализована функция поиска людей по украденным базам данных мобильных операторов и банков. Это грубое нарушение законов о защите информации и ToS Telegram.",
            "Бот предлагает услуги по взлому аккаунтов и деанонимизации анонимных пользователей. Пропаганда хакерства и нарушение безопасности мессенджера.",
            "Ресурс содержит архивы с личными переписками и интимными фотографиями, полученными незаконным путем. Распространение порнографии без согласия и нарушение частной жизни.",
            "Бот аккумулирует информацию из утекших баз данных государственных сервисов. Использование таких данных в коммерческих целях незаконно. Прошу заблокировать.",
            "Этот бот позволяет любому желающему получить доступ к истории перемещений граждан и их финансовым операциям. Это вопиющее нарушение прав граждан и безопасности.",
            "Бот используется для травли и буллинга. Он публикует домашние адреса и телефоны жертв, призывая к расправе. Срочная блокировка за призывы к насилию.",
            "Распространение данных о здоровье граждан и медицинских диагнозах через этот бот является нарушением врачебной тайны и прав человека.",
            "Бот предоставляет доступ к базам ГИБДД, позволяя отслеживать автомобили и их владельцев. Это создает условия для совершения преступлений.",
            "В боте публикуются списки 'неугодных' лиц с их полными данными и контактами. Это форма политического и социального преследования.",
            "Бот нарушает интеллектуальную собственность и права на частные данные, перепродавая информацию из закрытых корпоративных источников.",
            "Данный ресурс является части сети по торговле крадеными аккаунтами и личными профилями. Требую пресечь незаконную деятельность.",
            "Бот активно продвигает услуги 'пробива' по всем возможным базам данных, что является уголовным преступлением в большинстве стран мира.",
            "Использование этого бота ведет к массовым утечкам информации и нарушает стабильность работы экосистемы Telegram. Прошу забанить за вредоносный контент.",
            "Бот предоставляет доступ к закрытым базам данных МВД и ГИБДД, нарушая тайну частной жизни и закон о персональных данных. Требую немедленной блокировки → https://telegram.org/tos",
            "В данном боте реализована функция 'пробива' по номеру телефона, выдающая ФИО, адрес и паспортные данные владельца без его согласия. Нарушение ToS → https://telegram.org/tos",
            "Ресурс распространяет списки с личными данными участников протестных акций, включая их домашние адреса и контакты родственников. Это прямая угроза безопасности → https://telegram.org/tos",
            "Бот аккумулирует информацию из утекших баз банковских клиентов, позволяя мошенникам получать доступ к финансовым сведениям граждан. Срочная блокировка → https://telegram.org/tos",
            "Этот сервис используется для деанонимизации владельцев анонимных Telegram-каналов, что нарушает принципы конфиденциальности мессенджера. Требую принять меры → https://telegram.org/tos",
            "Бот публикует интимные фотографии и видео, украденные из личных облачных хранилищ, вместе с полными данными жертв. Грубое нарушение этики и закона → https://telegram.org/tos",
            "Через этот бот ведется торговля логинами и паролями от государственных сервисов, обеспечивающих доступ к ПД миллионов граждан. Нарушение безопасности → https://telegram.org/tos",
            "Бот предлагает услуги по отслеживанию геолокации пользователей в реальном времени через уязвимости в сетях связи. Это незаконная слежка → https://telegram.org/tos",
            "Данный ресурс является агрегатором слитых баз данных из сервисов доставки еды и такси, раскрывая историю перемещений и адреса граждан. Блокируйте → https://telegram.org/tos",
            "Бот содержит базу данных медицинских карт с диагнозами и результатами анализов, что является грубейшим нарушением врачебной тайны. Требую удаления → https://telegram.org/tos",
            "Этот инструмент позволяет находить профили в социальных сетях по фотографии лица (face recognition) без согласия субъектов. Нарушение приватности → https://telegram.org/tos",
            "Бот используется для организации массовой травли: публикует контакты 'жертв' и призывает к совершению противоправных действий в их отношении. Срочно в бан → https://telegram.org/tos",
            "В боте размещены инструменты для автоматизированного сбора (парсинга) личной информации из профилей пользователей Telegram в обход настроек приватности. Нарушение ToS → https://telegram.org/tos",
            "Этот сервис продает выписки из реестров недвижимости с указанием всех собственников и их паспортных данных, что способствует совершению краж. Требую блок → https://telegram.org/tos",
            "Бот функционирует как 'черный список' работодателей или сотрудников с публикацией их конфиденциальных данных и необоснованными обвинениями. Клевета и доксинг → https://telegram.org/tos",
            "Через данный интерфейс злоумышленники получают доступ к базам данных страховых компаний, включая сведения о застрахованном имуществе и доходах. Срочная блокировка → https://telegram.org/tos",
            "Бот предлагает услуги по 'восстановлению' сим-карт и получению доступа к СМС-кодам подтверждения, что ведет к краже личных аккаунтов. Нарушение безопасности → https://telegram.org/tos",
            "Ресурс содержит базу данных избирателей с указанием адресов и политических предпочтений, что является незаконным использованием персональной информации. Блокируйте → https://telegram.org/tos",
        ]
    },
    'gambling': {
        'reasons': [InputReportReasonSpam(), InputReportReasonOther()],
        'texts': [
            "Бот рекламирует незаконные онлайн-казино и букмекерские конторы без лицензии ФНС РФ. Предлагает ставки на спорт и азартные игры с выводом реальных денег. Нарушение статьи 171.2 УК РФ и ToS Telegram → https://telegram.org/tos",
            "Организация азартных игр в обход законодательства. Бот вовлекает несовершеннолетних в лудоманию через агрессивную рекламу и бонусы. Прошу заблокировать → https://telegram.org/tos",
            "Бот является витриной для нелегальных игровых площадок. Мошеннические схемы с выводом средств и обман игроков. Нарушение правил Telegram → https://telegram.org/tos",
            "Пропаганда гемблинга и незаконных финансовых операций. Бот использует фишинговые методы для привлечения депозитов. Срочная блокировка → https://telegram.org/tos",
            "Данный бот функционирует как нелегальное казино, принимая платежи через серые схемы. Это прямое нарушение финансового законодательства и правил мессенджера → https://telegram.org/tos",
            "Бот распространяет ссылки на зеркала запрещенных казино, обходя блокировки Роскомнадзора. Содействует незаконной игорной деятельности → https://telegram.org/tos",
            "В боте реализована система азартных игр на криптовалюту без какой-либо верификации возраста. Это способствует развитию игровой зависимости у детей → https://telegram.org/tos",
            "Этот ресурс используется для отмывания денег через фиктивные ставки и игровые счета. Нарушение политики противодействия легализации доходов → https://telegram.org/tos",
            "Бот обманывает пользователей, обещая 'беспроигрышные схемы' в казино, что является формой мошенничества и гемблинга одновременно → https://telegram.org/tos",
            "Реклама нелегальных слотов и игровых автоматов через этот бот нарушает закон о рекламе и внутренние правила Telegram → https://telegram.org/tos",
            "Бот предоставляет доступ к платформе для ставок на исходы событий, не имея на то законных оснований и лицензий. Требую блокировки → https://telegram.org/tos",
            "Через данный интерфейс организован тотализатор, работающий вне правового поля. Риск потери средств пользователями без возможности защиты прав → https://telegram.org/tos",
            "Бот активно спамит предложениями 'быстрого заработка' на азартных играх, вовлекая уязвимые слои населения в долги → https://telegram.org/tos",
            "Этот сервис является частью сети по организации подпольных онлайн-казино. Грубое нарушение ToS Telegram в части запрещенного контента → https://telegram.org/tos",
            "Бот предлагает участие в нелегальных лотереях и розыгрышах, что является нарушением законодательства о лотерейной деятельности → https://telegram.org/tos",
            "В боте отсутствуют механизмы ответственной игры, он нацелен на максимальное выкачивание денег из пользователей через азарт → https://telegram.org/tos",
            "Бот использует психологические манипуляции для удержания игроков в нелегальном казино. Прошу принять меры по ограничению доступа → https://telegram.org/tos",
            "Данный ресурс нарушает запрет на организацию и проведение азартных игр с использованием информационно-телекоммуникационных сетей → https://telegram.org/tos",
            "Бот рекламирует скриптовые (поддельные) казино, где результат игры заранее предопределен в пользу владельца. Мошенничество в чистом виде → https://telegram.org/tos",
            "Этот бот — точка входа в экосистему нелегального гемблинга, которая не контролируется регуляторами и нарушает правила платформы → https://telegram.org/tos",
        ]
    },
    'drugs': {
        'reasons': [InputReportReasonIllegalDrugs(), InputReportReasonOther()],
        'texts': [
            "Бот занимается продажей и распространением наркотических средств. Публикует прайс-листы, районы закладок и контакты курьеров. Пропаганда и сбыт запрещенных веществ. Требую блокировки → https://telegram.org/tos",
            "Автоматизированная витрина по продаже ПАВ (психоактивных веществ). Бот предоставляет координаты тайников после оплаты. Смертельная угроза для общества. Блокируйте немедленно → https://telegram.org/tos",
            "Бот рекламирует даркнет-площадки по торговле наркотиками. Инструкции по употреблению и изготовлению запрещенных веществ. Нарушение всех норм безопасности → https://telegram.org/tos",
            "Данный ресурс используется для вербовки курьеров-закладчиков и сбыта наркотиков оптом и в розницу. Преступная деятельность в мессенджере → https://telegram.org/tos",
            "Бот функционирует как автоматизированный магазин по продаже синтетических наркотиков и солей. Это прямое нарушение статьи 228.1 УК РФ → https://telegram.org/tos",
            "В боте размещены предложения о покупке марихуаны, гашиша и других наркотических средств. Пропаганда наркопотребления среди молодежи → https://telegram.org/tos",
            "Этот сервис предоставляет услуги по 'безопасному' приобретению запрещенных препаратов через систему тайников-закладок. Угроза жизни граждан → https://telegram.org/tos",
            "Бот является частью организованной преступной группы по сбыту наркотиков через интернет. Требую немедленного пресечения деятельности → https://telegram.org/tos",
            "Через данный бот распространяются рецептурные препараты с наркотическим эффектом без медицинских показаний. Нарушение аптечного законодательства → https://telegram.org/tos",
            "Бот содержит ссылки на чаты и каналы, где ведется открытая торговля ПАВ и обсуждаются способы обхода закона. Срочная блокировка → https://telegram.org/tos",
            "Ресурс предлагает работу 'курьером' с высокой оплатой, что является вербовкой в наркобизнес. Вовлечение людей в тяжкие преступления → https://telegram.org/tos",
            "Бот предоставляет доступ к каталогу наркотических средств with фотографиями и описанием эффектов. Грубое нарушение правил Telegram → https://telegram.org/tos",
            "Этот инструмент используется для приема оплаты за наркотики через анонимные платежные системы и криптовалюты. Финансирование наркоторговли → https://telegram.org/tos",
            "Бот рекламирует 'дизайнерские наркотики', которые несут непредсказуемую угрозу здоровью. Прошу заблокировать за опасный контент → https://telegram.org/tos",
            "Данный бот — это полноценный маркетплейс запрещенных веществ с системой отзывов и рейтингов. Преступная деятельность в открытом доступе → https://telegram.org/tos",
            "Бот распространяет информацию о местах хранения оптовых партий наркотиков для последующей розничной продажи. Угроза национальной безопасности → https://telegram.org/tos",
            "В боте реализована функция поиска ближайших 'закладок' по геолокации пользователя. Это вопиющее нарушение закона и правил мессенджера → https://telegram.org/tos",
            "Бот используется для координации действий наркодилеров и обмена информацией о поставках запрещенных грузов. Требую блокировки → https://telegram.org/tos",
            "Этот ресурс пропагандирует культуру употребления наркотиков и предоставляет инструкции по их самостоятельному изготовлению. Опасно для жизни → https://telegram.org/tos",
            "Бот является витриной магазина, торгующего смертью. Каждый час его работы увеличивает количество жертв наркомании. Срочно в бан → https://telegram.org/tos",
        ]
    }
}

# --- Работа с сессиями Telethon ---

async def get_telethon_client(
    session_path: str,
    api_id: int,
    api_hash: str,
) -> Optional[TelegramClient]:
    """Создаёт Telethon Client из существующего .session файла."""
    client = TelegramClient(session_path, api_id, api_hash)
    try:
        await client.connect()
        if await client.is_user_authorized():
            return client
        else:
            await client.disconnect()
            return None
    except Exception:
        try: await client.disconnect()
        except: pass
        return None

async def load_all_sessions(api_id: int, api_hash: str) -> List[TelegramClient]:
    """Загружает все .session файлы из папки SESSIONS_DIR"""
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    session_files = glob.glob(os.path.join(SESSIONS_DIR, "*.session"))
    
    if not session_files:
        return []

    tasks = [get_telethon_client(f, api_id, api_hash) for f in session_files]
    results = await asyncio.gather(*tasks)
    return [c for c in results if c is not None]

# --- Воркер жалоб ---

async def attack_worker(client: TelegramClient, target_username: str) -> int:
    """Один Telethon клиент отправляет жалобы на цель."""
    success_count = 0
    try:
        all_texts = []
        all_reasons = []
        for cat in COMPLAINT_CATEGORIES.values():
            all_texts.extend(cat['texts'])
            all_reasons.extend(cat['reasons'])
        
        for _ in range(3):
            try:
                reason = random.choice(all_reasons)
                message_text = random.choice(all_texts)
                await client(ReportPeerRequest(
                    peer=target_username,
                    reason=reason,
                    message=message_text
                ))
                success_count += 1
                await asyncio.sleep(0.2)
            except FloodWaitError as e:
                if e.seconds > 15: break
                await asyncio.sleep(e.seconds)
            except RPCError:
                continue
            except Exception:
                continue
    finally:
        try: await client.disconnect()
        except: pass
    return success_count

# --- Обработчики команд бота ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 *SherlockBan Bot v2 (Telegram Bot)*\n\n"
        "Команды:\n"
        "/ban @username — массовые жалобы на бота\n"
        "/ss — проверка сессий в папке ./session/\n"
        "/help — справка\n\n"
        "Сессии Telethon должны лежать в папке ./session/",
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 *SherlockBan Bot — справка*\n\n"
        "/ban @username — отправить жалобы со всех активных сессий\n"
        "/ss — проверить все .session файлы в папке ./session/\n"
        "/start — приветствие\n"
        "/help — эта справка\n\n"
        "Сессии должны быть авторизованы в Telegram.",
        parse_mode=ParseMode.MARKDOWN
    )

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Ошибка: Не указана цель!\nПример: /ban @username")
        return

    target_username = args[0].lstrip("@")
    msg = await update.message.reply_text("⚡ Загружаю сессии и отправляю жалобы...")
    
    workers = await load_all_sessions(API_ID, API_HASH)
    if not workers:
        await msg.edit_text("❌ Ошибка: Нет рабочих сессий в ./session/")
        return

    tasks = [attack_worker(worker, target_username) for worker in workers]
    results = await asyncio.gather(*tasks)
    total_reports = sum(results)
    
    output = (
        f"⚙️ *Отчет Sherlock Ban v2:*\n"
        f"├ Цель: @{target_username}\n"
        f"├ Статус: Завершено\n"
        f"├ Аккаунтов: {len(workers)}\n"
        f"├ Жалоб отправлено: {total_reports}\n"
        f"└ Тип: Массовый репорт"
    )
    await msg.edit_text(output, parse_mode=ParseMode.MARKDOWN)

async def ss_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⚡ Проверяю все сессии в папке ./session/...")
    
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    session_files = glob.glob(os.path.join(SESSIONS_DIR, "*.session"))
    
    if not session_files:
        await msg.edit_text("❌ Ошибка: Нет сессий в ./session/")
        return

    log_lines = [f"LOG: SESSION CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "="*50]
    active_count = 0
    dead_count = 0
    flood_count = 0
    
    for f in session_files:
        name = os.path.basename(f)
        client = TelegramClient(f, API_ID, API_HASH)
        status = "UNKNOWN"
        details = ""
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                status = "DEAD (Unauthorized)"
                dead_count += 1
            else:
                try:
                    me = await client.get_me()
                    status = "ACTIVE"
                    details = f"User: {me.first_name} (@{me.username or 'N/A'}) ID: {me.id}"
                    active_count += 1
                except FloodWaitError as e:
                    status = f"FLOODWAIT ({e.seconds}s)"
                    flood_count += 1
                except Exception as e:
                    status = f"ERROR: {str(e)}"
                    dead_count += 1
        except UserDeactivatedError:
            status = "DEAD (Deactivated/Banned)"
            dead_count += 1
        except AuthKeyDuplicatedError:
            status = "DEAD (Auth Key Duplicated)"
            dead_count += 1
        except Exception as e:
            status = f"CRITICAL ERROR: {str(e)}"
            dead_count += 1
        finally:
            await client.disconnect()
        
        log_lines.append(f"Session: {name}")
        log_lines.append(f"├ Status: {status}")
        if details:
            log_lines.append(f"└ Details: {details}")
        log_lines.append("-" * 30)

    summary = (
        f"\nSUMMARY:\n"
        f"├ Total: {len(session_files)}\n"
        f"├ Active: {active_count}\n"
        f"├ Flood: {flood_count}\n"
        f"└ Dead/Error: {dead_count}"
    )
    log_lines.append(summary)
    
    log_text = "\n".join(log_lines)
    
    output = (
        f"⚙️ *Результат проверки сессий:*\n"
        f"├ Всего найдено: {len(session_files)}\n"
        f"├ Рабочих: {active_count}\n"
        f"├ Флуд: {flood_count}\n"
        f"└ Мертвых: {dead_count}\n\n"
        f"📄 Подробный лог отправлен файлом ниже."
    )
    
    log_file = io.BytesIO(log_text.encode('utf-8'))
    log_file.name = f"session_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    await msg.edit_text(output, parse_mode=ParseMode.MARKDOWN)
    await update.message.reply_document(log_file, caption="📄 Подробный лог проверки сессий")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("ss", ss_command))
    
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()