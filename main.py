import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from io import BytesIO
from PIL import Image, ImageTk

import customtkinter
import payloads
import qrDinamico

# Configuración de tema CustomTkinter
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

def get_asset_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller y entorno local."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Paletas de Presets de diseño rápido
PRESET_THEMES = {
    "Classic": {
        "module": "#09090b",
        "back": "#ffffff",
        "fframe": "#09090b",
        "fcenter": "#09090b",
        "mshape": "square",
        "ffshape": "square",
        "fcshape": "square"
    },
    "Rounded": {
        "module": "#18181b",
        "back": "#ffffff",
        "fframe": "#18181b",
        "fcenter": "#18181b",
        "mshape": "rounded",
        "ffshape": "rounded",
        "fcshape": "circle"
    },
    "Dot Matrix": {
        "module": "#09090b",
        "back": "#ffffff",
        "fframe": "#09090b",
        "fcenter": "#09090b",
        "mshape": "dots",
        "ffshape": "circle",
        "fcshape": "circle"
    },
    "Neon": {
        "module": "#67e8f9",
        "back": "#083344",
        "fframe": "#22d3ee",
        "fcenter": "#67e8f9",
        "mshape": "rounded",
        "ffshape": "rounded",
        "fcshape": "circle"
    },
    "Midnight": {
        "module": "#e0e7ff",
        "back": "#172554",
        "fframe": "#818cf8",
        "fcenter": "#e0e7ff",
        "mshape": "organic",
        "ffshape": "rounded",
        "fcshape": "circle"
    },
    "Forest": {
        "module": "#166534",
        "back": "#f0fdf4",
        "fframe": "#15803d",
        "fcenter": "#166534",
        "mshape": "dots",
        "ffshape": "circle",
        "fcshape": "circle"
    },
    "Sunset": {
        "module": "#c2410c",
        "back": "#fff7ed",
        "fframe": "#ea580c",
        "fcenter": "#c2410c",
        "mshape": "diamond",
        "ffshape": "rounded",
        "fcshape": "square"
    }
}

class QRStudioApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("QR Studio Pro - Generador de Códigos QR Avanzado")
        self.geometry("1120x760")
        self.minsize(980, 680)

        # Icono de aplicación
        try:
            icon_p = get_asset_path("media/favicon.ico")
            if os.path.exists(icon_p):
                self.iconbitmap(icon_p)
        except Exception:
            pass

        # Variables de estado
        self.current_payload_type = "URL"
        self.module_color = "#09090b"
        self.back_color = "#ffffff"
        self.finder_frame_color = "#09090b"
        self.finder_center_color = "#09090b"

        self.module_shape = tk.StringVar(value="square")
        self.finder_frame_shape = tk.StringVar(value="square")
        self.finder_center_shape = tk.StringVar(value="square")
        self.error_correction = tk.StringVar(value="H")
        self.logo_ratio = tk.DoubleVar(value=0.22)
        self.export_format = tk.StringVar(value="PNG")

        # Nuevas variables avanzadas
        self.logo_background_pad = tk.BooleanVar(value=True)
        self.logo_background_color = "#ffffff"
        self.module_scale = tk.DoubleVar(value=1.0)
        self.card_corner_radius = tk.DoubleVar(value=1.0)
        self.target_resolution = tk.StringVar(value="1200px")
        self.canvas_padding_px = tk.IntVar(value=40)

        self.use_top_heading = tk.BooleanVar(value=False)
        self.top_heading_text = tk.StringVar(value="My QR Code")
        self.top_heading_color = "#4338ca"
        self.top_heading_size = tk.IntVar(value=25)

        self.use_bottom_caption = tk.BooleanVar(value=False)
        self.bottom_caption_text = tk.StringVar(value="Scan me")
        self.bottom_caption_color = "#4338ca"
        self.bottom_caption_size = tk.IntVar(value=25)
        self.font_family = tk.StringVar(value="Sans-Serif")

        self.logo_path = None
        self.current_qr_img = None
        self.history_records = []

        # Construir Interfaz
        self._setup_layout()
        self._build_sidebar()
        self._build_preview_panel()
        self._switch_payload_tab("URL")
        self._render_qr_preview()

    def _setup_layout(self):
        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self):
        """Construye el panel izquierdo con los controles y studio"""
        self.sidebar_scroll = customtkinter.CTkScrollableFrame(
            self, corner_radius=12, fg_color="#16191e"
        )
        self.sidebar_scroll.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)

        # Encabezado
        header_frame = customtkinter.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 16))

        eyebrow = customtkinter.CTkLabel(
            header_frame, text="PRO STUDIO UTILITY", font=("Geist", 11, "bold"), text_color="#00f0ff"
        )
        eyebrow.pack(anchor="w")

        title = customtkinter.CTkLabel(
            header_frame, text="Generador de Códigos QR", font=("Hanken Grotesk", 24, "bold"), text_color="#e2e2e8"
        )
        title.pack(anchor="w")

        # -------------------------------------------------------------
        # SECCIÓN 1: TIPO DE CONTENIDO (PAYLOAD)
        # -------------------------------------------------------------
        section1_label = customtkinter.CTkLabel(
            self.sidebar_scroll, text="01. TIPO DE CONTENIDO", font=("Geist", 12, "bold"), text_color="#849495"
        )
        section1_label.pack(anchor="w", padx=12, pady=(8, 6))

        # Grid de botones de Payload
        self.payload_buttons_frame = customtkinter.CTkFrame(self.sidebar_scroll, fg_color="#1e2024", corner_radius=10)
        self.payload_buttons_frame.pack(fill="x", padx=12, pady=(0, 12))

        payload_types = [
            ("🔗 URL", "URL"),
            ("💬 WhatsApp", "WhatsApp"),
            ("📶 Wi-Fi", "Wi-Fi"),
            ("🎴 vCard", "vCard"),
            ("✉️ Email", "Email"),
            ("📱 SMS", "SMS"),
            ("📞 Teléfono", "Phone"),
            ("📍 Geo", "Geo"),
            ("📝 Texto", "Text"),
            ("📅 Evento", "Calendar"),
            ("₿ Bitcoin", "Bitcoin"),
            ("📦 Masivo", "Bulk")
        ]

        self.payload_btn_dict = {}
        for idx, (label_txt, p_type) in enumerate(payload_types):
            r = idx // 4
            c = idx % 4
            btn = customtkinter.CTkButton(
                self.payload_buttons_frame,
                text=label_txt,
                font=("Hanken Grotesk", 12, "bold"),
                height=36,
                corner_radius=8,
                fg_color="#282a2e",
                text_color="#e2e2e8",
                hover_color="#006970",
                command=lambda pt=p_type: self._switch_payload_tab(pt)
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="ew")
            self.payload_buttons_frame.grid_columnconfigure(c, weight=1)
            self.payload_btn_dict[p_type] = btn

        # Contenedor dinámico del formulario de payload
        self.payload_form_frame = customtkinter.CTkFrame(self.sidebar_scroll, fg_color="#1e2024", corner_radius=10)
        self.payload_form_frame.pack(fill="x", padx=12, pady=(0, 16))

        # -------------------------------------------------------------
        # SECCIÓN 2: DESIGN STUDIO & ESTILOS
        # -------------------------------------------------------------
        section2_label = customtkinter.CTkLabel(
            self.sidebar_scroll, text="02. DESIGN STUDIO", font=("Geist", 12, "bold"), text_color="#849495"
        )
        section2_label.pack(anchor="w", padx=12, pady=(8, 6))

        studio_frame = customtkinter.CTkFrame(self.sidebar_scroll, fg_color="#1e2024", corner_radius=10)
        studio_frame.pack(fill="x", padx=12, pady=(0, 16))

        # Presets Rápidos (Remix)
        preset_lbl = customtkinter.CTkLabel(
            studio_frame, text="Presets de Estilo (Remix):", font=("Hanken Grotesk", 12, "bold"), text_color="#e2e2e8"
        )
        preset_lbl.pack(anchor="w", padx=12, pady=(12, 4))

        presets_subframe = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        presets_subframe.pack(fill="x", padx=12, pady=(0, 12))

        for p_name in PRESET_THEMES.keys():
            p_btn = customtkinter.CTkButton(
                presets_subframe,
                text=p_name,
                font=("Hanken Grotesk", 11),
                height=28,
                corner_radius=6,
                fg_color="#282a2e",
                hover_color="#00f0ff",
                text_color="#e2e2e8",
                command=lambda name=p_name: self._apply_preset_theme(name)
            )
            p_btn.pack(side="left", padx=3, pady=2)

        # Formas de Módulos
        mshape_lbl = customtkinter.CTkLabel(
            studio_frame, text="Forma de Módulos:", font=("Hanken Grotesk", 12, "bold"), text_color="#e2e2e8"
        )
        mshape_lbl.pack(anchor="w", padx=12, pady=(8, 4))

        module_options = [
            "square", "soft_rounded", "dots", "organic", "diamond",
            "pebble", "leaf", "star", "heart", "cross",
            "rounded", "horizontal_bars", "vertical_bars", "gapped_square"
        ]
        mshape_menu = customtkinter.CTkOptionMenu(
            studio_frame,
            values=module_options,
            variable=self.module_shape,
            fg_color="#282a2e",
            button_color="#333539",
            text_color="#e2e2e8",
            command=lambda val: self._on_setting_changed()
        )
        mshape_menu.pack(fill="x", padx=12, pady=(0, 12))

        # Finder Frames & Centers (Esquinas Ojos)
        finders_grid = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        finders_grid.pack(fill="x", padx=12, pady=(0, 12))
        finders_grid.grid_columnconfigure((0, 1), weight=1)

        ff_lbl = customtkinter.CTkLabel(finders_grid, text="Marco de Ojos:", font=("Hanken Grotesk", 11, "bold"))
        ff_lbl.grid(row=0, column=0, sticky="w", padx=4)
        ff_menu = customtkinter.CTkOptionMenu(
            finders_grid, values=["square", "circle", "soft_square", "leaf", "diamond", "shield"], variable=self.finder_frame_shape,
            fg_color="#282a2e", button_color="#333539", command=lambda val: self._on_setting_changed()
        )
        ff_menu.grid(row=1, column=0, sticky="ew", padx=4, pady=2)

        fc_lbl = customtkinter.CTkLabel(finders_grid, text="Centro de Ojos:", font=("Hanken Grotesk", 11, "bold"))
        fc_lbl.grid(row=0, column=1, sticky="w", padx=4)
        fc_menu = customtkinter.CTkOptionMenu(
            finders_grid, values=["square", "circle", "soft_square", "diamond", "leaf", "star", "heart"], variable=self.finder_center_shape,
            fg_color="#282a2e", button_color="#333539", command=lambda val: self._on_setting_changed()
        )
        fc_menu.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        # Selectores de Color
        color_grid = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        color_grid.pack(fill="x", padx=12, pady=(0, 12))
        color_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_color_mod = customtkinter.CTkButton(
            color_grid, text="Módulos", font=("Hanken Grotesk", 11), fg_color=self.module_color,
            command=lambda: self._choose_color("module")
        )
        self.btn_color_mod.grid(row=0, column=0, padx=2, pady=4)

        self.btn_color_bg = customtkinter.CTkButton(
            color_grid, text="Fondo", font=("Hanken Grotesk", 11), fg_color=self.back_color,
            text_color="#000000" if self.back_color=="#ffffff" else "#ffffff", command=lambda: self._choose_color("back")
        )
        self.btn_color_bg.grid(row=0, column=1, padx=2, pady=4)

        self.btn_color_ff = customtkinter.CTkButton(
            color_grid, text="Marco Ojos", font=("Hanken Grotesk", 11), fg_color=self.finder_frame_color,
            command=lambda: self._choose_color("fframe")
        )
        self.btn_color_ff.grid(row=0, column=2, padx=2, pady=4)

        self.btn_color_fc = customtkinter.CTkButton(
            color_grid, text="Centro Ojos", font=("Hanken Grotesk", 11), fg_color=self.finder_center_color,
            command=lambda: self._choose_color("fcenter")
        )
        self.btn_color_fc.grid(row=0, column=3, padx=2, pady=4)

        # Logo Central & Marcas Predeterminadas
        logo_sec_lbl = customtkinter.CTkLabel(
            studio_frame, text="Logo Central:", font=("Hanken Grotesk", 12, "bold"), text_color="#e2e2e8"
        )
        logo_sec_lbl.pack(anchor="w", padx=12, pady=(8, 4))

        logo_subframe = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        logo_subframe.pack(fill="x", padx=12, pady=(0, 8))

        upload_logo_btn = customtkinter.CTkButton(
            logo_subframe, text="📁 Subir Imagen", font=("Hanken Grotesk", 11), fg_color="#282a2e",
            hover_color="#006970", command=self._upload_custom_logo
        )
        upload_logo_btn.pack(side="left", padx=(0, 6))

        remove_logo_btn = customtkinter.CTkButton(
            logo_subframe, text="❌ Quitar", font=("Hanken Grotesk", 11), fg_color="#3a1e24",
            hover_color="#93000a", command=self._remove_logo
        )
        remove_logo_btn.pack(side="left")

        # Marcas Rápidas
        brands_frame = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        brands_frame.pack(fill="x", padx=12, pady=(0, 8))

        brand_list = ["whatsapp", "instagram", "facebook", "wifi", "mail", "phone", "link"]
        for b_name in brand_list:
            b_path = get_asset_path(f"media/brands/{b_name}.png")
            if os.path.exists(b_path):
                try:
                    pil_b = Image.open(b_path).resize((22, 22))
                    ctk_b = customtkinter.CTkImage(pil_b, size=(22, 22))
                    b_btn = customtkinter.CTkButton(
                        brands_frame, image=ctk_b, text="", width=34, height=34, fg_color="#282a2e",
                        hover_color="#00f0ff", command=lambda p=b_path: self._set_brand_logo(p)
                    )
                    b_btn.pack(side="left", padx=2)
                except Exception:
                    pass

        # Toggle y Selector de Color para Fondo de Logo (Show logo background & color)
        logo_bg_frame = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        logo_bg_frame.pack(fill="x", padx=12, pady=(4, 6))

        logo_pad_switch = customtkinter.CTkSwitch(
            logo_bg_frame, text="Show logo background", variable=self.logo_background_pad,
            font=("Hanken Grotesk", 11, "bold"), progress_color="#00f0ff", command=lambda: self._on_setting_changed()
        )
        logo_pad_switch.pack(side="left")

        self.btn_color_logo_bg = customtkinter.CTkButton(
            logo_bg_frame, text="Logo BG Color", font=("Hanken Grotesk", 10), width=100, height=26,
            fg_color=self.logo_background_color, text_color="#000000" if self.logo_background_color=="#ffffff" else "#ffffff",
            command=lambda: self._choose_color("logobg")
        )
        self.btn_color_logo_bg.pack(side="right")

        # Grid de Sliders de Ajuste Fino (Module size, Logo size, Card corner radius)
        sliders_grid = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        sliders_grid.pack(fill="x", padx=12, pady=(0, 8))
        sliders_grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Module size slider
        mod_sz_lbl = customtkinter.CTkLabel(sliders_grid, text="Module size:", font=("Hanken Grotesk", 11))
        mod_sz_lbl.grid(row=0, column=0, sticky="w")
        mod_sz_slider = customtkinter.CTkSlider(
            sliders_grid, from_=0.5, to=1.0, variable=self.module_scale,
            button_color="#00f0ff", button_hover_color="#00dbe9", command=lambda val: self._on_setting_changed()
        )
        mod_sz_slider.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 4))

        # Logo size slider
        logo_sz_lbl = customtkinter.CTkLabel(sliders_grid, text="Logo size:", font=("Hanken Grotesk", 11))
        logo_sz_lbl.grid(row=0, column=1, sticky="w")
        logo_sz_slider = customtkinter.CTkSlider(
            sliders_grid, from_=0.05, to=0.35, variable=self.logo_ratio,
            button_color="#00f0ff", button_hover_color="#00dbe9", command=lambda val: self._on_setting_changed()
        )
        logo_sz_slider.grid(row=1, column=1, sticky="ew", padx=2, pady=(0, 4))

        # Card corner radius slider
        card_r_lbl = customtkinter.CTkLabel(sliders_grid, text="Card corner radius:", font=("Hanken Grotesk", 11))
        card_r_lbl.grid(row=0, column=2, sticky="w")
        card_r_slider = customtkinter.CTkSlider(
            sliders_grid, from_=0.0, to=20.0, variable=self.card_corner_radius,
            button_color="#00f0ff", button_hover_color="#00dbe9", command=lambda val: self._on_setting_changed()
        )
        card_r_slider.grid(row=1, column=2, sticky="ew", padx=2, pady=(0, 4))

        # Encabezado Superior (Add top heading)
        head_frame = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        head_frame.pack(fill="x", padx=12, pady=(8, 2))

        head_switch = customtkinter.CTkSwitch(
            head_frame, text="Add top heading", variable=self.use_top_heading,
            font=("Hanken Grotesk", 11, "bold"), progress_color="#00f0ff", command=lambda: self._on_setting_changed()
        )
        head_switch.pack(side="left")

        self.btn_color_head = customtkinter.CTkButton(
            head_frame, text="Heading Color", font=("Hanken Grotesk", 10), width=100, height=24,
            fg_color=self.top_heading_color, command=lambda: self._choose_color("head")
        )
        self.btn_color_head.pack(side="right")

        head_ctrl_grid = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        head_ctrl_grid.pack(fill="x", padx=12, pady=(0, 8))
        head_ctrl_grid.grid_columnconfigure(0, weight=3)
        head_ctrl_grid.grid_columnconfigure(1, weight=2)

        self.head_entry = customtkinter.CTkEntry(head_ctrl_grid, textvariable=self.top_heading_text, placeholder_text="Heading text...")
        self.head_entry.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.head_entry.bind("<KeyRelease>", lambda e: self._on_setting_changed())

        head_sz_slider = customtkinter.CTkSlider(
            head_ctrl_grid, from_=12, to=48, variable=self.top_heading_size,
            button_color="#00f0ff", command=lambda val: self._on_setting_changed()
        )
        head_sz_slider.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Leyenda Inferior (Add bottom caption)
        cap_frame = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        cap_frame.pack(fill="x", padx=12, pady=(6, 2))

        cap_switch = customtkinter.CTkSwitch(
            cap_frame, text="Add bottom caption", variable=self.use_bottom_caption,
            font=("Hanken Grotesk", 11, "bold"), progress_color="#00f0ff", command=lambda: self._on_setting_changed()
        )
        cap_switch.pack(side="left")

        self.btn_color_cap = customtkinter.CTkButton(
            cap_frame, text="Caption Color", font=("Hanken Grotesk", 10), width=100, height=24,
            fg_color=self.bottom_caption_color, command=lambda: self._choose_color("cap")
        )
        self.btn_color_cap.pack(side="right")

        cap_ctrl_grid = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        cap_ctrl_grid.pack(fill="x", padx=12, pady=(0, 12))
        cap_ctrl_grid.grid_columnconfigure(0, weight=3)
        cap_ctrl_grid.grid_columnconfigure(1, weight=2)

        self.cap_entry = customtkinter.CTkEntry(cap_ctrl_grid, textvariable=self.bottom_caption_text, placeholder_text="Caption text...")
        self.cap_entry.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.cap_entry.bind("<KeyRelease>", lambda e: self._on_setting_changed())

        cap_sz_slider = customtkinter.CTkSlider(
            cap_ctrl_grid, from_=12, to=48, variable=self.bottom_caption_size,
            button_color="#00f0ff", command=lambda val: self._on_setting_changed()
        )
        cap_sz_slider.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Selector de Tipo de Fuente (Font Family)
        font_fam_frame = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        font_fam_frame.pack(fill="x", padx=12, pady=(0, 10))

        font_fam_lbl = customtkinter.CTkLabel(font_fam_frame, text="Tipo de Fuente:", font=("Hanken Grotesk", 11, "bold"))
        font_fam_lbl.pack(side="left")

        font_fam_menu = customtkinter.CTkOptionMenu(
            font_fam_frame, values=["Sans-Serif", "Serif", "Monospace", "Trebuchet", "Impact", "Futura"],
            variable=self.font_family, fg_color="#282a2e", button_color="#333539", width=140,
            command=lambda val: self._on_setting_changed()
        )
        font_fam_menu.pack(side="right")

        # Fila de Tamaño / Padding / Damage recovery
        export_cfg_grid = customtkinter.CTkFrame(studio_frame, fg_color="transparent")
        export_cfg_grid.pack(fill="x", padx=12, pady=(0, 12))
        export_cfg_grid.grid_columnconfigure((0, 1), weight=1)

        res_lbl = customtkinter.CTkLabel(export_cfg_grid, text="Size (Resolución):", font=("Hanken Grotesk", 11))
        res_lbl.grid(row=0, column=0, sticky="w")
        res_menu = customtkinter.CTkOptionMenu(
            export_cfg_grid, values=["300px", "600px", "1200px", "2400px"], variable=self.target_resolution,
            fg_color="#282a2e", button_color="#333539", command=lambda val: self._on_setting_changed()
        )
        res_menu.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        pad_lbl = customtkinter.CTkLabel(export_cfg_grid, text="Padding (Margen px):", font=("Hanken Grotesk", 11))
        pad_lbl.grid(row=0, column=1, sticky="w")
        pad_slider = customtkinter.CTkSlider(
            export_cfg_grid, from_=0, to=80, variable=self.canvas_padding_px,
            button_color="#00f0ff", button_hover_color="#00dbe9", command=lambda val: self._on_setting_changed()
        )
        pad_slider.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        # Damage recovery (Nivel de Corrección de Errores)
        ec_lbl = customtkinter.CTkLabel(
            studio_frame, text="Damage recovery (Nivel de error):", font=("Hanken Grotesk", 11, "bold")
        )
        ec_lbl.pack(anchor="w", padx=12, pady=(4, 2))

        ec_seg = customtkinter.CTkSegmentedButton(
            studio_frame, values=["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
            variable=self.error_correction, selected_color="#00f0ff", selected_hover_color="#00dbe9",
            unselected_color="#282a2e", command=lambda val: self._on_setting_changed_ec(val)
        )
        ec_seg.pack(fill="x", padx=12, pady=(0, 16))

    def _build_preview_panel(self):
        """Construye el panel derecho con la vista previa en vivo y exportación"""
        self.preview_panel = customtkinter.CTkFrame(self, corner_radius=12, fg_color="#16191e")
        self.preview_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)

        # Titulo Vista Previa
        prev_title = customtkinter.CTkLabel(
            self.preview_panel, text="LIVE PREVIEW", font=("Geist", 12, "bold"), text_color="#00f0ff"
        )
        prev_title.pack(anchor="w", padx=16, pady=(16, 4))

        # Canvas Contenedor de la Imagen QR
        self.qr_card = customtkinter.CTkFrame(self.preview_panel, fg_color="#1e2024", corner_radius=12)
        self.qr_card.pack(fill="both", expand=True, padx=16, pady=8)

        self.qr_image_label = customtkinter.CTkLabel(self.qr_card, text="")
        self.qr_image_label.pack(expand=True, padx=20, pady=20)

        # Indicador de Escanabilidad y Contraste
        self.contrast_badge = customtkinter.CTkLabel(
            self.preview_panel, text="🟢 Excelente Escanabilidad (Contraste 21.0:1)",
            font=("Hanken Grotesk", 11, "bold"), text_color="#a7ffb3", fg_color="#1e2024", corner_radius=6, height=28
        )
        self.contrast_badge.pack(fill="x", padx=16, pady=(0, 12))

        # Panel de Acciones Rápidas
        actions_frame = customtkinter.CTkFrame(self.preview_panel, fg_color="transparent")
        actions_frame.pack(fill="x", padx=16, pady=(0, 16))

        copy_btn = customtkinter.CTkButton(
            actions_frame, text="📋 Copiar al Portapapeles", font=("Hanken Grotesk", 12, "bold"),
            height=40, fg_color="#282a2e", hover_color="#006970", text_color="#e2e2e8",
            command=self._copy_to_clipboard_action
        )
        copy_btn.pack(fill="x", pady=(0, 8))

        export_grid = customtkinter.CTkFrame(actions_frame, fg_color="transparent")
        export_grid.pack(fill="x")
        export_grid.grid_columnconfigure(0, weight=2)
        export_grid.grid_columnconfigure(1, weight=3)

        fmt_menu = customtkinter.CTkOptionMenu(
            export_grid, values=["PNG", "SVG", "PDF", "JPEG"], variable=self.export_format,
            height=40, fg_color="#282a2e", button_color="#333539"
        )
        fmt_menu.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        save_btn = customtkinter.CTkButton(
            export_grid, text="💾 Guardar QR", font=("Hanken Grotesk", 13, "bold"),
            height=40, fg_color="#00f0ff", hover_color="#00dbe9", text_color="#002022",
            command=self._save_qr_action
        )
        save_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")

    # -----------------------------------------------------------------
    # CONTROL DE PESTAÑAS Y FORMULARIO DINÁMICO
    # -----------------------------------------------------------------
    def _switch_payload_tab(self, payload_type):
        self.current_payload_type = payload_type

        # Actualizar resaltado de botones
        for pt, btn in self.payload_btn_dict.items():
            if pt == payload_type:
                btn.configure(fg_color="#00f0ff", text_color="#002022")
            else:
                btn.configure(fg_color="#282a2e", text_color="#e2e2e8")

        # Limpiar formulario anterior
        for widget in self.payload_form_frame.winfo_children():
            widget.destroy()

        # Generar campos según el tipo
        if payload_type == "URL":
            self._add_form_entry("URL del sitio web:", "url", "https://ejemplo.com")
        elif payload_type == "WhatsApp":
            self._add_form_entry("Número de teléfono (con código país):", "phone", "+5215512345678")
            self._add_form_textbox("Mensaje predeterminado:", "message", "¡Hola! Quisiera más información.")
        elif payload_type == "Wi-Fi":
            self._add_form_entry("Nombre de la red (SSID):", "ssid", "MiRedWiFi")
            self._add_form_entry("Contraseña:", "password", "ClaveSecreta123", show="*")
            self.form_sec = customtkinter.CTkOptionMenu(
                self.payload_form_frame, values=["WPA/WPA2", "WEP", "Sin Clave (Ninguna)"],
                command=lambda val: self._render_qr_preview()
            )
            self.form_sec.pack(fill="x", padx=12, pady=4)
        elif payload_type == "vCard":
            self._add_form_entry("Nombre:", "first_name", "Juan")
            self._add_form_entry("Apellido:", "last_name", "Pérez")
            self._add_form_entry("Empresa / Organización:", "org", "Empresa S.A.")
            self._add_form_entry("Teléfono Móvil:", "phone", "+5215512345678")
            self._add_form_entry("Correo Electrónico:", "email", "juan@empresa.com")
        elif payload_type == "Email":
            self._add_form_entry("Destinatario:", "to", "contacto@empresa.com")
            self._add_form_entry("Asunto:", "subject", "Consulta sobre servicios")
            self._add_form_textbox("Mensaje:", "body", "Hola, me gustaría recibir cotización...")
        elif payload_type == "SMS":
            self._add_form_entry("Número de teléfono:", "phone", "+5215512345678")
            self._add_form_textbox("Mensaje SMS:", "message", "Hola!")
        elif payload_type == "Phone":
            self._add_form_entry("Número de teléfono:", "phone", "+5215512345678")
        elif payload_type == "Geo":
            self._add_form_entry("Latitud:", "lat", "19.432608")
            self._add_form_entry("Longitud:", "lng", "-99.133209")
        elif payload_type == "Text":
            self._add_form_textbox("Texto libre:", "text", "Escribe cualquier información aquí...")
        elif payload_type == "Calendar":
            self._add_form_entry("Título del evento:", "title", "Reunión de Proyecto")
            self._add_form_entry("Ubicación:", "location", "Oficina Central")
            self._add_form_entry("Inicio (YYYY-MM-DD THH:MM):", "start", "2026-09-01T10:00")
            self._add_form_entry("Fin (YYYY-MM-DD THH:MM):", "end", "2026-09-01T11:00")
        elif payload_type == "Bitcoin":
            self._add_form_entry("Dirección Wallet Bitcoin:", "address", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
            self._add_form_entry("Monto (BTC):", "amount", "0.005")
        elif payload_type == "Bulk":
            lbl = customtkinter.CTkLabel(self.payload_form_frame, text="Ingresa un ítem por línea (URLs o texto):", font=("Hanken Grotesk", 11, "bold"))
            lbl.pack(anchor="w", padx=12, pady=(8, 2))
            self.form_entries = {}
            txt_box = customtkinter.CTkTextbox(self.payload_form_frame, height=100)
            txt_box.insert("1.0", "https://ejemplo.com/1\nhttps://ejemplo.com/2\nhttps://ejemplo.com/3")
            txt_box.pack(fill="x", padx=12, pady=4)
            self.form_entries["bulk_text"] = txt_box
            txt_box.bind("<KeyRelease>", lambda e: self._render_qr_preview())

        self._render_qr_preview()

    def _add_form_entry(self, label_txt, key, placeholder="", show=None):
        if not hasattr(self, "form_entries"):
            self.form_entries = {}
        lbl = customtkinter.CTkLabel(self.payload_form_frame, text=label_txt, font=("Hanken Grotesk", 11, "bold"))
        lbl.pack(anchor="w", padx=12, pady=(6, 2))
        entry = customtkinter.CTkEntry(self.payload_form_frame, placeholder_text=placeholder, show=show)
        entry.pack(fill="x", padx=12, pady=(0, 4))
        entry.insert(0, placeholder)
        entry.bind("<KeyRelease>", lambda e: self._render_qr_preview())
        self.form_entries[key] = entry

    def _add_form_textbox(self, label_txt, key, placeholder=""):
        if not hasattr(self, "form_entries"):
            self.form_entries = {}
        lbl = customtkinter.CTkLabel(self.payload_form_frame, text=label_txt, font=("Hanken Grotesk", 11, "bold"))
        lbl.pack(anchor="w", padx=12, pady=(6, 2))
        txt = customtkinter.CTkTextbox(self.payload_form_frame, height=60)
        txt.insert("1.0", placeholder)
        txt.pack(fill="x", padx=12, pady=(0, 4))
        txt.bind("<KeyRelease>", lambda e: self._render_qr_preview())
        self.form_entries[key] = txt

    # -----------------------------------------------------------------
    # LÓGICA DE RENDERIZADO Y PRESET
    # -----------------------------------------------------------------
    def _get_current_payload_string(self) -> str:
        """Extrae la cadena formateada de la pestaña activa"""
        pt = self.current_payload_type
        fe = getattr(self, "form_entries", {})

        def get_val(key):
            widget = fe.get(key)
            if not widget: return ""
            if isinstance(widget, customtkinter.CTkTextbox):
                return widget.get("1.0", "end-1c").strip()
            return widget.get().strip()

        if pt == "URL": return payloads.format_url(get_val("url"))
        if pt == "WhatsApp": return payloads.format_whatsapp(get_val("phone"), get_val("message"))
        if pt == "Wi-Fi":
            sec = getattr(self, "form_sec", None)
            sec_val = sec.get() if sec else "WPA"
            return payloads.format_wifi(get_val("ssid"), get_val("password"), sec_val)
        if pt == "vCard": return payloads.format_vcard(get_val("first_name"), get_val("last_name"), get_val("org"), get_val("phone"), get_val("email"))
        if pt == "Email": return payloads.format_email(get_val("to"), get_val("subject"), get_val("body"))
        if pt == "SMS": return payloads.format_sms(get_val("phone"), get_val("message"))
        if pt == "Phone": return payloads.format_phone(get_val("phone"))
        if pt == "Geo": return payloads.format_geo(get_val("lat"), get_val("lng"))
        if pt == "Text": return payloads.format_text(get_val("text"))
        if pt == "Calendar": return payloads.format_vcalendar(get_val("title"), get_val("location"), get_val("start"), get_val("end"))
        if pt == "Bitcoin": return payloads.format_bitcoin(get_val("address"), get_val("amount"))
        if pt == "Bulk":
            lines = get_val("bulk_text").split("\n")
            return lines[0] if lines else "https://homielab.com"
        return "https://homielab.com"

    def _render_qr_preview(self):
        """Genera el QR y actualiza la vista previa"""
        data_str = self._get_current_payload_string()
        ec_val = self.error_correction.get().split()[0] # Extraer L, M, Q o H
        try:
            res_px = int(self.target_resolution.get().replace("px", ""))
        except Exception:
            res_px = 1200

        top_txt = self.top_heading_text.get().strip() if self.use_top_heading.get() else ""
        bot_txt = self.bottom_caption_text.get().strip() if self.use_bottom_caption.get() else ""

        self.current_qr_img = qrDinamico.makeQRDinamico(
            data=data_str,
            logo_path=self.logo_path,
            back_color=self.back_color,
            module_color=self.module_color,
            finder_frame_color=self.finder_frame_color,
            finder_center_color=self.finder_center_color,
            logo_background_color=self.logo_background_color,
            module_shape=self.module_shape.get(),
            finder_frame_shape=self.finder_frame_shape.get(),
            finder_center_shape=self.finder_center_shape.get(),
            error_correction=ec_val,
            logo_ratio=self.logo_ratio.get(),
            logo_background_pad=self.logo_background_pad.get(),
            module_scale=self.module_scale.get(),
            card_corner_radius=self.card_corner_radius.get(),
            top_heading=top_txt,
            top_heading_color=self.top_heading_color,
            top_heading_size=self.top_heading_size.get(),
            bottom_caption=bot_txt,
            bottom_caption_color=self.bottom_caption_color,
            bottom_caption_size=self.bottom_caption_size.get(),
            font_family=self.font_family.get(),
            target_resolution=res_px,
            canvas_padding_px=self.canvas_padding_px.get()
        )

        # Actualizar Vista Previa CTkImage usando BICUBIC para eliminar destellos/líneas de antialiasing
        preview_pil = self.current_qr_img.resize((320, 320), Image.Resampling.BICUBIC)
        ctk_qr = customtkinter.CTkImage(light_image=preview_pil, dark_image=preview_pil, size=(320, 320))
        self.qr_image_label.configure(image=ctk_qr)

        # Calcular contraste WCAG
        m_rgb = qrDinamico.hex_to_rgb(self.module_color)
        b_rgb = qrDinamico.hex_to_rgb(self.back_color)
        ratio = qrDinamico.calculate_contrast_ratio(m_rgb, b_rgb)

        if ratio >= 3.0:
            self.contrast_badge.configure(
                text=f"🟢 Excelente Escanabilidad (Contraste {ratio:.1f}:1)", text_color="#a7ffb3"
            )
        else:
            self.contrast_badge.configure(
                text=f"⚠️ Bajo Contraste ({ratio:.1f}:1) - Podría ser difícil de leer", text_color="#ffb4ab"
            )

    def _on_setting_changed(self):
        self._render_qr_preview()

    def _on_setting_changed_ec(self, val):
        self._render_qr_preview()

    def _choose_color(self, target):
        color = colorchooser.askcolor(title="Selecciona un color")
        if color[1]:
            hex_c = color[1]
            if target == "module":
                self.module_color = hex_c
                self.btn_color_mod.configure(fg_color=hex_c)
            elif target == "back":
                self.back_color = hex_c
                self.btn_color_bg.configure(fg_color=hex_c, text_color="#000000" if hex_c=="#ffffff" else "#ffffff")
            elif target == "fframe":
                self.finder_frame_color = hex_c
                self.btn_color_ff.configure(fg_color=hex_c)
            elif target == "fcenter":
                self.finder_center_color = hex_c
                self.btn_color_fc.configure(fg_color=hex_c)
            elif target == "logobg":
                self.logo_background_color = hex_c
                if hasattr(self, "btn_color_logo_bg"):
                    self.btn_color_logo_bg.configure(fg_color=hex_c, text_color="#000000" if hex_c=="#ffffff" else "#ffffff")
            elif target == "head":
                self.top_heading_color = hex_c
                if hasattr(self, "btn_color_head"):
                    self.btn_color_head.configure(fg_color=hex_c)
            elif target == "cap":
                self.bottom_caption_color = hex_c
                if hasattr(self, "btn_color_cap"):
                    self.btn_color_cap.configure(fg_color=hex_c)
            self._render_qr_preview()

    def _apply_preset_theme(self, name):
        p = PRESET_THEMES.get(name)
        if not p: return
        self.module_color = p["module"]
        self.back_color = p["back"]
        self.finder_frame_color = p["fframe"]
        self.finder_center_color = p["fcenter"]

        self.module_shape.set(p["mshape"])
        self.finder_frame_shape.set(p["ffshape"])
        self.finder_center_shape.set(p["fcshape"])

        self.btn_color_mod.configure(fg_color=self.module_color)
        self.btn_color_bg.configure(fg_color=self.back_color, text_color="#000000" if self.back_color=="#ffffff" else "#ffffff")
        self.btn_color_ff.configure(fg_color=self.finder_frame_color)
        self.btn_color_fc.configure(fg_color=self.finder_center_color)

        self._render_qr_preview()

    def _upload_custom_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.svg")])
        if path:
            self.logo_path = path
            self._render_qr_preview()

    def _set_brand_logo(self, path):
        self.logo_path = path
        self._render_qr_preview()

    def _remove_logo(self):
        self.logo_path = None
        self._render_qr_preview()

    def _copy_to_clipboard_action(self):
        if self.current_qr_img:
            success = qrDinamico.copy_image_to_clipboard(self.current_qr_img)
            if success:
                messagebox.showinfo("QR Studio Pro", "¡Imagen copiada al portapapeles con éxito!")
            else:
                messagebox.showerror("QR Studio Pro", "Error al copiar la imagen al portapapeles.")

    def _save_qr_action(self):
        fmt = self.export_format.get().upper()
        data_str = self._get_current_payload_string()

        # Si es formato Masivo (Bulk)
        if self.current_payload_type == "Bulk":
            dir_path = filedialog.askdirectory(title="Selecciona la carpeta para exportar el lote de QRs")
            if dir_path:
                fe = getattr(self, "form_entries", {})
                txt_widget = fe.get("bulk_text")
                if txt_widget:
                    lines = [l.strip() for l in txt_widget.get("1.0", "end-1c").split("\n") if l.strip()]
                    ec_val = self.error_correction.get().split()[0]
                    for idx, line in enumerate(lines, 1):
                        q_img = qrDinamico.makeQRDinamico(
                            data=line, logo_path=self.logo_path, back_color=self.back_color,
                            module_color=self.module_color, finder_frame_color=self.finder_frame_color,
                            finder_center_color=self.finder_center_color, module_shape=self.module_shape.get(),
                            finder_frame_shape=self.finder_frame_shape.get(), finder_center_shape=self.finder_center_shape.get(),
                            error_correction=ec_val, logo_ratio=self.logo_ratio.get()
                        )
                        q_img.save(os.path.join(dir_path, f"qr_bulk_{idx}.png"))
                    messagebox.showinfo("QR Studio Pro", f"¡Lote de {len(lines)} códigos QR exportado exitosamente!")
            return

        # Exportación individual
        ext_map = {"PNG": ".png", "JPEG": ".jpg", "SVG": ".svg", "PDF": ".pdf"}
        ext = ext_map.get(fmt, ".png")
        save_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[(f"{fmt} File", f"*{ext}"), ("All Files", "*.*")],
            title=f"Guardar Código QR en formato {fmt}"
        )
        if save_path:
            if fmt == "SVG":
                qrDinamico.save_qr_as_svg(data_str, save_path, self.back_color, self.module_color)
            elif fmt == "PDF":
                self.current_qr_img.convert("RGB").save(save_path, "PDF", resolution=300.0)
            elif fmt == "JPEG":
                self.current_qr_img.convert("RGB").save(save_path, "JPEG", quality=95)
            else: # PNG
                self.current_qr_img.save(save_path, "PNG")
            messagebox.showinfo("QR Studio Pro", f"Código QR guardado exitosamente en:\n{save_path}")

if __name__ == "__main__":
    app = QRStudioApp()
    app.mainloop()
