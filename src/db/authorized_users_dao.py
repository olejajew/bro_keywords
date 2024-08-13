from src.db.database_manager import db_manager


def save_user(user_id, phone_number):
    db_manager.execute_query(
        "INSERT INTO authorized_users (phone_number, user_id) VALUES (%s, %s ) ON CONFLICT (phone_number) DO NOTHING", (phone_number, user_id)
    )


def mark_as_authenticated(phone_number):
    db_manager.execute_query(
        "UPDATE authorized_users SET is_authenticated = TRUE WHERE phone_number = %s", (phone_number, )
    )


def mark_as_not_authenticated(phone_number):
    db_manager.execute_query(
        "UPDATE authorized_users SET is_authenticated = FALSE WHERE phone_number = %s", (phone_number, )
    )


def get_authenticated_phone_numbers():
    return db_manager.execute_query(
        "SELECT phone_number FROM authorized_users WHERE is_authenticated = TRUE"
    )


def update_chat_id(user_id, chat_id):
    db_manager.execute_query(
        "UPDATE authorized_users SET chat_id = %s WHERE user_id = %s", (chat_id, user_id)
    )


def get_chat_id(user_id):
    result = db_manager.execute_query(
        "SELECT chat_id FROM authorized_users WHERE user_id = %s", (user_id, )
    )
    if result:
        return result[0][0]
    return None


def get_user_id_by_phone(phone):
    result = db_manager.execute_query(
        "SELECT user_id FROM authorized_users WHERE phone_number = %s", (phone, )
    )
    if result:
        return result[0][0]
    return None


def get_phone_by_user_id(user_id):
    result = db_manager.execute_query(
        "SELECT phone_number FROM authorized_users WHERE user_id = %s", (user_id, )
    )
    if result:
        return result[0][0]
    return None
