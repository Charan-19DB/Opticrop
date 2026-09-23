import os
import re
import csv
import secrets
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env
load_dotenv()

MONGODB_URI = os.environ.get('MONGODB_URI', '')
MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'opticrop_db')
DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'opticrop.db'))
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'prediction_history.csv')

# Global database client references
_mongo_client = None
_mongo_db = None
_use_mongo = False


def _init_mongo():
    """Initializes MongoDB client with connection pooling and checks connectivity."""
    global _mongo_client, _mongo_db, _use_mongo
    if not MONGODB_URI:
        _use_mongo = False
        return False

    try:
        import pymongo
        try:
            import dns.resolver
            # Ensure dnspython has reliable nameservers for Atlas SRV resolution on Windows
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
            dns.resolver.default_resolver = resolver
        except Exception:
            pass

        # Connection with reasonable timeouts for resilient operation
        _mongo_client = pymongo.MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=8000,
            connectTimeoutMS=8000,
            socketTimeoutMS=12000,
            maxPoolSize=50,
            retryWrites=True
        )
        # Verify connection
        _mongo_client.admin.command('ping')
        _mongo_db = _mongo_client[MONGODB_DB_NAME]
        _use_mongo = True

        # Ensure collection indexes for performance and security
        _mongo_db.users.create_index('email', unique=True)
        _mongo_db.predictions.create_index([('user_id', pymongo.ASCENDING), ('created_at', pymongo.DESCENDING)])
        _mongo_db.farm_plots.create_index([('user_id', pymongo.ASCENDING), ('plot_name', pymongo.ASCENDING)], unique=True)
        _mongo_db.chat_history.create_index([('user_id', pymongo.ASCENDING), ('session_id', pymongo.ASCENDING)])

        print("OptiCrop DB: Connected to MongoDB Atlas successfully.")
        return True
    except Exception as e:
        print(f"OptiCrop DB Notice: MongoDB connection failed ({e}). Falling back to SQLite.")
        _mongo_client = None
        _mongo_db = None
        _use_mongo = False
        return False


_initialized = False


def ensure_initialized():
    global _initialized
    if not _initialized:
        init_db()
        _initialized = True


def is_mongo_active():
    """Checks whether MongoDB is currently active."""
    global _use_mongo
    ensure_initialized()
    return _use_mongo and _mongo_db is not None


def get_mongo_db():
    """Returns active MongoDB database instance or None."""
    ensure_initialized()
    return _mongo_db


# --- SQLite Helpers ---

def get_sqlite_connection():
    import sqlite3
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _migrate_sqlite_schema(conn):
    cursor = conn.cursor()
    # Check users table columns
    cursor.execute("PRAGMA table_info(users)")
    user_cols = [r[1] for r in cursor.fetchall()]
    if user_cols:
        if 'auth_provider' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'local'")
        if 'google_id' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN google_id TEXT DEFAULT ''")
        if 'avatar_url' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT DEFAULT ''")
        if 'reset_token' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT DEFAULT ''")
        if 'reset_token_expiry' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expiry TEXT DEFAULT ''")

    # Check predictions table columns
    cursor.execute("PRAGMA table_info(predictions)")
    cols = [r[1] for r in cursor.fetchall()]
    if cols and 'user_id' not in cols:
        cursor.execute("ALTER TABLE predictions ADD COLUMN user_id TEXT DEFAULT 'guest'")

    # Check farm_plots table columns
    cursor.execute("PRAGMA table_info(farm_plots)")
    cols = [r[1] for r in cursor.fetchall()]
    if cols and 'user_id' not in cols:
        cursor.execute("ALTER TABLE farm_plots ADD COLUMN user_id TEXT DEFAULT 'guest'")

    # Check chat_history table columns
    cursor.execute("PRAGMA table_info(chat_history)")
    cols = [r[1] for r in cursor.fetchall()]
    if cols and 'user_id' not in cols:
        cursor.execute("ALTER TABLE chat_history ADD COLUMN user_id TEXT DEFAULT 'guest'")
    conn.commit()


