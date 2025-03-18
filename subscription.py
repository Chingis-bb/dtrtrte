import sqlite3
from datetime import datetime, timedelta

def create_subscription(user_id: int):
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    test_period_end = datetime.now() + timedelta(days=7)
    cursor.execute('INSERT INTO subscriptions (user_id, status, test_period_end) VALUES (?, ?, ?)', (user_id, 'active', test_period_end))
    conn.commit()
    conn.close()

def check_subscription(user_id: int) -> bool:
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM subscriptions WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == 'active'

def cancel_subscription(user_id: int) -> bool:
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE subscriptions SET status = ? WHERE user_id = ?', ('inactive', user_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def is_test_period_active(user_id: int) -> bool:
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT test_period_end FROM subscriptions WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        test_period_end = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
        return datetime.now() < test_period_end
    return False

def get_subscription_end_date(user_id: int) -> datetime:
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT test_period_end FROM subscriptions WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
    return None

def extend_subscription(user_id: int):
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT test_period_end FROM subscriptions WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        new_end_date = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f') + timedelta(days=30)
        cursor.execute('UPDATE subscriptions SET test_period_end = ? WHERE user_id = ?', (new_end_date, user_id))
        conn.commit()
    conn.close()

def get_subscription_info(user_id: int) -> str:
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscriptions WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return f'ID: {result[0]}, Статус: {result[1]}, Дата окончания тестового периода: {result[2]}'
    return 'Подписка не найдена'
