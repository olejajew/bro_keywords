import ast

from src.db.database_manager import db_manager


def get_keywords_from_config():
    result = db_manager.execute_query(
        "SELECT value FROM config WHERE key = 'keywords'"
    )
    if result:
        keywords = ast.literal_eval(result[0][0])
        if isinstance(keywords, list):
            return keywords
    return []


def save_keywords(keywords):
    print("Saving keywords: ", keywords)
    keywords_string = ', '.join(keywords)  # Convert list to string
    db_manager.execute_query(
        "INSERT INTO config (key, value) VALUES ('keywords', %s) ON CONFLICT (key) DO UPDATE SET value = %s", (keywords_string, keywords_string)
    )
