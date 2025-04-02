import secrets

# Генерация случайного секретного ключа длиной 32 байта
secret_key = secrets.token_hex(32)
print(secret_key)


from cryptography.fernet import Fernet
import base64

# Генерируем новый ключ Fernet
key = Fernet.generate_key()

# Печатаем ключ в Base64
print(f"Сгенерированный ключ (Base64): {key.decode()}")
