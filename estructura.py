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