def init_db():
    """Initializes primary database (MongoDB or SQLite fallback) and applies schemas."""
    global _initialized
    # Attempt MongoDB connection first
    _init_mongo()

    # Always ensure SQLite schema is initialized for resilience and testing
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT DEFAULT '',
            farm_name TEXT DEFAULT '',
            auth_provider TEXT DEFAULT 'local',
            google_id TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            reset_token TEXT DEFAULT '',
            reset_token_expiry TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Predictions Table (with user_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'guest',
            farm_name TEXT DEFAULT 'Plot #1',
            farmer_name TEXT DEFAULT 'User',
            N REAL NOT NULL,
            P REAL NOT NULL,
            K REAL NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            ph REAL NOT NULL,
            rainfall REAL NOT NULL,
            predicted_crop TEXT NOT NULL,
            confidence REAL DEFAULT 0.0,
            top2_crop TEXT DEFAULT '',
            top2_conf REAL DEFAULT 0.0,
            top3_crop TEXT DEFAULT '',
            top3_conf REAL DEFAULT 0.0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Saved Farm Plots Table (with user_id and compound unique constraint)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farm_plots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'guest',
            plot_name TEXT NOT NULL,
            farmer_name TEXT DEFAULT 'Farm Owner',
            N REAL NOT NULL,
            P REAL NOT NULL,
            K REAL NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            ph REAL NOT NULL,
            rainfall REAL NOT NULL,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, plot_name)
        )
    ''')

    # Chat Memory Table (with user_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'guest',
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # Apply SQLite column migrations if needed
    _migrate_sqlite_schema(conn)
    conn.close()
    _initialized = True


# --- User Authentication Functions ---

def validate_email(email):
    """Validates email format using regex."""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email.strip()))


def register_user(name, email, password, farm_name=''):
    """
    Registers a new user securely.
    - Validates inputs
    - Hashes password using PBKDF2:SHA256 with salt
    - Ensures email is strictly unique
    - Returns user dict (omitting password_hash)
    """
    name = (name or '').strip()
    email = (email or '').strip().lower()
    farm_name = (farm_name or '').strip()

    if not name:
        raise ValueError("Full name is required.")
    if not validate_email(email):
        raise ValueError("Please provide a valid email address.")
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    # Securely hash password with salt
    password_hash = generate_password_hash(password, method='pbkdf2:sha256:600000')
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    if is_mongo_active():
        import pymongo
        try:
            # Check duplicate email
            existing = _mongo_db.users.find_one({'email': email})
            if existing:
                raise ValueError("An account with this email address already exists.")

            user_doc = {
                'name': name,
                'email': email,
                'password_hash': password_hash,
                'farm_name': farm_name,
                'created_at': now_iso,
                'last_login': now_iso
            }
            res = _mongo_db.users.insert_one(user_doc)
            return {
                'id': str(res.inserted_id),
                'name': name,
                'email': email,
                'farm_name': farm_name,
                'created_at': now_iso,
                'last_login': now_iso
            }
        except pymongo.errors.DuplicateKeyError:
            raise ValueError("An account with this email address already exists.")
        except ValueError:
            raise
        except Exception as e:
            print(f"MongoDB register_user error: {e}")
            # Fall back to SQLite below if needed

    # SQLite Storage
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE LOWER(email) = ?', (email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("An account with this email address already exists.")

    cursor.execute('''
        INSERT INTO users (name, email, password_hash, farm_name, created_at, last_login)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, email, password_hash, farm_name, now_iso, now_iso))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {
        'id': str(new_id),
        'name': name,
        'email': email,
        'farm_name': farm_name,
        'created_at': now_iso,
        'last_login': now_iso
    }


