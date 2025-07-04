import os



carpeta = r"C:\Users\dsanchez\Desktop\pdf"
print("CARPETA")
a = 0

for nombre_archivo in os.listdir(carpeta):
    a = a + 1
    ruta_antigua = os.path.join(carpeta, nombre_archivo)
    # Crear nuevo nombre (ejemplo: añadir prefijo "nuevo_")
    nuevo_nombre = str(a) + nombre_archivo
    ruta_nueva = os.path.join(carpeta, nuevo_nombre)

    os.rename(ruta_antigua, ruta_nueva)
    print(f"Renombrado: {nombre_archivo} -> {nuevo_nombre}")
