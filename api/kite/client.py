import datetime
import json
import os

from kiteconnect import KiteConnect
from kiteconnect.exceptions import NetworkException, TokenException

from ..security import decrypt_data, encrypt_data, load_key

try:
    from config import API_KEY, API_SECRET
except ImportError:
    raise ImportError(
        "Please create a config.py file with your API_KEY and API_SECRET."
    )

SESSION_FILE = os.path.join(os.path.dirname(
    __file__), "..", "..", "generated_data", "session.json")


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class KiteAPI:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.kite = KiteConnect(api_key=self.api_key)
        self.access_token = None
        self.key = load_key()

    def set_access_token(self, access_token):
        self.access_token = access_token
        self.kite.set_access_token(self.access_token)

    def get_login_url(self):
        return self.kite.login_url()

    def generate_session(self, request_token):
        try:
            data = self.kite.generate_session(
                request_token, api_secret=self.api_secret)
            self.set_access_token(data["access_token"])
            self.save_session(data)
            return data
        except TokenException as e:
            print(f"Error generating session: Invalid token - {e}")
            return None
        except NetworkException as e:
            print(f"Error generating session: Network error - {e}")
            return None
        except Exception as e:
            print(
                f"An unexpected error occurred during session generation: {e}")
            return None

    def save_session(self, data):
        try:
            encrypted_data = encrypt_data(
                json.dumps(data, default=json_serial).encode(), self.key
            )
            with open(SESSION_FILE, "wb") as f:
                f.write(encrypted_data)
            print("Session data saved successfully.")
        except Exception as e:
            print(f"Error saving session: {e}")

    def load_session(self):
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, "rb") as f:
                    encrypted_data = f.read()
                decrypted_data = decrypt_data(encrypted_data, self.key)
                data = json.loads(decrypted_data)
                self.set_access_token(data["access_token"])
                print(f"Session data loaded.")
                return data
            else:
                print("No session file found.")
                return None
        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    def is_session_valid(self):
        print("Validating session...")
        if not self.access_token:
            return False
        try:
            margins = self.get_margins()
            if margins is not None:
                print("Session is valid.")
                return True
            else:
                print("Session is invalid (margins are None).")
                return False
        except TokenException as e:
            print(f"Session is invalid (TokenException): {e}")
            return False
        except NetworkException as e:
            print(f"Session validation failed (NetworkException): {e}")
            return False
        except Exception as e:
            print(f"Session validation failed (Exception): {e}")
            return False

    def get_historical_data(self, instrument_token, from_date, to_date, interval):
        try:
            return self.kite.historical_data(
                instrument_token, from_date, to_date, interval
            )
        except (TokenException, NetworkException) as e:
            print(f"Error fetching historical data: {e}")
            return None
        except Exception as e:
            print(
                f"An unexpected error occurred while fetching historical data: {e}")
            return None

    def get_instruments(self):
        try:
            return self.kite.instruments()
        except (TokenException, NetworkException) as e:
            print(f"Error fetching instruments: {e}")
            return None
        except Exception as e:
            print(
                f"An unexpected error occurred while fetching instruments: {e}")
            return None

    def get_margins(self):
        try:
            return self.kite.margins()
        except (TokenException, NetworkException) as e:
            print(f"Error fetching margins: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while fetching margins: {e}")
            return None

    def get_positions(self):
        try:
            return self.kite.positions()
        except (TokenException, NetworkException) as e:
            print(f"Error fetching positions: {e}")
            return None
        except Exception as e:
            print(
                f"An unexpected error occurred while fetching positions: {e}")
            return None

    def get_holdings(self):
        try:
            return self.kite.holdings()
        except (TokenException, NetworkException) as e:
            print(f"Error fetching holdings: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while fetching holdings: {e}")
            return None


kite_api = KiteAPI()