import pytest
from utils.database import get_mongo_db, is_mongo_active, get_sqlite_connection, init_db

def _clean():
    """Removes transient test data matching @opticrop.io domain."""
    if is_mongo_active():
        db = get_mongo_db()
        if db is not None:
            try:
                db.users.delete_many({'email': {'$regex': '@opticrop\\.io$'}})
                db.predictions.delete_many({'user_id': {'$regex': '^(user_|test_)'}})
                db.farm_plots.delete_many({'user_id': {'$regex': '^(user_|test_)'}})
                db.chat_history.delete_many({'user_id': {'$regex': '^(user_|test_)'}})
            except Exception:
                pass

    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email LIKE '%@opticrop.io'")
        cursor.execute("DELETE FROM predictions WHERE user_id LIKE 'user_%' OR user_id LIKE 'test_%'")
        cursor.execute("DELETE FROM farm_plots WHERE user_id LIKE 'user_%' OR user_id LIKE 'test_%'")
        cursor.execute("DELETE FROM chat_history WHERE user_id LIKE 'user_%' OR user_id LIKE 'test_%'")
        conn.commit()
        conn.close()
    except Exception:
        pass

@pytest.fixture(scope="session", autouse=True)
def session_test_cleanup():
    init_db()
    _clean()
    yield
    _clean()

@pytest.fixture(autouse=True)
def function_test_cleanup():
    yield
    _clean()
