# audio_utils.py
from mutagen.mp3 import MP3
from pydub import AudioSegment
from moviepy.editor import AudioFileClip

# Se asume que la función buscar_archivos está definida en file_utils.py
from file_utils import buscar_archivos

def extraer_informacion_audio(ruta):
    """
    Extrae información de un archivo de audio (MP3) y retorna un diccionario
    con la ruta, duración, bitrate, frecuencia de muestreo y número de canales.
    """
    try:
        audio = MP3(ruta)
        detalles_audio = {
            "ruta": ruta,
            "duracion": audio.info.length,         # Duración en segundos
            "bitrate": audio.info.bitrate,           # Bitrate en bps
            "frecuencia_muestreo": audio.info.sample_rate,  # Frecuencia de muestreo en Hz
            "canales": audio.info.channels,          # Número de canales
        }
    except:
        detalles_audio = {
            "ruta": ruta,
            "duracion": '',
            "bitrate": '',
            "frecuencia_muestreo": '',
            "canales": '',
        }
    return detalles_audio

def get_sonidos_rutas(sonidos_personas):
    """
    Dado un diccionario de sonidos (con nombres y rutas o lista de rutas),
    busca los archivos de audio en 'audio_path' (variable global) utilizando
    la función buscar_archivos y retorna un diccionario con la información extraída.
    
    Nota: 'audio_path' debe estar definido globalmente o en un ámbito accesible.
    """
    sonidos_rutas = {}
    for key, v in sonidos_personas.items():
        ls_rutas = []
        if isinstance(v, list):
            for x in v:
                x_agender = x.replace(' (man)','').replace(' (woman)','')\
                             .replace(' (men)','').replace(' (women)','')
                res_ = buscar_archivos(audio_path, x_agender)
                if len(res_) == 0:
                    print(key, ":_", x)
                else:
                    ls_rutas.append(extraer_informacion_audio(res_[0]))
        else:
            v_agender = v.replace(' (man)','').replace(' (woman)','')\
                         .replace(' (men)','').replace(' (women)','')
            res_ = buscar_archivos(audio_path, v_agender)
            if len(res_) == 0:
                print(key, ":", v)
            else:
                ls_rutas.append(extraer_informacion_audio(res_[0]))
        sonidos_rutas[key] = ls_rutas
    return sonidos_rutas

def extraer_duracion_rapida(datos_audio):
    """
    Extrae la duración de archivos de audio usando pydub.
    Recibe un diccionario con claves y rutas de archivos de audio, y retorna
    un diccionario con la duración en segundos de cada archivo.
    """
    resultados = {}
    for llave, ruta_mp3 in datos_audio.items():
        try:
            audio = AudioSegment.from_file(ruta_mp3)
            duracion_segundos = len(audio) / 1000.0  # Conversión de ms a s
            resultados[llave] = {
                "ruta_mp3": ruta_mp3,
                "duracion_segundos": duracion_segundos
            }
        except Exception as e:
            print(f"Error al cargar el archivo {ruta_mp3}: {e}")
            resultados[llave] = None
    return resultados

def asignar_audio_a_clips(lista_clips, lista_rutas_audio, modo_audio='cortar'):
    """
    Asigna archivos de audio a una lista de clips de video utilizando moviepy.
    
    Parámetros:
      - lista_clips: Lista de objetos VideoFileClip.
      - lista_rutas_audio: Lista de rutas a archivos de audio.
      - modo_audio: 'cortar' para recortar el audio a la duración del clip,
                    'bucle' para repetir el audio hasta completar la duración del clip,
                    'audio corto' para dejarlo sin cambios.
    
    Retorna la lista de clips con el audio asignado.
    """
    clips_con_audio = []
    for clip, ruta_audio in zip(lista_clips, lista_rutas_audio):
        audio_clip = AudioFileClip(ruta_audio)
        if modo_audio == 'cortar':
            if audio_clip.duration > clip.duration:
                audio_clip = audio_clip.subclip(0, clip.duration)
        elif modo_audio == 'bucle':
            audio_clip = audio_clip.loop(duration=clip.duration)
        elif modo_audio == 'audio corto':
            pass  # No se realizan modificaciones
        clip = clip.set_audio(audio_clip)
        clips_con_audio.append(clip)
    return clips_con_audio
