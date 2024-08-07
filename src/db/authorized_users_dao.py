from src.db.database_manager import db_manager


def save_user(trader_id, user_id, phone_number):
    db_manager.execute_query(
        "INSERT INTO authorized_users (trader_id, phone_number, user_id) VALUES (%s, %s, %s) ON CONFLICT (phone_number) DO NOTHING", (trader_id, phone_number, user_id)
    )


def mark_as_authenticated(phone_number):
    db_manager.execute_query(
        "UPDATE authorized_users SET is_authenticated = TRUE WHERE phone_number = %s", (phone_number, )
    )


def mark_as_not_authenticated(phone_number):
    db_manager.execute_query(
        "UPDATE authorized_users SET is_authenticated = FALSE WHERE phone_number = %s", (phone_number, )
    )


def get_trader_id_by_user_id(user_id):
    return db_manager.execute_query(
        "SELECT trader_id FROM authorized_users WHERE user_id = %s", user_id
    )


def get_trader_id_by_phone(phone_number):
    result = db_manager.execute_query(
        "SELECT trader_id FROM authorized_users WHERE phone_number = %s", (phone_number, )
    )
    if result:
        return result[0][0]
    return None


def get_authenticated_phone_numbers():
    return db_manager.execute_query(
        "SELECT phone_number FROM authorized_users WHERE is_authenticated = TRUE"
    )