def authenticate_user(email, password):
    """
    Authenticates a user with email and password.
    - Uses constant-time password verification to prevent timing attacks.
    - Updates last_login timestamp upon success.
    - Returns user dictionary or None.
    """
    email = (email or '').strip().lower()
    if not email or not password:
        return None

    now_iso = datetime.now(timezone.utc).isoformat()

    if is_mongo_active():
        try:
            user = _mongo_db.users.find_one({'email': email})
            if user and check_password_hash(user.get('password_hash', ''), password):
                _mongo_db.users.update_one({'_id': user['_id']}, {'$set': {'last_login': now_iso}})
                return {
                    'id': str(user['_id']),
                    'name': user.get('name', ''),
                    'email': user.get('email', ''),
                    'farm_name': user.get('farm_name', ''),
                    'created_at': user.get('created_at', now_iso),
                    'last_login': now_iso
                }
            return None
        except Exception as e:
            print(f"MongoDB authenticate_user error: {e}")

    # SQLite fallback
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email,))
    row = cursor.fetchone()

    if row and check_password_hash(row['password_hash'], password):
        user_id = row['id']
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (now_iso, user_id))
        conn.commit()
        user_dict = {
            'id': str(row['id']),
            'name': row['name'],
            'email': row['email'],
            'farm_name': row['farm_name'],
            'created_at': row['created_at'],
            'last_login': now_iso
        }
        conn.close()
        return user_dict

    conn.close()
    return None


