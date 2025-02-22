#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main.py – Archivo principal para la generación y renderizado de escenas localmente.

Este script utiliza configuraciones y variables definidas en config.py, por lo que ya se tienen:
    Posiciones_fondos, Posiciones_personajes, Posiciones_textos
    equivalencias_sentimientos, asociacion_nuevos_sentimientos
    df_personajes, personajes_car
    onomato_idea, Ambiente, sonidos_personas, sonidos_rutas

Además, se importa el script de guión desde Guiones/script.txt y se usan funciones de los módulos:
  • positions, utils, file_utils, script_parser, character_manager,
    audio_utils, video_effects e image_processing (para get_img_transitions).
  
Asegúrate de que la estructura de carpetas esté organizada según las rutas definidas en config.py.
"""

import os
import time

# Importar configuraciones y variables definidas en config.py
from config import (
    BASE_MEDIA_PATH, PERSONAJES_PATH, CSV_PERSONAJES, AUDIO_PATH,
    FONDOS_PATH, RENDER_PATH, TRANSIC_PATH, FONTS_PATH,
    Posiciones_fondos, Posiciones_personajes, Posiciones_textos,
    equivalencias_sentimientos, asociacion_nuevos_sentimientos,
    df_personajes, personajes_car, onomato_idea, Ambiente, sonidos_personas, sonidos_rutas
)

# Importar funciones de los módulos
from modules.file_utils import get_folder_content, move_and_rename_file, get_chapter_number
from modules.script_parser import get_ESCENAS, get_random_advice
from modules.character_manager import get_dict_personajes_
from modules.audio_utils import get_onomatos, get_sonidos_rutas
from modules.video_effects import (
    crear_clips_de_imagenes, create_ordered_video, renderizar_audios,
    concatenar_clips_segun_audio, get_paths_save, get_chapter_render,
    Create_Scene_Media, ordenar_clips_audio
)
from modules.image_processing import get_img_transitions
from modules.utils import create_folder, reorganize_dict_by_format, get_sentimientos  # get_sentimientos ya está en config, se puede usar si se requiere

# Definir rutas locales adicionales
FONT_PATH = os.path.join(FONTS_PATH, "Raleway", "Raleway-Medium.ttf")
PATH_SAVE = "imagen_final.jpeg"

def main():
    # Leer el script inicial desde el archivo en la carpeta Guiones
    script_path = os.path.join("Guiones", "script.txt")
    with open(script_path, "r", encoding="utf-8") as f:
        script_inicial = f.read()

    # Crear carpeta para audios si no existe
    audios_path = "audios"
    create_folder(audios_path)

    # Obtener lista de fondos disponibles (se asume que FONDOS_PATH contiene subcarpetas con nombres de lugares)
    fondos = get_folder_content(FONDOS_PATH)
    lugares_disp = [os.path.basename(os.path.dirname(fondo)).lower() for fondo in fondos]

    # Generar un contexto descriptivo de personajes (usando personajes_car ya importado de config)
    personajes = [row for row in personajes_car[['Personajes', 'Sexo', 'Rol', 'Descripcion']].values if row[0] != '']
    descripcion_personajes = "\n".join([f"{p[0]} (Sexo: {p[1]}, Rango: {p[2]}): {p[3]}" for p in personajes])
    contexto = f"Aquí está la lista de personajes (LP):\n{descripcion_personajes}\n"

    # Procesar el script para obtener escenas, lugares y transiciones
    ESCENAS_, LUGARES_, textos_cambio_escena = get_ESCENAS(script_inicial, lugares_disp)

    # Uso de OpenAI para obtener el diccionario de asignación de personajes
    sust_dd = get_dict_personajes_(ESCENAS_)

    # Procesar transiciones de imágenes (se importa get_img_transitions desde image_processing)
    if len(textos_cambio_escena) > 0:
        output_transition_images = get_img_transitions(textos_cambio_escena, False)
        ruta_audio_trn = os.path.join(AUDIO_PATH, "Eff Sonido", "Background", "Pasarla bien_Menu - Cooking Mama Soundtrack.mp3")
        rytas_horizzz = [x[0] for x in output_transition_images]
        rytas_vertical = [x[1] for x in output_transition_images]
        clips_horiz_trans = crear_clips_de_imagenes(rytas_horizzz, ruta_audio=ruta_audio_trn)
        clips_ver_trans = crear_clips_de_imagenes(rytas_vertical, ruta_audio=ruta_audio_trn)
    else:
        clips_horiz_trans = []
        clips_ver_trans = []

    # Otra transición utilizando un consejo aleatorio
    output_transition_images = get_img_transitions({1: get_random_advice()}, False, TRANSIC_PATH, 'subl_')
    ruta_audio_trn = os.path.join(AUDIO_PATH, "Eff Sonido", "Background", "Pasarla bien_Menu - Cooking Mama Soundtrack.mp3")
    subl_clip_hor = crear_clips_de_imagenes([x[0] for x in output_transition_images],
                                             duracion_por_imagen=0.04, ruta_audio=ruta_audio_trn)
    subl_clip_ver = crear_clips_de_imagenes([x[1] for x in output_transition_images],
                                             duracion_por_imagen=0.04, ruta_audio=ruta_audio_trn)

    # Iniciar contador global para medir tiempos
    overall_start = time.perf_counter()

    # Inicializar estructuras para almacenar resultados
    output_paths_start_ls = {}
    output_paths_ls = {}
    clips_list = {}
    rutas_ends_ls = {}
    ruta_audio_ls = {}
    videos_list = {}
    no_escena = 0
    tiempos_por_escena = {}

    # Procesar cada escena extraída del script
    for (desagregar, lugar___) in zip(ESCENAS_, LUGARES_):
        escena_start = time.perf_counter()
        seg_tiempos = {}

        print("\nProcesando escena para lugar:", lugar___)
        escenas_info_, sentimientos, personajes = desagregar

        # Segmento 1: Renderizar audios para la escena
        seg_start = time.perf_counter()
        escenas_info, Dialogos_onomatos, Dialogos_con_voz, audios_generados, ruta_audios = renderizar_audios(
            escenas_info_, personajes_car, onomato_idea, personajes, sust_dd)
        seg_tiempos['renderizar_audios'] = time.perf_counter() - seg_start

        # Segmento 2: Obtener número de capítulo
        seg_start = time.perf_counter()
        if 'n_chapter' not in locals():
            n_chapter = get_chapter_number(os.path.join(BASE_MEDIA_PATH, "Caps", "BetaV"))
        seg_tiempos['get_chapter_number'] = time.perf_counter() - seg_start

        # Segmento 3: Determinar el lugar equivalente en fondos
        seg_start = time.perf_counter()
        equiv_lugares = {f.lower().strip(): f for f in os.listdir(FONDOS_PATH) if os.path.isdir(os.path.join(FONDOS_PATH, f))}
        lugar_equivalente = equiv_lugares.get(lugar___, lugar___)
        seg_tiempos['determinar_lugar_equivalente'] = time.perf_counter() - seg_start

        # Segmento 4: Crear medios de la escena
        rutas_vid, clips_ls, rutas_img_text = Create_Scene_Media(
            escenas_info=escenas_info,
            lugar=lugar_equivalente,
            chap_n=n_chapter,
            gen_vid=False,
            sounds=sonidos_personas,
            verbose=True,
            apply_temblor_effect=True,
            sust_dd=sust_dd,
        )
        seg_tiempos['Create_Scene_Media'] = time.perf_counter() - seg_start

        # Segmento 5: Procesar textos a partir de imágenes
        seg_start = time.perf_counter()
        def flatten(xss):
            return [x for xs in xss for x in xs]
        text_in_img = flatten([list(x.values()) for x in rutas_img_text])
        seg_tiempos['flatten_text_in_img'] = time.perf_counter() - seg_start

        # Segmento 6: Ordenar clips y audio
        seg_start = time.perf_counter()
        clips_ordered, Audio_fondo_activo = ordenar_clips_audio(
            rutas_vid, clips_ls, text_in_img, personajes_car, ruta_audios, Dialogos_con_voz)
        seg_tiempos['ordenar_clips_audio'] = time.perf_counter() - seg_start

        # Segmento 7: Concatenar y dividir clips según audio
        seg_start = time.perf_counter()
        clips_procesados = concatenar_clips_segun_audio(clips_ordered, Audio_fondo_activo)
        clips_procesados_hor = clips_procesados[:len(clips_procesados)//2]
        clips_procesados_ver = clips_procesados[len(clips_procesados)//2:]
        seg_tiempos['concatenar_y_dividir_clips'] = time.perf_counter() - seg_start

        # Segmento 8: Obtener rutas de guardado para el video
        seg_start = time.perf_counter()
        ruta_audio, output_paths, output_paths_start, rutas_ending = get_paths_save(rutas_vid)
        seg_tiempos['get_paths_save'] = time.perf_counter() - seg_start

        # Segmento 9: Guardar resultados y generar render final del capítulo
        seg_start = time.perf_counter()
        key = f'Escena_{no_escena}-{lugar_equivalente}'
        output_paths_start_ls[key] = output_paths_start
        output_paths_ls[key] = output_paths
        clips_list[key] = [clips_procesados_hor, clips_procesados_ver]
        rutas_ends_ls[key] = rutas_ending
        ruta_audio_ls[key] = ruta_audio
        videos_list[key] = get_chapter_render([clips_procesados_hor, clips_procesados_ver],
                                              ruta_audio, lugar_equivalente, no_escena)
        seg_tiempos['guardar_resultados_y_get_chapter_render'] = time.perf_counter() - seg_start

        escena_end = time.perf_counter()
        total_escena = escena_end - escena_start
        seg_tiempos['total_por_escena'] = total_escena
        tiempos_por_escena[key] = seg_tiempos

        no_escena += 1
        print(f"Escena {no_escena} terminada. Tiempo total: {total_escena:.4f} segundos")
        for seg, t in seg_tiempos.items():
            print(f"  Segmento {seg}: {t:.4f} segundos")

    overall_end = time.perf_counter()
    total_overall = overall_end - overall_start
    print("\nTiempo total de procesamiento:", total_overall, "segundos")
    print("\nDetalle de tiempos por escena:")
    for key, tiempos in tiempos_por_escena.items():
        print("Para", key, ":", tiempos)

    # Reestructurar diccionarios para la generación final de videos
    A_output_paths_start_ls = reorganize_dict_by_format(output_paths_start_ls)
    A_output_paths_ls = reorganize_dict_by_format(output_paths_ls)
    A_clips_list = reorganize_dict_by_format(clips_list)
    A_rutas_ends_ls = reorganize_dict_by_format(rutas_ends_ls)
    A_videos_list_ls = reorganize_dict_by_format(videos_list)

    ruta_audio_final = list(ruta_audio_ls.values())[0]
    for orientacion in ['Vertical', 'Horizontal']:
        vertical = True if orientacion == 'Vertical' else False
        clip_transicion = clips_ver_trans if vertical else clips_horiz_trans
        subl_clip = subl_clip_ver if vertical else subl_clip_hor
        start_path = list(A_output_paths_start_ls[orientacion][0].values())[0]
        final_path = list(A_output_paths_ls[orientacion][0].values())[0]
        ruta_ending = list(A_rutas_ends_ls[orientacion][0].values())[0]
        video_dict_list = A_videos_list_ls[orientacion]
        print("Renderizando Videos para", orientacion)
        create_ordered_video(video_dict_list, clip_transicion, subl_clip,
                             ruta_ending, start_path, True, True, vertical, 1)
        carpeta_s = os.path.dirname(final_path)
        spth = os.path.basename(final_path)
        try:
            move_and_rename_file(start_path, carpeta_s, spth)
        except Exception as e:
            print("No se pudo mover el archivo:", e)

if __name__ == "__main__":
    main()
