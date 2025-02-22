# config.py
BASE_MEDIA_PATH = "./media"
PERSONAJES_PATH = f"{BASE_MEDIA_PATH}/personajes"
CSV_PERSONAJES = f"{PERSONAJES_PATH}/Descripciones/Avances_Personajes_Memorias_de_7.csv"
AUDIO_PATH = f"{BASE_MEDIA_PATH}/audio"  # si tienes audios
FONDOS_PATH = f"{BASE_MEDIA_PATH}/fondos"
RENDER_PATH = "./Videos"
TRANSIC_PATH = f"{BASE_MEDIA_PATH}/Transiciones"
FONTS_PATH = f"{BASE_MEDIA_PATH}/Fuentes Letra"


from modules.character_manager import get_dfpersonajes, get_personajes_features
from modules.audio_utils import get_sonidos_rutas
from modules.audio_utils import get_onomatos  # O, si la separas, de un módulo onomato.py
from modules.positions import get_Posiciones
from modules.utils import get_sentimientos

Posiciones_fondos, Posiciones_personajes, Posiciones_textos = get_Posiciones(1920, 1080)
equivalencias_sentimientos, asociacion_nuevos_sentimientos = get_sentimientos()
df_personajes = get_dfpersonajes()
personajes_car = get_personajes_features()

onomato_idea, Ambiente, sonidos_personas = get_onomatos()
sonidos_rutas = get_sonidos_rutas(sonidos_personas)

