# config.py
BASE_MEDIA_PATH = "./media"
PERSONAJES_PATH = f"{BASE_MEDIA_PATH}/personajes"
CSV_PERSONAJES = f"{PERSONAJES_PATH}/Descripciones/Avances_Personajes_Memorias_de_7.csv"
AUDIO_PATH = f"{BASE_MEDIA_PATH}/audio"  # si tienes audios
FONDOS_PATH = f"{BASE_MEDIA_PATH}/fondos"
RENDER_PATH = "./Videos"
TRANSIC_PATH = f"{BASE_MEDIA_PATH}/Transiciones"
FONTS_PATH = f"{BASE_MEDIA_PATH}/Fuentes Letra"
CLIPS_PATH = f"{BASE_MEDIA_PATH}/clips"

from modules.positions import get_Posiciones
from modules.utils import get_sentimientos

Posiciones_fondos, Posiciones_personajes, Posiciones_textos = get_Posiciones(1920, 1080)
equivalencias_sentimientos, asociacion_nuevos_sentimientos = get_sentimientos()

# from dotenv import load_dotenv
import os

# load_dotenv()  # carga variables desde .env
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# valor_A = os.getenv('valor_A')
# valor_B = os.getenv('valor_B')

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
valor_A = os.environ.get("VALOR_A", None)
valor_B = os.environ.get("VALOR_B", None)
