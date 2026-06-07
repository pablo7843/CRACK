"""
Internationalization (i18n) module.
Supports English (en) and Spanish (es).
Auto-detects from system locale; override with set_lang().
"""
import locale

_current_lang = "en"

STRINGS = {
    "en": {
        # Banner / disclaimer
        "disclaimer": "  [!] Educational / CTF use only. Never attack without authorization.",

        # Auto-detection
        "auto_detected": "Auto-detected: [bold]{}[/]",
        "hash_could_be": "Hash could be: {}. Use --algo to specify.",

        # Attack headers
        "dict_attack_header": "Dictionary attack",
        "brute_attack_header": "Brute force",
        "rules_label": "Rules",
        "algo_label": "algo",
        "wordlist_label": "wordlist",
        "charset_label": "charset",
        "len_label": "len",

        # Progress line
        "progress_fmt": "{} attempts | {} H/s | last: {}",

        # Result panel
        "cracked_title": "SUCCESS",
        "failed_title": "FAILED",
        "cracked_msg": "PASSWORD CRACKED!",
        "not_found_msg": "NOT FOUND",
        "label_plaintext": "Plaintext",
        "label_algorithm": "Algorithm",
        "label_attempts": "Attempts",
        "label_time": "Time",
        "label_speed": "Speed",
        "attack_type_dict": "dictionary",
        "attack_type_brute": "brute force",

        # Info table
        "info_title": "Hashing Algorithm Security Overview",
        "col_algorithm": "Algorithm",
        "col_bits": "Bits",
        "col_year": "Year",
        "col_broken": "Broken?",
        "col_hashcat_mode": "Hashcat Mode",
        "col_notes": "Notes",
        "yes": "YES",
        "no": "NO",

        # Hashcat hint panel
        "hashcat_title": "Hashcat Commands",
        "hashcat_dict": "# Dictionary attack",
        "hashcat_rules": "# + best64 rules (mutations)",
        "hashcat_brute": "# Brute force up to 8 chars",
        "hashcat_gpu_note": "GPU: RTX 4090 -> ~65B MD5/s, ~20 bcrypt/s (cost=12)",

        # Keyspace table
        "keyspace_title": "Brute Force Keyspace",
        "keyspace_charset": "Charset",
        "keyspace_range": "Length range",
        "keyspace_total": "Total candidates",
        "keyspace_eta": "Est. @ 1M H/s",

        # Credential stuffing demo
        "stuffing_title": "=== CREDENTIAL STUFFING DEMO ===",
        "stuffing_scenario": (
            "Scenario: 'ServiceA' DB leaked. Attacker obtained plaintext passwords.\n"
            "Now testing them against 'ServiceB' which stores SHA-256 hashes."
        ),
        "stuffing_hashes_label": "ServiceB hashes (SHA-256):",
        "stuffing_running": "Running credential stuffing attack...",
        "stuffing_defend": "How to defend:",
        "stuffing_compromised": "Credential stuffing: {}/{} accounts compromised",
        "stuffing_none": "No accounts compromised (passwords not reused).",
        "col_username": "Username",
        "col_reused_pw": "Reused Password",

        # Defense table
        "defense_title": "Defense Strategies",
        "col_strategy": "Strategy",
        "col_impact": "Impact",
        "col_details": "Details",

        # Impact labels
        "impact_Critical": "Critical",
        "impact_High": "High",
        "impact_Medium": "Medium",

        # Batch mode
        "batch_cracking": "Cracking {} hashes from {}",
        "hash_n_of_m": "Hash {}/{}:",

        # Errors
        "err_hash_file_not_found": "Hash file not found: {}",
        "err_generic": "Error: {}",
        "err_bcrypt_brute": "Brute force against bcrypt is not practical — use dictionary attack.",

        # Algorithm notes (used in --info table)
        "algo_note_MD5": (
            "Collision attacks found 1996, fully broken 2004. "
            "GPU can crack ~50 billion MD5/s. Never use for passwords."
        ),
        "algo_note_SHA-1": (
            "Google SHAttered (2017) proved practical collisions for $110k. "
            "GPU ~10 billion SHA-1/s. Deprecated by NIST."
        ),
        "algo_note_SHA-256": (
            "SHA-2 family. Cryptographically secure but NO salt. "
            "Vulnerable to rainbow tables + GPU attacks. Not for passwords."
        ),
        "algo_note_SHA-512": (
            "Stronger SHA-2 variant. Still no built-in salt or work factor. "
            "Prefer bcrypt/Argon2 for passwords."
        ),
        "algo_note_bcrypt": (
            "Built-in salt + configurable work factor (cost). "
            "~20 bcrypt/s on GPU at cost=12. Designed for passwords - use it."
        ),
        "algo_note_Argon2id": (
            "Winner of Password Hashing Competition 2015. "
            "Memory-hard - defeats GPU/ASIC attacks. Current best practice."
        ),

        # Defense strategy entries (name + detail, indexed)
        "defense_0_name": "Password Hashing (Argon2id / bcrypt)",
        "defense_0_detail": (
            "Slow-by-design algorithms make GPU cracking impractical. "
            "Even if DB leaks, plaintext recovery is expensive."
        ),
        "defense_1_name": "Multi-Factor Authentication (MFA)",
        "defense_1_detail": "Correct credentials alone not enough. OTP/FIDO2 required.",
        "defense_2_name": "Rate Limiting + Lockout",
        "defense_2_detail": "Limit failed attempts per IP/account. Block after N failures.",
        "defense_3_name": "HaveIBeenPwned check at registration",
        "defense_3_detail": (
            "Reject passwords found in known breach datasets. "
            "HIBP k-anonymity API: send first 5 chars of SHA-1 only."
        ),
        "defense_4_name": "CAPTCHA on login",
        "defense_4_detail": "Stops automated stuffing bots without human interaction.",
        "defense_5_name": "Device Fingerprinting",
        "defense_5_detail": "Flag logins from unknown devices/IPs even with correct credentials.",
        "defense_6_name": "Unique salts per password",
        "defense_6_detail": (
            "Rainbow table attacks fail. Each password needs individual cracking. "
            "bcrypt/Argon2 handle this automatically."
        ),

        # Interactive mode
        "menu_title": "What do you want to do?",
        "menu_crack_hash": "Crack a single hash",
        "menu_crack_file": "Crack a hash file (multiple hashes)",
        "menu_stuffing": "Credential stuffing demo",
        "menu_algo_info": "View algorithm info table",
        "menu_exit": "Exit",
        "prompt_hash": "Enter the hash to crack:",
        "prompt_algo": "Select algorithm:",
        "prompt_algo_auto": "Auto-detect",
        "prompt_attack": "Select attack mode:",
        "prompt_attack_dict": "Dictionary attack (wordlist)",
        "prompt_attack_brute": "Brute force (exhaustive enumeration)",
        "prompt_wordlist": "Wordlist path:",
        "prompt_rules": "Apply mutation rules:",
        "prompt_rules_none": "None (no mutations)",
        "prompt_charset": "Select character set:",
        "prompt_min_len": "Minimum password length:",
        "prompt_max_len": "Maximum password length:",
        "prompt_hashcat": "Show equivalent hashcat commands?",
        "prompt_hash_file": "Hash file path:",
        "prompt_another": "Crack another hash?",
        "err_empty_hash": "Hash cannot be empty.",
        "err_file_missing": "File not found: {}",
        "err_invalid_number": "Must be a positive integer.",
        "interactive_goodbye": "Goodbye!",
        "interactive_cancelled": "Cancelled.",
        "menu_gen_hash": "Generate hashes from a password",
        "menu_hashcat_cmds": "Show hashcat commands for a hash",
        "menu_keyspace": "Keyspace estimator (brute force)",
        "menu_change_lang": "Change language",
        "prompt_password": "Password to hash:",
        "prompt_algo_all": "All algorithms",
        "prompt_save_to_file": "Save to file? (leave empty to skip):",
        "prompt_wordlist_name": "Wordlist name (for hashcat command):",
        "prompt_quiet": "Suppress progress output?",
        "prompt_lang_select": "Select language:",
        "lang_changed_to_en": "Language changed to: English",
        "lang_changed_to_es": "Idioma cambiado a: Español",
    },

    "es": {
        # Banner / disclaimer
        "disclaimer": "  [!] Solo uso educativo / CTF. Nunca atacar sin autorizacion.",

        # Auto-detection
        "auto_detected": "Auto-detectado: [bold]{}[/]",
        "hash_could_be": "El hash podria ser: {}. Usa --algo para especificar.",

        # Attack headers
        "dict_attack_header": "Ataque de diccionario",
        "brute_attack_header": "Fuerza bruta",
        "rules_label": "Reglas",
        "algo_label": "algo",
        "wordlist_label": "wordlist",
        "charset_label": "charset",
        "len_label": "longitud",

        # Progress line
        "progress_fmt": "{} intentos | {} H/s | ultimo: {}",

        # Result panel
        "cracked_title": "EXITO",
        "failed_title": "FALLIDO",
        "cracked_msg": "CONTRASEÑA CRACKEADA!",
        "not_found_msg": "NO ENCONTRADA",
        "label_plaintext": "Texto plano",
        "label_algorithm": "Algoritmo",
        "label_attempts": "Intentos",
        "label_time": "Tiempo",
        "label_speed": "Velocidad",
        "attack_type_dict": "diccionario",
        "attack_type_brute": "fuerza bruta",

        # Info table
        "info_title": "Resumen de Seguridad de Algoritmos Hash",
        "col_algorithm": "Algoritmo",
        "col_bits": "Bits",
        "col_year": "Año",
        "col_broken": "Roto?",
        "col_hashcat_mode": "Modo Hashcat",
        "col_notes": "Notas",
        "yes": "SI",
        "no": "NO",

        # Hashcat hint panel
        "hashcat_title": "Comandos Hashcat",
        "hashcat_dict": "# Ataque de diccionario",
        "hashcat_rules": "# + reglas best64 (mutaciones)",
        "hashcat_brute": "# Fuerza bruta hasta 8 caracteres",
        "hashcat_gpu_note": "GPU: RTX 4090 -> ~65B MD5/s, ~20 bcrypt/s (coste=12)",

        # Keyspace table
        "keyspace_title": "Espacio de Busqueda (Fuerza Bruta)",
        "keyspace_charset": "Charset",
        "keyspace_range": "Rango de longitud",
        "keyspace_total": "Total de candidatos",
        "keyspace_eta": "Est. @ 1M H/s",

        # Credential stuffing demo
        "stuffing_title": "=== DEMO: CREDENTIAL STUFFING ===",
        "stuffing_scenario": (
            "Escenario: La BD de 'ServicioA' fue filtrada. El atacante obtuvo contraseñas en texto plano.\n"
            "Ahora las prueba contra 'ServicioB' que guarda hashes SHA-256."
        ),
        "stuffing_hashes_label": "Hashes de ServicioB (SHA-256):",
        "stuffing_running": "Ejecutando ataque de credential stuffing...",
        "stuffing_defend": "Como defenderse:",
        "stuffing_compromised": "Credential stuffing: {}/{} cuentas comprometidas",
        "stuffing_none": "Ninguna cuenta comprometida (contraseñas no reutilizadas).",
        "col_username": "Usuario",
        "col_reused_pw": "Contraseña Reutilizada",

        # Defense table
        "defense_title": "Estrategias de Defensa",
        "col_strategy": "Estrategia",
        "col_impact": "Impacto",
        "col_details": "Detalles",

        # Impact labels
        "impact_Critical": "Critico",
        "impact_High": "Alto",
        "impact_Medium": "Medio",

        # Batch mode
        "batch_cracking": "Crackeando {} hashes desde {}",
        "hash_n_of_m": "Hash {}/{}:",

        # Errors
        "err_hash_file_not_found": "Archivo de hashes no encontrado: {}",
        "err_generic": "Error: {}",
        "err_bcrypt_brute": "Fuerza bruta contra bcrypt no es practico — usa ataque de diccionario.",

        # Algorithm notes
        "algo_note_MD5": (
            "Ataques de colision hallados en 1996, completamente roto en 2004. "
            "GPU puede crackear ~50 mil millones de MD5/s. Nunca usar para contraseñas."
        ),
        "algo_note_SHA-1": (
            "Google SHAttered (2017) demostro colisiones practicas por $110k. "
            "GPU ~10 mil millones SHA-1/s. Obsoleto segun NIST."
        ),
        "algo_note_SHA-256": (
            "Familia SHA-2. Criptograficamente seguro pero SIN salt. "
            "Vulnerable a rainbow tables + ataques GPU. No usar para contraseñas."
        ),
        "algo_note_SHA-512": (
            "Variante SHA-2 mas fuerte. Sin salt ni factor de trabajo integrado. "
            "Preferir bcrypt/Argon2 para contraseñas."
        ),
        "algo_note_bcrypt": (
            "Salt integrado + factor de trabajo configurable (coste). "
            "~20 bcrypt/s en GPU con coste=12. Diseñado para contraseñas - usalo."
        ),
        "algo_note_Argon2id": (
            "Ganador de la Password Hashing Competition 2015. "
            "Memory-hard - derrota ataques GPU/ASIC. Mejor practica actual."
        ),

        # Defense strategy entries
        "defense_0_name": "Hashing de Contraseñas (Argon2id / bcrypt)",
        "defense_0_detail": (
            "Algoritmos lentos por diseño hacen el crackeo GPU impractico. "
            "Aunque la BD se filtre, recuperar el texto plano es muy costoso."
        ),
        "defense_1_name": "Autenticacion Multi-Factor (MFA)",
        "defense_1_detail": "Las credenciales correctas solas no son suficientes. Se requiere OTP/FIDO2.",
        "defense_2_name": "Limitacion de tasa + Bloqueo",
        "defense_2_detail": "Limitar intentos fallidos por IP/cuenta. Bloquear tras N fallos.",
        "defense_3_name": "Verificacion HaveIBeenPwned al registro",
        "defense_3_detail": (
            "Rechazar contraseñas encontradas en filtraciones conocidas. "
            "API k-anonimato HIBP: enviar solo los primeros 5 chars del SHA-1."
        ),
        "defense_4_name": "CAPTCHA en el login",
        "defense_4_detail": "Detiene bots de stuffing automatizado sin interaccion humana.",
        "defense_5_name": "Huella digital del dispositivo",
        "defense_5_detail": "Marcar logins desde dispositivos/IPs desconocidos aunque las credenciales sean correctas.",
        "defense_6_name": "Salt unico por contraseña",
        "defense_6_detail": (
            "Los ataques de rainbow table fallan. Cada contraseña necesita cracking individual. "
            "bcrypt/Argon2 lo gestionan automaticamente."
        ),

        # Interactive mode
        "menu_title": "Que deseas hacer?",
        "menu_crack_hash": "Crackear un hash",
        "menu_crack_file": "Crackear archivo de hashes (multiples)",
        "menu_stuffing": "Demo credential stuffing",
        "menu_algo_info": "Ver tabla de algoritmos",
        "menu_exit": "Salir",
        "prompt_hash": "Introduce el hash a crackear:",
        "prompt_algo": "Selecciona el algoritmo:",
        "prompt_algo_auto": "Auto-detectar",
        "prompt_attack": "Selecciona el modo de ataque:",
        "prompt_attack_dict": "Ataque de diccionario (wordlist)",
        "prompt_attack_brute": "Fuerza bruta (enumeracion exhaustiva)",
        "prompt_wordlist": "Ruta del wordlist:",
        "prompt_rules": "Aplicar reglas de mutacion:",
        "prompt_rules_none": "Ninguna (sin mutaciones)",
        "prompt_charset": "Selecciona el charset:",
        "prompt_min_len": "Longitud minima de contraseña:",
        "prompt_max_len": "Longitud maxima de contraseña:",
        "prompt_hashcat": "Mostrar comandos hashcat equivalentes?",
        "prompt_hash_file": "Ruta del archivo de hashes:",
        "prompt_another": "Crackear otro hash?",
        "err_empty_hash": "El hash no puede estar vacio.",
        "err_file_missing": "Archivo no encontrado: {}",
        "err_invalid_number": "Debe ser un numero entero positivo.",
        "interactive_goodbye": "Hasta luego!",
        "interactive_cancelled": "Cancelado.",
        "menu_gen_hash": "Generar hashes de una contraseña",
        "menu_hashcat_cmds": "Ver comandos hashcat para un hash",
        "menu_keyspace": "Estimador de keyspace (fuerza bruta)",
        "menu_change_lang": "Cambiar idioma",
        "prompt_password": "Contraseña a hashear:",
        "prompt_algo_all": "Todos los algoritmos",
        "prompt_save_to_file": "Guardar en archivo? (vacio para omitir):",
        "prompt_wordlist_name": "Nombre del wordlist (para comando hashcat):",
        "prompt_quiet": "Suprimir progreso en pantalla?",
        "prompt_lang_select": "Selecciona el idioma:",
        "lang_changed_to_en": "Language changed to: English",
        "lang_changed_to_es": "Idioma cambiado a: Español",
    },
}


def detect_lang() -> str:
    """Detect language from system locale or env vars. Falls back to 'en'."""
    import os
    # Check environment variables (work on all platforms)
    for var in ("LANGUAGE", "LANG", "LC_ALL", "LC_MESSAGES"):
        val = os.environ.get(var, "")
        if val.lower().startswith("es"):
            return "es"
    # locale.getlocale() is not deprecated (unlike getdefaultlocale)
    try:
        lang_code = locale.getlocale()[0] or ""
        if lang_code.lower().startswith("es"):
            return "es"
    except Exception:
        pass
    return "en"


def set_lang(lang: str) -> None:
    """Set active language globally. Accepts 'en' or 'es'."""
    global _current_lang
    if lang in STRINGS:
        _current_lang = lang


def get_lang() -> str:
    return _current_lang


def t(key: str, *args) -> str:
    """
    Translate a string key to the current language.
    Falls back to English if key missing in active lang.
    *args are positional format arguments.
    """
    lang_strings = STRINGS.get(_current_lang, STRINGS["en"])
    text = lang_strings.get(key) or STRINGS["en"].get(key) or key
    if args:
        return text.format(*args)
    return text
