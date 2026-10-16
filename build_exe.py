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
BUNDLE_ID = "com.erickmejia.qrgenerator"
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


def get_author(proj_data):
    """Obtiene el nombre del autor desde pyproject.toml"""
    authors = proj_data.get("authors", [])
    if authors and isinstance(authors, list) and "name" in authors[0]:
        return authors[0]["name"]
    return "Erick Mejía"


def create_raw_version_file(proj_data):
    """
    Crea el archivo de versión en formato RAW, usando codificación UTF-8.
    PyInstaller decodifica los archivos de versión en UTF-8.
    """
    version_str = proj_data.get("version", "0.0.0.0")
    description = proj_data.get("description", "Generador de códigos QR")
    author = get_author(proj_data)

    ver_parts = version_str.split('.')
    while len(ver_parts) < 4:
        ver_parts.append('0')

    try:
        v1, v2, v3, v4 = map(int, ver_parts[:4])
    except ValueError:
        v1 = v2 = v3 = v4 = 0

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
    """Ejecuta PyInstaller con banderas seguras según el sistema operativo"""
    print(f"[BUILD] Iniciando compilación para plataforma: {sys.platform}...")

    icon_arg = []
    if os.path.exists(ICON_FILE):
        clean_icon_path = ICON_FILE.replace('\\', '/')
        icon_arg = [f'--icon={clean_icon_path}']
    else:
        print("[WARNING] Advertencia: Icono no encontrado. Se usará el predeterminado.")

    add_data_arg = []
    if os.path.exists("media"):
        add_data_arg = [f'--add-data=media{os.pathsep}media']

    # Base de argumentos: --noupx y --clean evitan falsos positivos de antivirus
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "-y",
        "--clean",
        "--noupx",
        "--windowed",
        f"--name={APP_NAME}",
    ]

    if sys.platform == "darwin":
        # En macOS, --windowed genera directamente el bundle .app limpio.
        # No se combina con --onefile porque está deprecado en macOS y rompe la firma.
        command.append(f"--osx-bundle-identifier={BUNDLE_ID}")
    else:
        # En Windows/Linux generamos un único ejecutable con metadatos de versión
        command.append("--onefile")
        if sys.platform == "win32" and os.path.exists(VERSION_TXT):
            command.append(f"--version-file={VERSION_TXT}")

    command.extend(add_data_arg)
    command.extend(icon_arg)
    command.append(MAIN_SCRIPT)

    print(f"Comando: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")

    if result.returncode == 0:
        print("[SUCCESS] ¡Compilación de PyInstaller exitosa!")
    else:
        print("[ERROR] Error en PyInstaller:")
        print(result.stderr)
        sys.exit(result.returncode)


def sign_macos_bundle():
    """Aplica firma digital (Developer ID o Ad-Hoc) al bundle .app en macOS"""
    app_path = os.path.join("dist", f"{APP_NAME}.app")
    if not os.path.exists(app_path):
        print(f"[WARNING] No se encontró {app_path} para firmar en macOS.")
        return

    identity = os.environ.get("APPLE_SIGNING_IDENTITY", "-")
    print(f"[SIGN] Firmando {app_path} en macOS (identidad: '{identity}')...")

    sign_cmd = ["codesign", "--force", "--deep", "--sign", identity]
    if identity != "-":
        sign_cmd.extend(["--options", "runtime", "--timestamp"])
    sign_cmd.append(app_path)

    res = subprocess.run(sign_cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("[OK] Paquete .app firmado correctamente en macOS.")
        verify_res = subprocess.run(
            ["codesign", "--verify", "--deep", "--strict", "--verbose=2", app_path],
            capture_output=True,
            text=True,
        )
        if verify_res.returncode == 0:
            print("[OK] Verificación de firma codesign exitosa.")
        else:
            print(f"[WARNING] Advertencia en verificación codesign: {verify_res.stderr}")
    else:
        print(f"[WARNING] No se pudo firmar el paquete .app: {res.stderr}")


def sign_windows_executable(proj_data):
    """
    Firma digitalmente dist/QRGenerator.exe en Windows con Authenticode SHA-256.
    Si existe WINDOWS_PFX_PATH usa ese certificado; de lo contrario, si se indica
    --self-sign o SELF_SIGN_EXE=1, genera/aplica un certificado autofirmado.
    """
    exe_path = os.path.abspath(os.path.join("dist", f"{APP_NAME}.exe"))
    if not os.path.exists(exe_path):
        print(f"[WARNING] No se encontró {exe_path} para firmar.")
        return

    pfx_path = os.environ.get("WINDOWS_PFX_PATH", "")
    pfx_password = os.environ.get("WINDOWS_PFX_PASSWORD", "")
    do_self_sign = "--self-sign" in sys.argv or os.environ.get("SELF_SIGN_EXE") == "1"

    if not pfx_path and not do_self_sign:
        print("[INFO] Omitiendo firma local (usa '--self-sign' o variables WINDOWS_PFX_PATH para firmar).")
        return

    author = get_author(proj_data)
    print(f"[SIGN] Firmando {exe_path} con Authenticode SHA-256...")

    if pfx_path and os.path.exists(pfx_path):
        ps_script = f"""
        $ErrorActionPreference = 'Stop'
        $pwd = ConvertTo-SecureString -String '{pfx_password}' -AsPlainText -Force
        $cert = Get-PfxCertificate -FilePath '{pfx_path}' -Password $pwd
        $sig = Set-AuthenticodeSignature -FilePath '{exe_path}' -Certificate $cert -HashAlgorithm SHA256 -TimestampServer 'http://timestamp.digicert.com'
        if ($sig.Status -ne 'Valid' -and $sig.Status -ne 'UnknownError') {{
            Write-Output "Estado de firma: $($sig.Status) - $($sig.StatusMessage)"
        }}
        """
    else:
        ps_script = f"""
        $ErrorActionPreference = 'Stop'
        $subject = 'CN={author}, O={APP_NAME}'
        $cert = Get-ChildItem Cert:\\CurrentUser\\My -CodeSigningCert | Where-Object {{ $_.Subject -eq $subject }} | Select-Object -First 1
        if (-not $cert) {{
            $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject $subject -KeyUsage DigitalSignature -KeyAlgorithm RSA -KeyLength 2048 -HashAlgorithm SHA256 -CertStoreLocation 'Cert:\\CurrentUser\\My' -NotAfter (Get-Date).AddYears(3)
        }}
        Export-Certificate -Cert $cert -FilePath 'dist\\{APP_NAME}-PublicCert.cer' -Force | Out-Null
        $sig = Set-AuthenticodeSignature -FilePath '{exe_path}' -Certificate $cert -HashAlgorithm SHA256 -TimestampServer 'http://timestamp.digicert.com'
        Write-Output "Firmado con thumbprint: $($cert.Thumbprint) | Estado: $($sig.Status)"
        """

    res = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode == 0:
        print(f"[OK] Ejecutable firmado en Windows. {res.stdout.strip()}")
    else:
        print(f"[WARNING] No se pudo completar la firma en Windows: {res.stderr.strip()}")


if __name__ == "__main__":
    print("--- Iniciando ---")
    proj_data = read_pyproject()
    if sys.platform == "win32":
        create_raw_version_file(proj_data)

    run_pyinstaller()

    if sys.platform == "darwin":
        sign_macos_bundle()
    elif sys.platform == "win32":
        sign_windows_executable(proj_data)

    # Limpieza
    if os.path.exists(VERSION_TXT):
        os.remove(VERSION_TXT)
        print("[CLEAN] Archivo temporal eliminado.")
    print("--- Finalizado ---")