def get_user_by_id(user_id):
    """Retrieves user profile information by ID (omits password hash)."""
    if not user_id:
        return None

    user_id_str = str(user_id)

    if is_mongo_active():
        try:
            from bson import ObjectId
            query = {'_id': ObjectId(user_id_str)} if ObjectId.is_valid(user_id_str) else {'_id': user_id_str}
            user = _mongo_db.users.find_one(query)
            if user:
                return {
                    'id': str(user['_id']),
                    'name': user.get('name', ''),
                    'email': user.get('email', ''),
                    'farm_name': user.get('farm_name', ''),
                    'auth_provider': user.get('auth_provider', 'local'),
                    'google_id': user.get('google_id', ''),
                    'avatar_url': user.get('avatar_url', ''),
                    'created_at': user.get('created_at', ''),
                    'last_login': user.get('last_login', '')
                }
        except Exception as e:
            print(f"MongoDB get_user_by_id error: {e}")

    # SQLite
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, farm_name, auth_provider, google_id, avatar_url, created_at, last_login 
            FROM users WHERE id = ?
        ''', (user_id_str,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception:
        pass

    return None


def get_user_by_email(email):
    """Retrieves user profile information by email address."""
    email = (email or '').strip().lower()
    if not email:
        return None

    if is_mongo_active():
        try:
            user = _mongo_db.users.find_one({'email': email})
            if user:
                return {
                    'id': str(user['_id']),
                    'name': user.get('name', ''),
                    'email': user.get('email', ''),
                    'farm_name': user.get('farm_name', ''),
                    'auth_provider': user.get('auth_provider', 'local'),
                    'google_id': user.get('google_id', ''),
                    'avatar_url': user.get('avatar_url', ''),
                    'created_at': user.get('created_at', ''),
                    'last_login': user.get('last_login', '')
                }
        except Exception as e:
            print(f"MongoDB get_user_by_email error: {e}")

    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, farm_name, auth_provider, google_id, avatar_url, created_at, last_login 
            FROM users WHERE LOWER(email) = ?
        ''', (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception:
        pass

    return None


def get_or_create_google_user(email, name, google_id, avatar_url=''):
    """
    Authenticates or creates a user via Google OAuth.
    If the email already exists, links the Google ID and avatar, and updates last_login.
    If new, creates the user account with auth_provider='google'.
    Returns the user profile dict.
    """
    email = (email or '').strip().lower()
    name = (name or '').strip() or email.split('@')[0].capitalize()
    google_id = str(google_id or '').strip()
    now_iso = datetime.now(timezone.utc).isoformat()

    if not email:
        raise ValueError("Valid email from Google account is required.")

    if is_mongo_active():
        try:
            user = _mongo_db.users.find_one({'$or': [{'email': email}, {'google_id': google_id}]})
            if user:
                update_fields = {
                    'last_login': now_iso,
                    'auth_provider': 'google',
                    'google_id': google_id
                }
                if avatar_url:
                    update_fields['avatar_url'] = avatar_url
                if not user.get('name') and name:
                    update_fields['name'] = name
                _mongo_db.users.update_one({'_id': user['_id']}, {'$set': update_fields})
                return {
                    'id': str(user['_id']),
                    'name': user.get('name', name),
                    'email': user.get('email', email),
                    'farm_name': user.get('farm_name', ''),
                    'auth_provider': 'google',
                    'google_id': google_id,
                    'avatar_url': avatar_url or user.get('avatar_url', ''),
                    'created_at': user.get('created_at', now_iso),
                    'last_login': now_iso
                }
            else:
                user_doc = {
                    'name': name,
                    'email': email,
                    'password_hash': '',
                    'farm_name': 'My Farm',
                    'auth_provider': 'google',
                    'google_id': google_id,
                    'avatar_url': avatar_url,
                    'created_at': now_iso,
                    'last_login': now_iso
                }
                res = _mongo_db.users.insert_one(user_doc)
                return {
                    'id': str(res.inserted_id),
                    'name': name,
                    'email': email,
                    'farm_name': 'My Farm',
                    'auth_provider': 'google',
                    'google_id': google_id,
                    'avatar_url': avatar_url,
                    'created_at': now_iso,
                    'last_login': now_iso
                }
        except Exception as e:
            print(f"MongoDB get_or_create_google_user error: {e}")

    # SQLite
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE LOWER(email) = ? OR (google_id != "" AND google_id = ?)', (email, google_id))
    row = cursor.fetchone()

    if row:
        user_id = row['id']
        cursor.execute('''
            UPDATE users SET 
                last_login = ?, 
                auth_provider = 'google', 
                google_id = ?, 
                avatar_url = CASE WHEN ? != '' THEN ? ELSE avatar_url END
            WHERE id = ?
        ''', (now_iso, google_id, avatar_url, avatar_url, user_id))
        conn.commit()
        user_dict = {
            'id': str(row['id']),
            'name': row['name'] or name,
            'email': row['email'],
            'farm_name': row['farm_name'],
            'auth_provider': 'google',
            'google_id': google_id,
            'avatar_url': avatar_url or (row['avatar_url'] if 'avatar_url' in row.keys() else avatar_url),
            'created_at': row['created_at'],
            'last_login': now_iso
        }
        conn.close()
        return user_dict
    else:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, farm_name, auth_provider, google_id, avatar_url, created_at, last_login)
            VALUES (?, ?, '', 'My Farm', 'google', ?, ?, ?, ?)
        ''', (name, email, google_id, avatar_url, now_iso, now_iso))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return {
            'id': str(new_id),
            'name': name,
            'email': email,
            'farm_name': 'My Farm',
            'auth_provider': 'google',
            'google_id': google_id,
            'avatar_url': avatar_url,
            'created_at': now_iso,
            'last_login': now_iso
        }


def generate_password_reset_token(email):
    """
    Generates a secure password reset token with 1-hour expiration.
    Returns (token, user_dict) or (None, None) if user does not exist.
    """
    email = (email or '').strip().lower()
    if not email:
        return None, None

    token = secrets.token_urlsafe(32)
    expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    if is_mongo_active():
        try:
            user = _mongo_db.users.find_one({'email': email})
            if user:
                _mongo_db.users.update_one(
                    {'_id': user['_id']},
                    {'$set': {'reset_token': token, 'reset_token_expiry': expiry}}
                )
                return token, {
                    'id': str(user['_id']),
                    'name': user.get('name', ''),
                    'email': user.get('email', '')
                }
            return None, None
        except Exception as e:
            print(f"MongoDB generate_password_reset_token error: {e}")

    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM users WHERE LOWER(email) = ?', (email,))
    row = cursor.fetchone()
    if row:
        cursor.execute('UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE id = ?', (token, expiry, row['id']))
        conn.commit()
        user_info = dict(row)
        user_info['id'] = str(user_info['id'])
        conn.close()
        return token, user_info

    conn.close()
    return None, None


def verify_and_reset_password(token, new_password):
    """
    Verifies reset token validity and expiration, sets new password hash, and clears token.
    Returns (success: bool, message: str).
    """
    token = (token or '').strip()
    if not token or not new_password or len(new_password) < 6:
        return False, "Password must be at least 6 characters long."

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    new_hash = generate_password_hash(new_password, method='pbkdf2:sha256:600000')

    if is_mongo_active():
        try:
            user = _mongo_db.users.find_one({'reset_token': token})
            if user:
                expiry_str = user.get('reset_token_expiry', '')
                if expiry_str:
                    try:
                        expiry_dt = datetime.fromisoformat(expiry_str)
                        if now > expiry_dt:
                            return False, "Password reset link has expired. Please request a new one."
                    except Exception:
                        pass
                _mongo_db.users.update_one(
                    {'_id': user['_id']},
                    {'$set': {
                        'password_hash': new_hash,
                        'reset_token': '',
                        'reset_token_expiry': '',
                        'last_login': now_iso
                    }}
                )
                return True, "Password reset successfully. You can now log in with your new password."
            return False, "Invalid or already used password reset link."
        except Exception as e:
            print(f"MongoDB verify_and_reset_password error: {e}")

    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, reset_token_expiry FROM users WHERE reset_token = ?', (token,))
    row = cursor.fetchone()
    if row:
        expiry_str = row['reset_token_expiry']
        if expiry_str:
            try:
                expiry_dt = datetime.fromisoformat(expiry_str)
                if now > expiry_dt:
                    conn.close()
                    return False, "Password reset link has expired. Please request a new one."
            except Exception:
                pass

        cursor.execute('''
            UPDATE users SET password_hash = ?, reset_token = '', reset_token_expiry = '', last_login = ? 
            WHERE id = ?
        ''', (new_hash, now_iso, row['id']))
        conn.commit()
        conn.close()
        return True, "Password reset successfully. You can now log in with your new password."

    conn.close()
    return False, "Invalid or already used password reset link."


def get_user_stats(user_id):
    """Calculates summary statistics for the user profile."""
    if not user_id:
        return {'total_predictions': 0, 'saved_plots': 0}

    user_id_str = str(user_id)

    if is_mongo_active():
        try:
            preds_count = _mongo_db.predictions.count_documents({'user_id': user_id_str})
            plots_count = _mongo_db.farm_plots.count_documents({'user_id': user_id_str})
            return {'total_predictions': preds_count, 'saved_plots': plots_count}
        except Exception as e:
            print(f"MongoDB get_user_stats error: {e}")

    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM predictions WHERE user_id = ?', (user_id_str,))
        preds = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM farm_plots WHERE user_id = ?', (user_id_str,))
        plots = cursor.fetchone()[0]
        conn.close()
        return {'total_predictions': preds, 'saved_plots': plots}
    except Exception:
        return {'total_predictions': 0, 'saved_plots': 0}


# --- User-Specific Predictions Management ---

def add_prediction(N, P, K, temperature, humidity, ph, rainfall, predicted_crop,
                   confidence=0.0, top2_crop='', top2_conf=0.0, top3_crop='', top3_conf=0.0,
                   farm_name='Plot #1', farmer_name='User', notes='', user_id='guest'):
    """Inserts a new prediction strictly scoped to the user."""
    user_id_str = str(user_id) if user_id else 'guest'
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    doc = {
        'user_id': user_id_str,
        'farm_name': farm_name,
        'farmer_name': farmer_name,
        'N': float(N),
        'P': float(P),
        'K': float(K),
        'temperature': float(temperature),
        'humidity': float(humidity),
        'ph': float(ph),
        'rainfall': float(rainfall),
        'predicted_crop': predicted_crop,
        'confidence': float(confidence),
        'top2_crop': top2_crop,
        'top2_conf': float(top2_conf),
        'top3_crop': top3_crop,
        'top3_conf': float(top3_conf),
        'notes': notes,
        'created_at': now_iso
    }

    new_id = None

    if is_mongo_active():
        try:
            res = _mongo_db.predictions.insert_one(doc)
            new_id = str(res.inserted_id)
        except Exception as e:
            print(f"MongoDB add_prediction error: {e}")

    # Also keep SQLite in sync for resilience
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions 
            (user_id, farm_name, farmer_name, N, P, K, temperature, humidity, ph, rainfall, 
             predicted_crop, confidence, top2_crop, top2_conf, top3_crop, top3_conf, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id_str, farm_name, farmer_name, float(N), float(P), float(K), float(temperature),
              float(humidity), float(ph), float(rainfall), predicted_crop,
              float(confidence), top2_crop, float(top2_conf), top3_crop, float(top3_conf), notes, now_iso))
        conn.commit()
        if not new_id:
            new_id = str(cursor.lastrowid)
        conn.close()
    except Exception as e:
        print(f"SQLite add_prediction error: {e}")

    return new_id


def get_predictions(user_id=None, query=None, crop_filter=None, limit=100):
    """
    Retrieves predictions strictly scoped to the requesting user.
    Enforces user data isolation: one user cannot view another's predictions.
    """
    user_id_str = str(user_id) if user_id else 'guest'

    if is_mongo_active():
        try:
            filter_query = {'user_id': user_id_str}
            if crop_filter:
                filter_query['predicted_crop'] = {'$regex': f"^{re.escape(crop_filter)}$", '$options': 'i'}
            if query:
                regex = {'$regex': re.escape(query), '$options': 'i'}
                filter_query['$or'] = [
                    {'farm_name': regex},
                    {'farmer_name': regex},
                    {'predicted_crop': regex},
                    {'notes': regex}
                ]

            cursor = _mongo_db.predictions.find(filter_query).sort('created_at', -1).limit(limit)
            records = []
            for r in cursor:
                rec = dict(r)
                rec['id'] = str(rec.pop('_id'))
                records.append(rec)
            return records
        except Exception as e:
            print(f"MongoDB get_predictions error: {e}")

    # SQLite query scoped to user_id
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    sql = 'SELECT * FROM predictions WHERE user_id = ?'
    params = [user_id_str]

    if crop_filter:
        sql += ' AND LOWER(predicted_crop) = LOWER(?)'
        params.append(crop_filter)

    if query:
        sql += ' AND (farm_name LIKE ? OR farmer_name LIKE ? OR predicted_crop LIKE ? OR notes LIKE ?)'
        like_query = f'%{query}%'
        params.extend([like_query, like_query, like_query, like_query])

    sql += ' ORDER BY id DESC LIMIT ?'
    params.append(limit)

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_prediction(pred_id, user_id=None):
    """
    Deletes a single prediction by ID with strict ownership verification.
    Returns True if deleted, False if not found or unauthorized.
    """
    user_id_str = str(user_id) if user_id else 'guest'
    pred_id_str = str(pred_id)

    deleted = False

    if is_mongo_active():
        try:
            from bson import ObjectId
            query_id = ObjectId(pred_id_str) if ObjectId.is_valid(pred_id_str) else pred_id_str
            res = _mongo_db.predictions.delete_one({'_id': query_id, 'user_id': user_id_str})
            if res.deleted_count > 0:
                deleted = True
        except Exception as e:
            print(f"MongoDB delete_prediction error: {e}")

    # Also delete in SQLite
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM predictions WHERE id = ? AND user_id = ?', (pred_id_str, user_id_str))
        conn.commit()
        if cursor.rowcount > 0:
            deleted = True
        conn.close()
    except Exception as e:
        print(f"SQLite delete_prediction error: {e}")

    return deleted


def clear_predictions(user_id=None):
    """Clears all prediction history for the current user only."""
    user_id_str = str(user_id) if user_id else 'guest'

    if is_mongo_active():
        try:
            _mongo_db.predictions.delete_many({'user_id': user_id_str})
        except Exception as e:
            print(f"MongoDB clear_predictions error: {e}")

    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM predictions WHERE user_id = ?', (user_id_str,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"SQLite clear_predictions error: {e}")

    return True


# --- User-Specific Farm Plot Presets ---

def save_farm_plot(user_id, plot_name, farmer_name, N, P, K, temperature, humidity, ph, rainfall, notes=''):
    """Saves or updates a recurring farm plot profile for the specific user."""
    user_id_str = str(user_id) if user_id else 'guest'
    plot_name = (plot_name or '').strip()
    if not plot_name:
        raise ValueError("Plot name is required.")

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    doc = {
        'user_id': user_id_str,
        'plot_name': plot_name,
        'farmer_name': farmer_name or 'Farm Owner',
        'N': float(N),
        'P': float(P),
        'K': float(K),
        'temperature': float(temperature),
        'humidity': float(humidity),
        'ph': float(ph),
        'rainfall': float(rainfall),
        'notes': notes,
        'created_at': now_iso
    }

    if is_mongo_active():
        try:
            _mongo_db.farm_plots.update_one(
                {'user_id': user_id_str, 'plot_name': plot_name},
                {'$set': doc},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"MongoDB save_farm_plot error: {e}")

    # SQLite
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO farm_plots (user_id, plot_name, farmer_name, N, P, K, temperature, humidity, ph, rainfall, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, plot_name) DO UPDATE SET
            farmer_name=excluded.farmer_name,
            N=excluded.N,
            P=excluded.P,
            K=excluded.K,
            temperature=excluded.temperature,
            humidity=excluded.humidity,
            ph=excluded.ph,
            rainfall=excluded.rainfall,
            notes=excluded.notes
    ''', (user_id_str, plot_name, farmer_name, float(N), float(P), float(K),
          float(temperature), float(humidity), float(ph), float(rainfall), notes, now_iso))
    conn.commit()
    conn.close()
    return True


