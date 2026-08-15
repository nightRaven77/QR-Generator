# 🌀 QR Studio Pro - Generador de Códigos QR Avanzado

Un generador de códigos QR moderno, profesional y altamente personalizable con interfaz gráfica de usuario (GUI) construido en Python con `CustomTkinter`, `Pillow` y `qrcode`. 

Permite crear códigos QR con múltiples tipos de contenido (URL, WhatsApp, Wi-Fi, vCard, Email, SMS, Geo, Calendario, Bitcoin, Masivo), estilos de módulos avanzados, patrones de búsqueda de esquinas (Finder Eyes) independientes, colores personalizados, análisis de contraste en tiempo real, logotipos de marcas e incrustación de imágenes.

---

## ✨ Características Principales

- 📝 **12 Tipos de Contenido (Payloads):**
  - 🔗 **URL**: Sitios web con protocolo http/https asegurado.
  - 💬 **WhatsApp**: Enlace directo `wa.me/<número>?text=<mensaje>` para iniciar chats con mensajes predeterminados.
  - 📶 **Wi-Fi**: Conexión rápida escaneable (SSID, contraseña, tipo de seguridad WPA/WEP y red oculta).
  - 🎴 **vCard 3.0**: Ficha de contacto digital (Nombre, Apellido, Empresa, Teléfono, Email).
  - ✉️ **Email**: `mailto:` con destinatario, asunto y cuerpo del mensaje.
  - 📱 **SMS**: `smsto:` para envío rápido de mensajes de texto.
  - 📞 **Teléfono**: Marcado directo `tel:`.
  - 📍 **Geo**: Coordenadas geográficas `geo:lat,lng`.
  - 📝 **Texto Libre**: Texto plano o notas.
  - 📅 **Evento de Calendario**: `vCalendar` con resumen, ubicación y fechas.
  - ₿ **Bitcoin**: Transacciones con dirección wallet y monto en BTC.
  - 📦 **Generador Masivo (Bulk)**: Exportación por lotes desde texto multi-línea o CSV.

- 🎨 **Design Studio & Estilos Visuales:**
  - **Presets Rápidos (Remix)**: *Classic, Rounded, Dot Matrix, Neon, Midnight, Forest, Sunset*.
  - **Formas de Módulos**: *Square, Soft Rounded, Dots, Diamond, Organic*.
  - **Patrones de Búsqueda (Finder Eyes)**: Control independiente para el Marco Exterior (Cuadrado, Círculo, Redondeado) y el Centro Interior.
  - **Selectores de Colores**: Módulos, Fondo, Marco de Ojos y Centro de Ojos.
  - **Logotipos e Iconos de Marcas**: Subida de imágenes personalizadas + librería integrada (*WhatsApp, Instagram, Facebook, Wi-Fi, Mail, Phone, Link*).
  - **Slider de Proporción de Logo**: Ajuste dinámico del tamaño del logo central.
  - **Nivel de Corrección de Errores Configurable**: Selección entre `L (7%)`, `M (15%)`, `Q (25%)` y `H (30%)`.

- ⚡ **Productividad y Exportación Avanzada:**
  - 🟢 **Indicador de Escanabilidad y Contraste WCAG**: Alerta visual en tiempo real si el contraste de color es bajo para la lectura por cámaras.
  - 📋 **Copiar al Portapapeles**: Copia el código QR generado directamente en memoria para pegarlo en cualquier aplicación (Word, Slack, WhatsApp, Photoshop).
  - 💾 **Exportación Multiformato**: Guardado en **PNG**, **SVG** (vectorial de escala infinita para imprenta), **PDF** y **JPEG**.

---

## 🛠️ Requisitos e Instalación

Este proyecto utiliza **`uv`** (el administrador de paquetes ultrarrápido de Python) o el gestor estándar **`pip`**.

### Opción A: Usando `uv` (Recomendado)

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/nightRaven77/QR-Generator.git
   cd QR-Generator
   ```

2. Ejecutar la aplicación directamente:
   ```bash
   uv run main.py
   ```

### Opción B: Usando `pip` estándar

1. Instalar las dependencias:
   ```bash
   pip install customtkinter qrcode Pillow pyinstaller
   ```

2. Iniciar la aplicación:
   ```bash
   python main.py
   ```

---

## 📦 Compilación para Windows (`.exe`)

El script de compilación genera un ejecutable autónomo listo para distribuir:

```bash
uv run build_exe.py
```
*(O `python build_exe.py` si no utilizas uv)*

El ejecutable compilado se guardará en la carpeta `dist/QRGenerator.exe`.

---

## 📂 Estructura del Proyecto

```
QR-Generator/
├── media/               # Recursos multimedia (favicon, marcas predeterminadas)
│   └── brands/          # Iconos de marcas (WhatsApp, Instagram, FB, Wi-Fi, etc.)
├── build_exe.py         # Script para empaquetar la aplicación a .exe con PyInstaller
├── main.py              # Interfaz gráfica principal (CustomTkinter)
├── qrDinamico.py        # Motor de renderizado visual y exportación de QR
├── payloads.py          # Formateador de datos para los 12 tipos de códigos QR
├── pyproject.toml       # Dependencias y metadatos del proyecto
└── README.md            # Documentación del proyecto
```

---

## 🤝 Créditos y Tecnologías

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Interfaz visual moderna en modo oscuro/claro.
- [Google Stitch MCP](https://stitch.google) - Prototipado y sistema de diseño visual UI (Pro Studio Logic).
- [qrcode](https://github.com/lincolnloop/python-qrcode) - Generador de matriz de códigos QR.
- [Pillow](https://python-pillow.org/) - Manipulación y renderizado gráfico de imágenes.
