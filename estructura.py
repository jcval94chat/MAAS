import os

def imprimir_estructura(ruta, nivel=0):
    # Si la carpeta actual es "env", se omite
    if os.path.basename(ruta) == "env":
        return

    prefijo = "    " * nivel
    print(f"{prefijo}{os.path.basename(ruta)}/")
    
    try:
        entradas = os.listdir(ruta)
    except PermissionError:
        print(f"{prefijo}    [Permiso denegado]")
        return

    for entrada in sorted(entradas):
        ruta_completa = os.path.join(ruta, entrada)
        if os.path.isdir(ruta_completa):
            # Omitir subcarpeta "env"
            if entrada.lower() == "env":
                continue
            imprimir_estructura(ruta_completa, nivel + 1)
        else:
            print(f"{prefijo}    {entrada}")

if __name__ == "__main__":
    ruta_directorio = input("Ingrese la ruta de la carpeta: ").strip()
    if os.path.isdir(ruta_directorio):
        imprimir_estructura(ruta_directorio)
    else:
        print("La ruta proporcionada no es una carpeta válida.")


# Estructura:

# Guiones/
#     script.txt
# Render/
#     Video1/
#         Horizontal/
#         Vertical/
# Videos/
#     Video1/
#         Horizontal/
#         Vertical/
# Videosm/
# config.py
# main.py
# media/
#     fondos/
#         Cafetería/
#             Fondos de personajes (1).png
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png
#             Fondos de personajes (4).png
#             Fondos de personajes (5).png
#             Fondos de personajes.png
#         Calle/
#             Fondos de personajes (1).png
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png
#             Fondos de personajes (4).png
#             Fondos de personajes (5).png
#             Fondos de personajes.png
#         Elevador/
#             Fondos de personajes (1).png
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png
#             Fondos de personajes (4).png
#             Fondos de personajes (5).png
#             Fondos de personajes.png
#         Oficina/
#             Fondos de personajes (1).png
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png
#             Fondos de personajes (4).png
#             Fondos de personajes (5).png
#             Fondos de personajes.png
#         Parque/
#             Fondos de personajes (1).png
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png
#             Fondos de personajes (4).png
#             Fondos de personajes (5).png
#             Fondos de personajes.png
#         Pasillo/
#             Fondos de personajes (1).png
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png
#             Fondos de personajes (4).png
#             Fondos de personajes (5).png
#             Fondos de personajes.png
#         Puerta/
#             Fondos de personajes (1).png
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png
#             Fondos de personajes (4).png
#             Fondos de personajes (5).png
#             Fondos de personajes.png
#         Sala/
#             Fondos de personajes (1).png
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png
#             Fondos de personajes (4).png
#             Fondos de personajes (5).png
#             Fondos de personajes.png
#         Tren/
#             Fondos de personajes (1).png
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png
#             Fondos de personajes (4).png
#             Fondos de personajes (5).png
#             Fondos de personajes.png
#     personajes/
#         Descripciones/
#             Avances_Personajes_Memorias_de_7.csv.csv
#         imagenes/
#             Cactus/
#                 A_left.png
#                 angry_left.png
#                 angry_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left.png
#                 happy_right.png
#                 realistic_chair.png
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png
#             Coneja/
#                 angry_left.png
#                 angry_right.png
#                 confused_left.png
#                 confused_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_front.png
#                 happy_left.png
#                 happy_right.png
#                 realistic_chair.png
#                 realistic_photo.png
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png
#             Conejo/
#                 A_left.png
#                 A_right.png
#                 angry_left.png
#                 angry_right.png
#                 confused_left.png
#                 confused_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left.png
#                 happy_right.png
#                 realistic_chair.png
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png
#             Gata/
#                 A_right.png
#                 Correct_A_left.png
#                 Correct_happy_left.png
#                 Correct_surprised_left.png
#                 angy_left.png
#                 confused_left.png
#                 happy_right.png
#                 realistic_chair.png
#                 serious_left.png
#                 surprised_right.png
#             Kiwi/
#                 A_right.png
#                 Correct_A_left.png
#                 Correct_happy_left.png
#                 Correct_surprised_left.png
#                 angry_left.png
#                 angry_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_front.png
#                 happy_right.png
#                 realistic_chair.png
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png
#             Pata/
#                 A_left.png
#                 angry_left.png
#                 angry_right.png
#                 confused_front.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left.png
#                 realistic_chair.png
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_front.png
#                 worried_left.png
#             Pato/
#                 A_left.png
#                 A_right.png
#                 Correct_happy_left.png
#                 angry_left.png
#                 angry_right.png
#                 condused_right.png
#                 confused_left.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_right.png
#                 realistic_chair.png
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#             Pollo/
#                 A_right.png
#                 Correct_A_left.png
#                 angry_left.png
#                 angry_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left (2).png
#                 happy_left.png
#                 happy_right (2).png
#                 happy_right.png
#                 realistic_chair.png
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png
#             Rinoceronte Rojo/
#                 A_right.png
#                 Correct_A_left.png
#                 Correct_happy_left.png
#                 angry_left.png
#                 angry_right.png
#                 confused_left.png
#                 confused_right.png
#                 happy_right.png
#                 realistic_A.png
#                 realistic_chair.png
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png
#             Roca/
#                 A_left.png
#                 A_right.png
#                 angy_left.png
#                 angy_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left.png
#                 happy_right.png
#                 realistic_chair.png
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png
#             Tortuga/
#                 DALLE2_1-removebg-preview.png
#                 DALL·E 2023-12-15.png
#                 DALL·E 2023-12-12.png
# modules/
#     __init__.py
#     audio_utils.py
#     character_manager.py
#     file_utils.py
#     image_processing.py
#     positions.py
#     script_parser.py
#     utils.py
# modules/
#     __init__.py
#     audio_utils.py
#     character_manager.py
#     file_utils.py
# modules/
#     __init__.py
#     audio_utils.py
# modules/
#     __init__.py
# modules/
#     __init__.py
#     audio_utils.py
# modules/
#     __init__.py
#     audio_utils.py
#     character_manager.py
#     file_utils.py
#     image_processing.py
#     positions.py
#     script_parser.py
#     utils.py
#     video_effects.py
# requirements.txt