def get_farm_plots(user_id=None):
    """Retrieves all saved farm plot memory presets belonging to the current user."""
    user_id_str = str(user_id) if user_id else 'guest'

    if is_mongo_active():
        try:
            cursor = _mongo_db.farm_plots.find({'user_id': user_id_str}).sort('plot_name', 1)
            plots = []
            for r in cursor:
                rec = dict(r)
                rec['id'] = str(rec.pop('_id'))
                plots.append(rec)
            return plots
        except Exception as e:
            print(f"MongoDB get_farm_plots error: {e}")

    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM farm_plots WHERE user_id = ? ORDER BY plot_name ASC', (user_id_str,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# --- User-Specific Chat Memory ---

def save_chat_message(user_id, session_id, role, content):
    """Saves a chat message into conversation memory tied to the user."""
    user_id_str = str(user_id) if user_id else 'guest'
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    doc = {
        'user_id': user_id_str,
        'session_id': session_id,
        'role': role,
        'content': content,
        'created_at': now_iso
    }

    if is_mongo_active():
        try:
            _mongo_db.chat_history.insert_one(doc)
            return
        except Exception as e:
            print(f"MongoDB save_chat_message error: {e}")

    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (user_id, session_id, role, content, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id_str, session_id, role, content, now_iso))
    conn.commit()
    conn.close()


def get_chat_history(user_id, session_id, limit=15):
    """
    Retrieves recent chat history strictly scoped to the user and active session.
    Ensures conversations remain completely private between users.
    """
    user_id_str = str(user_id) if user_id else 'guest'

    if is_mongo_active():
        try:
            cursor = _mongo_db.chat_history.find(
                {'user_id': user_id_str, 'session_id': session_id}
            ).sort('created_at', 1).limit(limit)
            history = []
            for r in cursor:
                history.append({
                    'role': r.get('role', ''),
                    'content': r.get('content', ''),
                    'created_at': r.get('created_at', '')
                })
            return history
        except Exception as e:
            print(f"MongoDB get_chat_history error: {e}")

    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content, created_at FROM chat_history 
        WHERE user_id = ? AND session_id = ? ORDER BY id ASC LIMIT ?
    ''', (user_id_str, session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
