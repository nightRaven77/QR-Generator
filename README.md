# 🌀 Generador de Códigos QR Personalizados

Un generador de códigos QR moderno y altamente personalizable con interfaz gráfica de usuario (GUI) construido en Python. Permite crear códigos QR con estilos de módulos únicos, colores personalizados (borde, centro, fondo) e incrustar imágenes en el centro.

---

## ✨ Características

- 📝 **Conversión directa:** Genera códigos QR desde cualquier texto o URL.
- 🎨 **Diseño Personalizable:**
  - Estilo de módulos configurables (Círculos, cuadrados redondeados, barras horizontales/verticales, etc.).
  - Selector de colores para el fondo, el borde y el centro del código QR.
- 🖼️ **Incrustar Logotipos:** Añade una imagen en el centro del código QR y ajusta su tamaño/proporción interactivamente.
- 💻 **Interfaz Moderna:** Desarrollada con `CustomTkinter` para una estética limpia, oscura y responsiva.
- 🚀 **Compilación Sencilla:** Incluye un script listo (`build_exe.py`) para generar el ejecutable de Windows (`.exe`) con un solo comando.

---

## 🛠️ Requisitos e Instalación

Este proyecto utiliza **`uv`** (el administrador de paquetes ultra rápido de Python) o el gestor estándar **`pip`**.

### Opción A: Usando `uv` (Recomendado)

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/nightRaven77/QR-Generator.git
   cd QR-Generator
   ```

2. Ejecutar la aplicación directamente (instala dependencias automáticamente en un entorno virtual):
   ```bash
   uv run main.py
   ```

### Opción B: Usando `pip` estándar

1. Instalar las dependencias listadas en el `pyproject.toml`:
   ```bash
   pip install customtkinter qrcode Pillow tomli
   ```

2. Iniciar la aplicación:
   ```bash
   python main.py
   ```

---

## 🚀 Cómo usar la Aplicación

1. **Ingresa el texto o URL** en el campo indicado.
2. **Selecciona colores personalizados** utilizando los botones de selección para el borde, centro y fondo.
3. (Opcional) **Carga una imagen** para colocarla en el centro del QR y ajusta la proporción mediante el control deslizante (slider).
4. **Elige el estilo de diseño** del QR desde el menú desplegable.
5. Haz clic en **Generar**.
6. Selecciona la ruta de tu equipo donde deseas guardar el archivo `.png` resultante.

---

## 📦 Compilación para Windows (`.exe`)

El script de compilación genera un ejecutable autónomo con soporte de iconos y metadatos de versión:

```bash
uv run build_exe.py
```
*(O `python build_exe.py` si no utilizas uv)*

El ejecutable compilado se guardará en la carpeta `dist/QRGenerator.exe`.

---

## 📂 Estructura del Proyecto

```
QR-Generator/
├── media/               # Recursos multimedia (favicon, logotipos)
├── build_exe.py         # Script para empaquetar la aplicación a .exe
├── main.py              # Interfaz gráfica y flujo principal (GUI)
├── qrDinamico.py        # Lógica de generación del código QR
├── pyproject.toml       # Dependencias y metadatos del proyecto
└── README.md            # Documentación del proyecto
```

---

## 🤝 Créditos y Tecnologías

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Interfaz visual moderna para Tkinter.
- [qrcode](https://github.com/lincolnloop/python-qrcode) - Generación de códigos QR en Python.
- [Pillow](https://python-pillow.org/) - Manipulación de imágenes.
