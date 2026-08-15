import urllib.parse

def clean_phone_number(phone: str) -> str:
    """Limpia caracteres no numéricos excepto el signo +"""
    if not phone:
        return ""
    clean = "".join(c for c in phone if c.isdigit() or c == '+')
    return clean

def format_url(url: str) -> str:
    """Formatea una URL asegurando el esquema http/https"""
    if not url:
        return ""
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    return url

def format_whatsapp(phone: str, message: str = "") -> str:
    """Genera enlace oficial de WhatsApp wa.me con mensaje codificado"""
    phone_clean = clean_phone_number(phone).lstrip('+')
    if not phone_clean:
        return ""
    if message:
        encoded_msg = urllib.parse.quote(message)
        return f"https://wa.me/{phone_clean}?text={encoded_msg}"
    return f"https://wa.me/{phone_clean}"

def format_email(to: str, subject: str = "", body: str = "") -> str:
    """Genera URI mailto:"""
    if not to:
        return ""
    params = []
    if subject:
        params.append(f"subject={urllib.parse.quote(subject)}")
    if body:
        params.append(f"body={urllib.parse.quote(body)}")
    query = "&".join(params)
    return f"mailto:{to.strip()}?{query}" if query else f"mailto:{to.strip()}"

def format_phone(phone: str) -> str:
    """Genera URI tel:"""
    clean = clean_phone_number(phone)
    return f"tel:{clean}" if clean else ""

def format_sms(phone: str, message: str = "") -> str:
    """Genera cadena SMSTO:"""
    clean = clean_phone_number(phone)
    if not clean:
        return ""
    return f"smsto:{clean}:{message}"

def format_geo(lat: str, lng: str) -> str:
    """Genera URI geo:lat,lng"""
    lat = lat.strip()
    lng = lng.strip()
    if not lat or not lng:
        return ""
    return f"geo:{lat},{lng}"

def format_text(text: str) -> str:
    """Retorna texto plano"""
    return text if text else ""

def format_wifi(ssid: str, password: str = "", security: str = "WPA", hidden: bool = False) -> str:
    """Genera cadena estándar WIFI:S:<ssid>;T:<security>;P:<password>;H:<hidden>;;"""
    if not ssid:
        return ""
    sec = security.upper() if security else "NOPASS"
    if sec == "NONE":
        sec = "NOPASS"
    h_str = "true" if hidden else "false"

    def escape_wifi(val: str) -> str:
        for char in ['\\', ';', ',', ':', '"']:
            val = val.replace(char, f'\\{char}')
        return val

    e_ssid = escape_wifi(ssid)
    e_pass = escape_wifi(password)
    return f"WIFI:S:{e_ssid};T:{sec};P:{e_pass};H:{h_str};;"

def format_vcard(first_name: str, last_name: str = "", org: str = "", phone: str = "", email: str = "", url: str = "") -> str:
    """Genera ficha de contacto en formato vCard 3.0"""
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{last_name.strip()};{first_name.strip()};;;",
        f"FN:{first_name.strip()} {last_name.strip()}".strip(),
    ]
    if org:
        lines.append(f"ORG:{org.strip()}")
    if phone:
        lines.append(f"TEL;TYPE=CELL:{clean_phone_number(phone)}")
    if email:
        lines.append(f"EMAIL:{email.strip()}")
    if url:
        lines.append(f"URL:{format_url(url)}")
    lines.append("END:VCARD")
    return "\n".join(lines)

def format_vcalendar(title: str, location: str = "", start_iso: str = "", end_iso: str = "") -> str:
    """Genera evento vCalendar vEvent"""
    if not title:
        return ""
    lines = [
        "BEGIN:VEVENT",
        f"SUMMARY:{title.strip()}"
    ]
    if location:
        lines.append(f"LOCATION:{location.strip()}")
    if start_iso:
        clean_start = start_iso.replace("-", "").replace(":", "").replace(" ", "T")
        lines.append(f"DTSTART:{clean_start}")
    if end_iso:
        clean_end = end_iso.replace("-", "").replace(":", "").replace(" ", "T")
        lines.append(f"DTEND:{clean_end}")
    lines.append("END:VEVENT")
    return "\n".join(lines)

def format_bitcoin(address: str, amount: str = "", label: str = "") -> str:
    """Genera URI bitcoin:"""
    if not address:
        return ""
    params = []
    if amount:
        params.append(f"amount={amount.strip()}")
    if label:
        params.append(f"label={urllib.parse.quote(label.strip())}")
    query = "&".join(params)
    return f"bitcoin:{address.strip()}?{query}" if query else f"bitcoin:{address.strip()}"
