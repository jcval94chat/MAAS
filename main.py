#!/usr/bin/env python3
"""
main.py - Punto de entrada del proyecto de diseño de personajes

Este script orquesta la ejecución del programa utilizando funciones definidas en los módulos
contenido en la carpeta "modules". Se procesa un script de escenas, se selecciona la primera
escena y se genera una imagen combinando el fondo, un personaje (imagen) y el texto de diálogo.

Uso (desde la terminal):
    python main.py --script ruta_al_script.txt --fondo ruta_al_fondo.png --output imagen_final.jpeg --resolucion 960x540
"""

import os
import sys
import argparse

# Importar funciones desde los módulos del proyecto
from modules.script_parser import parse_script_to_dict
from modules.image_processing import generar_imagen_ejemplo
from modules.positions import get_Posiciones
from modules.file_utils import create_folder


def main():
    # Definir argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description="Ejecuta el proceso de diseño de personajes basado en un script de escenas."
    )
    parser.add_argument(
        "--script",
        type=str,
        required=True,
        help="Ruta al archivo de script de escenas (texto)."
    )
    parser.add_argument(
        "--fondo",
        type=str,
        required=True,
        help="Ruta al archivo de imagen de fondo."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="imagen_final.jpeg",
        help="Ruta donde se guardará la imagen final."
    )
    parser.add_argument(
        "--resolucion",
        type=str,
        default="960x540",
        help="Resolución en formato anchoxalto (ejemplo: 960x540)."
    )
    args = parser.parse_args()

    # Parsear la resolución (anchoxalto)
    try:
        ancho, alto = map(int, args.resolucion.lower().split('x'))
    except Exception as e:
        print("Error al parsear la resolución. Asegúrate de usar el formato anchoxalto (ejemplo: 960x540).")
        sys.exit(1)

    # Verificar que el archivo del script existe
    if not os.path.exists(args.script):
        print(f"El archivo de script no existe: {args.script}")
        sys.exit(1)

    # Leer el contenido del script
    try:
        with open(args.script, "r", encoding="utf-8") as f:
            script_content = f.read()
    except Exception as e:
        print("Error al leer el archivo de script:", e)
        sys.exit(1)

    # Procesar el script para obtener las escenas
    escenas = parse_script_to_dict(script_content)
    if not escenas:
        print("No se pudo procesar ninguna escena a partir del script.")
        sys.exit(1)
    print("Escenas parseadas:", escenas)

    # Tomamos como ejemplo la primera escena ordenada
    primera_escena_key = sorted(escenas.keys())[0]
    primera_escena = escenas[primera_escena_key]
    # Se asume que el formato es: [personaje, duración, sentimiento, acción, [líneas de diálogo]]
    try:
        personaje, duracion, sentimiento, accion, dialogo = primera_escena
    except Exception as e:
        print("Error al interpretar la primera escena:", e)
        sys.exit(1)

    # Para este ejemplo se usa una imagen de personaje ficticia.
    # En una implementación real se invocaría una función para obtener la ruta a la imagen del personaje.
    ruta_personaje = "ruta_personaje_ejemplo.png"
    if not os.path.exists(ruta_personaje):
        print(f"La imagen del personaje no se encontró: {ruta_personaje}")
        sys.exit(1)

    # Concatenar líneas de diálogo (si existen) para formar el texto a mostrar.
    texto_dialogo = "\n".join(dialogo) if dialogo else ""

    # 1) Obtener los diccionarios de posiciones escalados a la resolución especificada
    #    Esto retorna: pos_fondos, pos_personajes, pos_textos
    pos_fondos, pos_personajes, pos_textos = get_Posiciones(ancho, alto)

    # 2) Elegir la clave de posición del fondo:
    #    Asumimos "Fondos de personajes" como ejemplo. 'H C' es el valor por defecto si no se encuentra
    pos_fondo = pos_fondos.get("Fondos de personajes", "H C")

    # Asegurarse de que la carpeta de salida exista
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        create_folder(output_dir)

    # 3) Llamar a generar_imagen_ejemplo pasándole los diccionarios pos_personajes y pos_textos
    try:
        generar_imagen_ejemplo(
            fondo_path=args.fondo,
            pos_fondo=pos_fondo,
            personajes_rutas=[ruta_personaje],
            texto=texto_dialogo,
            pos_personajes=pos_personajes,
            pos_textos=pos_textos,
            save_path=args.output,
            resolucion=(ancho, alto),
            grande=False,
            verbose=True
        )
    except Exception as e:
        print("Error al generar la imagen:", e)
        sys.exit(1)

    print("Proceso completado exitosamente. Imagen guardada en:", args.output)

if __name__ == "__main__":
    main()
