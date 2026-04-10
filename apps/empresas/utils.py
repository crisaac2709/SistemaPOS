from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

# Esta llave debe ser un string de 32 bytes codificado en base64
# Puedes generarla una vez con: Fernet.generate_key()
MASTER_KEY =  os.getenv("MASTER_KEY")

if MASTER_KEY:
    # Convertimos a bytes para que Fernet no de error
    cipher_suite = Fernet(MASTER_KEY.encode()) 
else:
    raise ValueError("No se encontró MASTER_KEY en el archivo .env")

def encriptar_clave(texto_plano):
    if not texto_plano: return None
    return cipher_suite.encrypt(texto_plano.encode()).decode()

def desencriptar_clave(texto_encriptado):
    if not texto_encriptado: return None
    return cipher_suite.decrypt(texto_encriptado.encode()).decode()
