import json
import os
import datetime
from kiteconnect import KiteConnect
try:
    from config import API_KEY, API_SECRET
except ImportError:
    raise ImportError("Please create a config.py file with your API_KEY and API_SECRET.")

SESSION_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'session.json')

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

class KiteAPI:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.kite = KiteConnect(api_key=self.api_key)
        self.access_token = None

    def set_access_token(self, access_token):
        self.access_token = access_token
        self.kite.set_access_token(self.access_token)

    def get_login_url(self):
        return self.kite.login_url()

    def generate_session(self, request_token):
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.set_access_token(data["access_token"])
            self.save_session(data)
            return data
        except Exception as e:
            print(f"Error generating session: {e}")
            return None

    def save_session(self, data):
        try:
            with open(SESSION_FILE, 'w') as f:
                json.dump(data, f, default=json_serial)
            print("Session data saved successfully.")
        except Exception as e:
            print(f"Error saving session: {e}")

    def load_session(self):
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                    self.set_access_token(data["access_token"])
                    print(f"Session data loaded: {data}")
                    return data
            else:
                print("No session file found.")
                return None
        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    def is_session_valid(self):
        print("Validating session...")
        try:
            if self.get_margins() is not None:
                print("Session is valid.")
                return True
            print("Session is invalid.")
            return False
        except Exception as e:
            print(f"Session validation failed: {e}")
            return False

    def get_historical_data(self, instrument_token, from_date, to_date, interval):
        try:
            return self.kite.historical_data(instrument_token, from_date, to_date, interval)
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None

    def get_instruments(self):
        try:
            return self.kite.instruments()
        except Exception as e:
            print(f"Error fetching instruments: {e}")
            return None

    def get_margins(self):
        try:
            return self.kite.margins()
        except Exception as e:
            print(f"Error fetching margins: {e}")
            return None

    def get_positions(self):
        try:
            return self.kite.positions()
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return None

    def get_holdings(self):
        try:
            return self.kite.holdings()
        except Exception as e:
            print(f"Error fetching holdings: {e}")
            return None

kite_api = KiteAPI()
