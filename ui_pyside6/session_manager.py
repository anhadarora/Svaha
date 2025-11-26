from api.kite_api import KiteAPI

class SessionManager:
    def __init__(self, kite_api: KiteAPI):
        self._kite_api = kite_api
        self.try_load_session()

    def get_kite(self):
        return self._kite_api.kite

    def try_load_session(self):
        print("Attempting to load Kite session...")
        if self._kite_api.load_session():
            print("Session loaded and valid.")
        else:
            print("No valid session found.")

    def generate_session(self, request_token):
        return self._kite_api.generate_session(request_token)
