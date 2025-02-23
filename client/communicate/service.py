from cryptography.fernet import Fernet
from json import dumps, loads

# Генерация ключа
#key = Fernet.generate_key()

key = b'M95xDbhZivBW2dvs00BSE7WPgh6c2oEXIo7EX5NUizc='
cipher_suite = Fernet(key)

def encryption(data):
    pattern = {
        'method': 'POST',
        'encrypt': True,
        'data': ''
    }

    json_data = dumps(data).encode()

    # Шифрование данных
    encrypted_data = cipher_suite.encrypt(json_data)
    print(encrypted_data)
    return encrypted_data

def decryption(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data)

    data = loads(decrypted_data.decode())
    return data



# Пример использования
encrypted = encryption({"popa": 'pisa'})
print(decryption(encrypted))