import ast

from src.db.database_manager import db_manager


def save_keywords(user_id, keywords):
    print("Saving keywords: ", keywords)
    keywords_string = ', '.join(keywords)
    db_manager.execute_query(
        "INSERT INTO config (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
        (user_id, keywords_string)
    )


def get_user_words(user_id):
    result = db_manager.execute_query(
        "SELECT value FROM config WHERE key = %s", (str(user_id), )
    )
    if result:
        keywords = result[0][0].split(', ')
        return keywords
    return []