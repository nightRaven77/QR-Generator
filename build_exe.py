import subprocess
import os
import sys
import codecs
from datetime import date

# Configurar encoding de stdout/stderr para Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Intentar importar tomllib (py 3.11+) o tomli (anterior)
try:
    import tomllib
except ImportError:
    try:
        # pyrefly: ignore [missing-import]
        import tomli as tomllib
    except ImportError:
        print("[ERROR] Necesitas instalar la librería 'tomli' para leer pyproject.toml")
        sys.exit(1)

# --- CONFIGURACIÓN ---
APP_NAME = "QRGenerator" 
MAIN_SCRIPT = "main.py" 
ICON_FILE = "media/favicon.ico" 
VERSION_TXT = "file_version_info.txt"

def read_pyproject():
    """Lee los datos del pyproject.toml"""
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {})
    except FileNotFoundError:
        print("[ERROR] pyproject.toml no encontrado.")
        sys.exit(1)

def create_raw_version_file(proj_data):
    """
    Crea el archivo de versión en formato RAW, usando codificación UTF-8.
    PyInstaller decodifica los archivos de versión en UTF-8.
    """
    version_str = proj_data.get("version", "0.0.0.0")
    description = proj_data.get("description", "Generador de códigos QR")
    author = "Erick"
    
    ver_parts = version_str.split('.')
    while len(ver_parts) < 4:
        ver_parts.append('0')
    
    try:
        v1, v2, v3, v4 = map(int, ver_parts)
    except ValueError:
        v1=v2=v3=v4=0

    year = date.today().year

    raw_template = r"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({v1}, {v2}, {v3}, {v4}),
    prodvers=({v1}, {v2}, {v3}, {v4}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [
        StringStruct(u'CompanyName', u'{author}'),
        StringStruct(u'FileDescription', u'{description}'),
        StringStruct(u'FileVersion', u'{version_str}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'© {year} {author}'),
        StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
        StringStruct(u'ProductName', u'{APP_NAME}'),
        StringStruct(u'ProductVersion', u'{version_str}')
        ])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    file_content = raw_template.format(
        v1=v1, v2=v2, v3=v3, v4=v4,
        author=author, description=description,
        version_str=version_str, APP_NAME=APP_NAME, year=year
    )

    try:
        with open(VERSION_TXT, "w", encoding="utf-8") as f:
            f.write(file_content)
        print(f"[OK] Archivo '{VERSION_TXT}' generado correctamente (UTF-8).")
    except Exception as e:
        print(f"[ERROR] Error crítico al guardar el archivo de versión: {e}")
        sys.exit(1)


def run_pyinstaller():
    """Ejecuta PyInstaller"""
    print("[BUILD] Iniciando compilación...")
    
    icon_arg = []
    if os.path.exists(ICON_FILE):
        clean_icon_path = ICON_FILE.replace('\\', '/')
        icon_arg = [f'--icon={clean_icon_path}']
    else:
        print(f"[WARNING] Advertencia: Icono no encontrado. Se usará el predeterminado.")

    add_data_arg = []
    if os.path.exists("media"):
        add_data_arg = [f'--add-data=media{os.pathsep}media']

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "-y",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        f"--version-file={VERSION_TXT}",
        *add_data_arg,
        *icon_arg,
        MAIN_SCRIPT
    ]

    print(f"Comando: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    
    if result.returncode == 0:
        print("[SUCCESS] ¡Compilación exitosa!")
    else:
        print("[ERROR] Error en PyInstaller:")
        print(result.stderr)
        sys.exit(result.returncode)

if __name__ == "__main__":
    print("--- Iniciando ---")
    proj_data = read_pyproject()
    create_raw_version_file(proj_data)
    run_pyinstaller()
    
    # Limpieza
    if os.path.exists(VERSION_TXT):
        os.remove(VERSION_TXT)
        print(f"[CLEAN] Archivo temporal eliminado.")
    print("--- Finalizado ---")