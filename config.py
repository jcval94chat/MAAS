# config.py
BASE_MEDIA_PATH = "./media"
PERSONAJES_PATH = f"{BASE_MEDIA_PATH}/personajes"
CSV_PERSONAJES = f"{PERSONAJES_PATH}/Descripciones/Avances_Personajes_Memorias_de_7.csv"
AUDIO_PATH = f"{BASE_MEDIA_PATH}/audio"  # si tienes audios
FONDOS_PATH = f"{BASE_MEDIA_PATH}/fondos"
RENDER_PATH = "./Videos"
TRANSIC_PATH = f"{BASE_MEDIA_PATH}/Transiciones"
FONTS_PATH = f"{BASE_MEDIA_PATH}/Fuentes Letra"

from modules.positions import get_Posiciones
from modules.utils import get_sentimientos

Posiciones_fondos, Posiciones_personajes, Posiciones_textos = get_Posiciones(1920, 1080)
equivalencias_sentimientos, asociacion_nuevos_sentimientos = get_sentimientos()



