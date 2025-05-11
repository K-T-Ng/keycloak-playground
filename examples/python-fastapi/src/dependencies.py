from keycloak import KeycloakOpenID
from cryptography.fernet import Fernet

from src.model import Setting


class Singleton(object):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        pass


class ApplicationSetting(Singleton):
    def __init__(self):
        self.setting = Setting()


class KeycloakOpenIDClient(KeycloakOpenID, Singleton):
    def __init__(self):
        setting = ApplicationSetting().setting
        super().__init__(
            server_url=setting.keycloak_url,
            realm_name=setting.keycloak_realm_name,
            client_id=setting.keycloak_client_id,
            client_secret_key=setting.keycloak_client_secret,
            verify=False,
        )


class CryptoClient(Singleton):
    def __init__(self):
        setting = ApplicationSetting().setting
        self.key = setting.fernet_encrypt_key
    
    def encrypt(self, plain: str) -> str:
        return Fernet(self.key).encrypt(plain.encode()).decode()
    
    def decrypt(self, cipher: str | None) -> str | None:
        if not cipher:
            return None
        return Fernet(self.key).decrypt(cipher.encode()).decode()
