import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from payment import create_payment
from subscription import check_subscription, cancel_subscription, create_subscription, is_test_period_active, get_subscription_end_date, extend_subscription, get_subscription_info
from marzban import create_marzban_profile, get_keys
from datetime import timedelta

SUBSCRIPTION_PAGE_TEMPLATE = 'https://your-website.com/subscription/{user_id}'

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Используйте /subscribe для подписки.')

# Функция для обработки команды /subscribe
def subscribe(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    try:
        if not check_subscription(user_id):
            create_subscription(user_id)
            create_marzban_profile(user_id)
            subscription_page = SUBSCRIPTION_PAGE_TEMPLATE.format(user_id=user_id)
            update.message.reply_text(f'Вы получили бесплатный тестовый период на 7 дней. Ваша страница подписки: {subscription_page}')
            schedule_subscription_end_notification(context.job_queue, user_id)
        else:
            payment_url = create_payment(user_id)
            update.message.reply_text(f'Перейдите по ссылке для оплаты: {payment_url}')
    except Exception as e:
        logger.error(f'Ошибка при обработке команды /subscribe: {e}')
        update.message.reply_text('Произошла ошибка при обработке вашей подписки. Пожалуйста, попробуйте позже.')

# Функция для уведомления пользователя о скором окончании подписки
def notify_subscription_end(context: CallbackContext) -> None:
    job = context.job
    context.bot.send_message(job.context, text='Ваша подписка истекает через 3 дня. Пожалуйста, продлите подписку.')

# Планирование уведомления за 3 дня до окончания подписки
def schedule_subscription_end_notification(job_queue: JobQueue, user_id: int) -> None:
    end_date = get_subscription_end_date(user_id)
    notification_date = end_date - timedelta(days=3)
    job_queue.run_once(notify_subscription_end, notification_date, context=user_id)

# Функция для обработки команды /status
def status(update: Update, context: CallbackContext) -> None:
    try:
        if check_subscription(update.message.chat_id):
            update.message.reply_text('Ваш статус подписки: активна.')
        else:
            update.message.reply_text('У вас нет активной подписки.')
    except Exception as e:
        logger.error(f'Ошибка при обработке команды /status: {e}')
        update.message.reply_text('Произошла ошибка при проверке вашего статуса подписки. Пожалуйста, попробуйте позже.')

# Функция для обработки команды /help
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Доступные команды:\n/start - Начало работы\n/subscribe - Подписка\n/status - Статус подписки\n/cancel - Отмена подписки\n/extend - Продление подписки\n/getkeys - Получить ключи\n/info - Информация о подписке')

# Функция для обработки команды /cancel
def cancel(update: Update, context: CallbackContext) -> None:
    try:
        if cancel_subscription(update.message.chat_id):
            update.message.reply_text('Ваша подписка отменена.')
        else:
            update.message.reply_text('У вас нет активной подписки.')
    except Exception as e:
        logger.error(f'Ошибка при обработке команды /cancel: {e}')
        update.message.reply_text('Произошла ошибка при отмене вашей подписки. Пожалуйста, попробуйте позже.')

# Функция для обработки команды /getkeys
def getkeys(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    try:
        if is_test_period_active(user_id):
            keys = get_keys(user_id)
            update.message.reply_text(f'Ваши ключи: {keys}')
        else:
            update.message.reply_text('Ваш тестовый период истек. Пожалуйста, оформите подписку.')
    except Exception as e:
        logger.error(f'Ошибка при обработке команды /getkeys: {e}')
        update.message.reply_text('Произошла ошибка при получении ваших ключей. Пожалуйста, попробуйте позже.')

# Функция для обработки команды /extend
def extend(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    try:
        if check_subscription(user_id):
            extend_subscription(user_id)
            update.message.reply_text('Ваша подписка продлена на 30 дней.')
        else:
            update.message.reply_text('У вас нет активной подписки.')
    except Exception as e:
        logger.error(f'Ошибка при обработке команды /extend: {e}')
        update.message.reply_text('Произошла ошибка при продлении вашей подписки. Пожалуйста, попробуйте позже.')

# Функция для обработки команды /info
def info(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    try:
        subscription_info = get_subscription_info(user_id)
        update.message.reply_text(f'Информация о подписке: {subscription_info}')
    except Exception as e:
        logger.error(f'Ошибка при обработке команды /info: {e}')
        update.message.reply_text('Произошла ошибка при получении информации о вашей подписке. Пожалуйста, попробуйте позже.')

def main() -> None:
    updater = Updater("YOUR_TOKEN")

    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(CommandHandler("getkeys", getkeys))
    dispatcher.add_handler(CommandHandler("extend", extend))
    dispatcher.add_handler(CommandHandler("info", info))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
