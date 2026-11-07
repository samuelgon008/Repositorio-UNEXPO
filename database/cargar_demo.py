"""Carga documentos de DEMOSTRACIÓN: genera un PDF de prueba por cada trabajo,
lo guarda en backend/storage/documentos/ y registra sus metadatos en la BD.

    python ../database/cargar_demo.py        (desde la carpeta backend, con el .venv activo)

Requiere haber ejecutado antes init_db.py --crear-admin. Es idempotente:
si se ejecuta dos veces no duplica nada.

    python ../database/cargar_demo.py --exportar-web

Exporta los MISMOS trabajos al modo demostración de la interfaz web (sin
base de datos): PDFs en frontend-web/public/demo/ y la lista en
frontend-web/lib/demo-documentos.json. Úselo al cambiar los datos de prueba.

    python ../database/cargar_demo.py --usuarios-prueba

Además crea una cuenta de prueba por rol (docente y estudiante; el
administrador es el suyo) para probar los permisos. Contraseña: Prueba2026.
"""
import hashlib
import json
import sys
import textwrap
import unicodedata
from datetime import date
from pathlib import Path

DIR_DB = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR_DB.parent / "backend"))

from sqlalchemy import select  # noqa: E402

from app.config import settings  # noqa: E402
from app.core.security import hashear_password  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    Documento, DocumentoPersona, Etiqueta, EstadoUsuario, PalabraClave, Participacion, Persona,
    Rol, TipoDocumento, Usuario,
)

# ----------------------------------------------------------------------------
# Datos de prueba: (nombres, apellidos) de autores y tutores, área = etiqueta
# ----------------------------------------------------------------------------
TRABAJOS = [
    {
        "titulo": "Sistema mecatrónico embebido para clasificación automática de piezas por color y tamaño",
        "tipo": "TEG", "fecha": date(2026, 10, 15), "area": "Control y Automatización",
        "autores": [("María Fernanda", "Rojas"), ("Luis Alberto", "Méndez")],
        "tutores": [("Carlos", "Pérez", "UNEXPO")],
        "palabras_clave": ["visión artificial", "ESP32", "banda transportadora"],
        "resumen": "Diseño e implementación de una celda de clasificación basada en un microcontrolador ESP32 y una cámara OV2640. El sistema identifica piezas por color y dimensiones mediante procesamiento de imágenes en el borde y acciona servomotores para desviarlas a su contenedor, alcanzando una precisión del 96 % a 30 piezas por minuto.",
    },
    {
        "titulo": "Red de sensores LoRaWAN para el monitoreo de la calidad del agua en el río Caroní",
        "tipo": "TEG", "fecha": date(2026, 9, 28), "area": "Telecomunicaciones",
        "autores": [("José Gregorio", "Salazar")],
        "tutores": [("Ana", "Martínez", "UNEXPO")],
        "palabras_clave": ["LoRaWAN", "IoT", "pH", "turbidez"],
        "resumen": "Se desplegaron cinco nodos autónomos alimentados por energía solar que miden pH, turbidez, temperatura y oxígeno disuelto. Los datos viajan por LoRaWAN hasta un gateway y se visualizan en un tablero web con alertas en tiempo real cuando se superan los límites de la norma venezolana.",
    },
    {
        "titulo": "Optimización del sistema de excitación de un generador síncrono en una planta hidroeléctrica",
        "tipo": "IEI", "fecha": date(2026, 9, 10), "area": "Electrónica de Potencia", "empresa": "CORPOELEC",
        "autores": [("Daniela Carolina", "Ruiz")],
        "tutores": [("Ramón", "Figueroa", "CORPOELEC")],
        "palabras_clave": ["AVR", "generador síncrono", "PID"],
        "resumen": "Informe de entrenamiento industrial que documenta la sintonización del regulador automático de voltaje de una unidad generadora. Se modeló el lazo de excitación en MATLAB/Simulink y se propusieron nuevos parámetros PID que reducen el sobreimpulso del voltaje en terminales de 12 % a 4 %.",
    },
    {
        "titulo": "Prótesis mioeléctrica de mano de bajo costo con control por redes neuronales",
        "tipo": "TEG", "fecha": date(2025, 12, 2), "area": "Procesamiento de Señales",
        "autores": [("Andrea Valentina", "Gómez"), ("Pedro José", "Hernández")],
        "tutores": [("Miguel Ángel", "Torres", "UNEXPO")],
        "palabras_clave": ["EMG", "impresión 3D", "TinyML"],
        "resumen": "Se desarrolló una prótesis impresa en 3D que interpreta señales electromiográficas superficiales del antebrazo. Un modelo de red neuronal cuantizado, ejecutado en un microcontrolador ARM Cortex-M4, reconoce seis gestos con una exactitud del 91 % y una latencia menor a 150 ms.",
    },
    {
        "titulo": "Diseño de un inversor fotovoltaico monofásico con seguimiento del punto de máxima potencia",
        "tipo": "TEG", "fecha": date(2025, 11, 20), "area": "Energías Renovables",
        "autores": [("Ricardo Antonio", "Marcano")],
        "tutores": [("Laura", "Contreras", "UNEXPO")],
        "palabras_clave": ["MPPT", "inversor", "SPWM", "paneles solares"],
        "resumen": "Implementación de un inversor de 1 kW con algoritmo MPPT de perturbación y observación sobre un DSP TMS320F28379D. El prototipo entrega una onda senoidal con distorsión armónica total inferior al 3 % y una eficiencia pico del 94 %.",
    },
    {
        "titulo": "Automatización del sistema de dosificación de aditivos en la línea de colada de SIDOR",
        "tipo": "IEI", "fecha": date(2025, 10, 5), "area": "Control y Automatización", "empresa": "SIDOR",
        "autores": [("Gabriela Alejandra", "León")],
        "tutores": [("Héctor", "Villarroel", "SIDOR")],
        "palabras_clave": ["PLC", "SCADA", "Siemens S7-1500"],
        "resumen": "Durante el entrenamiento industrial se migró la lógica de dosificación de relés a un PLC Siemens S7-1500 y se diseñaron las pantallas HMI en WinCC. La automatización redujo la variabilidad de la dosificación y el tiempo de parada por ajustes manuales.",
    },
    {
        "titulo": "Plataforma FPGA para la enseñanza de sistemas digitales en el laboratorio de Electrónica",
        "tipo": "TEG", "fecha": date(2025, 7, 18), "area": "Sistemas Digitales y Embebidos",
        "autores": [("Jesús Manuel", "Blanco")],
        "tutores": [("Patricia", "Lugo", "UNEXPO")],
        "palabras_clave": ["FPGA", "VHDL", "docencia"],
        "resumen": "Se diseñó una tarjeta de desarrollo con FPGA Lattice iCE40 y una guía de diez prácticas de laboratorio en VHDL. La herramienta usa software de código abierto y reduce el costo por puesto de trabajo frente a las tarjetas comerciales.",
    },
    {
        "titulo": "Enlace de radio definido por software para comunicaciones rurales en el estado Bolívar",
        "tipo": "TEG", "fecha": date(2024, 11, 30), "area": "Telecomunicaciones",
        "autores": [("Rafael Enrique", "Castillo"), ("Mariana Isabel", "Díaz")],
        "tutores": [("Fernando", "Ríos", "UNEXPO")],
        "palabras_clave": ["SDR", "GNU Radio", "OFDM"],
        "resumen": "Implementación de un enlace punto a punto de 12 km basado en radio definida por software con modulación OFDM en GNU Radio. Se evaluó el desempeño frente al multitrayecto característico de la zona y se propone como alternativa de bajo costo para comunidades sin cobertura.",
    },
]

TIPO_LARGO = {"TEG": "TRABAJO ESPECIAL DE GRADO", "IEI": "INFORME DE ENTRENAMIENTO INDUSTRIAL"}


# ----------------------------------------------------------------------------
# Generador mínimo de PDF (una página, fuente Helvetica, sin dependencias)
# ----------------------------------------------------------------------------
def _texto_pdf(texto: str) -> str:
    """Escapa caracteres especiales de PDF; los acentos se codifican luego en cp1252."""
    return texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _ancho(texto: str, tam: float) -> float:
    """Ancho aproximado del texto en Helvetica (mayúsculas más anchas que minúsculas)."""
    return sum(0.28 if c == " " else 0.68 if c.isupper() else 0.5 for c in texto) * tam


def generar_pdf(trabajo: dict) -> bytes:
    nombre = lambda p: f"{p[0]} {p[1]}"  # noqa: E731
    lineas = []  # (tamaño de letra, x, y, texto)
    y = 790

    def escribir(texto, tam=11, centrado=False, ancho=88, salto=1.45):
        nonlocal y
        for linea in textwrap.wrap(texto, ancho) or [""]:
            x = (595 - _ancho(linea, tam)) / 2 if centrado else 60
            lineas.append((tam, x, y, linea))
            y -= tam * salto

    escribir("UNIVERSIDAD NACIONAL EXPERIMENTAL POLITÉCNICA", 10, True, 70)
    escribir("\"ANTONIO JOSÉ DE SUCRE\" - VICERRECTORADO PUERTO ORDAZ", 10, True, 70)
    escribir("DEPARTAMENTO DE INGENIERÍA ELECTRÓNICA", 10, True, 70)
    y -= 40
    escribir(TIPO_LARGO[trabajo["tipo"]], 12, True, 60)
    y -= 10
    escribir(trabajo["titulo"].upper(), 15, True, 48, 1.35)
    y -= 30
    escribir("Autor(es): " + ", ".join(map(nombre, trabajo["autores"])))
    escribir("Tutor: " + ", ".join(map(nombre, trabajo["tutores"])))
    if trabajo.get("empresa"):
        escribir("Empresa: " + trabajo["empresa"])
    escribir("Fecha de aprobación: " + trabajo["fecha"].strftime("%d/%m/%Y"))
    y -= 20
    escribir("RESUMEN", 12)
    escribir(trabajo["resumen"])
    y -= 8
    escribir("Palabras clave: " + ", ".join(trabajo["palabras_clave"]))
    y = 70
    escribir("Documento de prueba generado automáticamente para el Repositorio Digital.", 8, True, 100)

    contenido = "\n".join(
        f"BT /F1 {t} Tf {x:.1f} {yy:.1f} Td ({_texto_pdf(s)}) Tj ET" for t, x, yy, s in lineas
    ).encode("cp1252", errors="replace")

    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Length %d >>\nstream\n" % len(contenido) + contenido + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    posiciones = []
    for i, obj in enumerate(objetos, start=1):
        posiciones.append(len(pdf))
        pdf += b"%d 0 obj\n" % i + obj + b"\nendobj\n"
    inicio_xref = len(pdf)
    pdf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    pdf += b"".join(b"%010d 00000 n \n" % p for p in posiciones)
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objetos) + 1, inicio_xref)
    return bytes(pdf)


# ----------------------------------------------------------------------------
# Carga en la base de datos
# ----------------------------------------------------------------------------
def _persona(db, nombres, apellidos, institucion=None) -> Persona:
    p = db.scalar(select(Persona).where(Persona.nombres == nombres, Persona.apellidos == apellidos))
    if p is None:
        p = Persona(nombres=nombres, apellidos=apellidos, institucion=institucion)
        db.add(p)
    return p


def _palabra(db, termino) -> PalabraClave:
    termino = termino.strip().lower()
    p = db.scalar(select(PalabraClave).where(PalabraClave.termino == termino))
    if p is None:
        p = PalabraClave(termino=termino)
        db.add(p)
    return p


# Cuentas para probar los roles (sólo para desarrollo, nunca en producción)
USUARIOS_PRUEBA = [
    # username,         rol,         nombres,     apellidos,  cédula
    ("docente.prueba",    "docente",    "Laura",     "Contreras", "V-90000001"),
    ("estudiante.prueba", "estudiante", "José",      "Salazar",   "V-90000002"),
]
CLAVE_PRUEBA = "Prueba2026"


def crear_usuarios_prueba() -> list[str]:
    """Crea (si no existen) las cuentas de prueba activas. Devuelve las creadas."""
    creados = []
    with SessionLocal() as db:
        roles = {r.nombre: r for r in db.scalars(select(Rol))}
        for username, rol, nombres, apellidos, cedula in USUARIOS_PRUEBA:
            if db.scalar(select(Usuario.id).where(Usuario.username == username)):
                continue
            db.add(Usuario(
                username=username, nombres=nombres, apellidos=apellidos, cedula=cedula,
                email=f"{username}@prueba.local", password_hash=hashear_password(CLAVE_PRUEBA),
                rol_id=roles[rol].id, estado=EstadoUsuario.activo,
            ))
            creados.append(username)
        db.commit()
    return creados


def nombre_archivo(t: dict) -> str:
    """Nombre de descarga sin acentos, p. ej. "TEG_2026_Mendez.pdf"."""
    apellido = unicodedata.normalize("NFKD", t["autores"][0][1]).encode("ascii", "ignore").decode()
    return f"{t['tipo']}_{t['fecha'].year}_{apellido}.pdf"


def cargar() -> int:
    """Devuelve cuántos documentos nuevos se cargaron."""
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    nuevos = 0
    with SessionLocal() as db:
        admin = db.scalar(select(Usuario).join(Rol).where(Rol.nombre == "administrador").order_by(Usuario.id))
        if admin is None:
            sys.exit("✗ Primero cree un administrador: python ../database/init_db.py --crear-admin")
        tipos = {t.codigo: t for t in db.scalars(select(TipoDocumento))}

        for t in TRABAJOS:
            pdf = generar_pdf(t)
            sha = hashlib.sha256(pdf).hexdigest()
            if db.scalar(select(Documento.id).where(Documento.hash_sha256 == sha)):
                continue  # ya cargado

            ruta = f"{sha}.pdf"
            (settings.storage_dir / ruta).write_bytes(pdf)
            doc = Documento(
                titulo=t["titulo"], resumen=t["resumen"], tipo_id=tipos[t["tipo"]].id,
                anio=t["fecha"].year, fecha_aprobacion=t["fecha"], empresa=t.get("empresa"),
                ruta_archivo=ruta, nombre_original=nombre_archivo(t),
                tamano_bytes=len(pdf), hash_sha256=sha, publicado=True, subido_por=admin.id,
            )
            doc.etiquetas = [db.scalar(select(Etiqueta).where(Etiqueta.nombre == t["area"]))]
            doc.palabras_clave = [_palabra(db, p) for p in t["palabras_clave"]]
            for orden, (n, a) in enumerate(t["autores"], start=1):
                doc.participantes.append(DocumentoPersona(
                    persona=_persona(db, n, a, "UNEXPO"), participacion=Participacion.autor, orden=orden))
            for n, a, inst in t["tutores"]:
                papel = Participacion.tutor_academico if inst == "UNEXPO" else Participacion.tutor_industrial
                doc.participantes.append(DocumentoPersona(persona=_persona(db, n, a, inst), participacion=papel))
            db.add(doc)
            db.flush()  # para que las personas nuevas existan antes del siguiente trabajo
            nuevos += 1
        db.commit()
    return nuevos


def exportar_web() -> Path:
    """Escribe los PDFs y un JSON con la misma forma que GET /documentos."""
    web = DIR_DB.parent / "frontend-web"
    carpeta_pdf = web / "public" / "demo"
    carpeta_pdf.mkdir(parents=True, exist_ok=True)
    documentos = []
    for i, t in enumerate(sorted(TRABAJOS, key=lambda t: t["fecha"], reverse=True), start=1):
        pdf = generar_pdf(t)
        archivo = nombre_archivo(t)
        (carpeta_pdf / archivo).write_bytes(pdf)
        documentos.append({
            "id": i, "titulo": t["titulo"], "resumen": t["resumen"], "tipo": t["tipo"],
            "anio": t["fecha"].year, "fecha": t["fecha"].isoformat(), "empresa": t.get("empresa"),
            "autores": [f"{n} {a}" for n, a in t["autores"]],
            "tutores": [f"{n} {a}" for n, a, _ in t["tutores"]],
            "etiquetas": [t["area"]],
            "palabras_clave": [p.lower() for p in t["palabras_clave"]],
            "nombre_archivo": archivo, "tamano_bytes": len(pdf),
        })
    destino = web / "lib" / "demo-documentos.json"
    destino.write_text(json.dumps(documentos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destino


if __name__ == "__main__":
    if "--exportar-web" in sys.argv:
        print(f"✓ Modo demostración exportado: {exportar_web()}")
        sys.exit()
    from app.services.catalogos import preparar_base_de_datos
    preparar_base_de_datos()  # por si la BD es de una versión anterior
    n = cargar()
    print(f"✓ {n} documentos de prueba cargados." if n else "· Los documentos de prueba ya estaban cargados.")
    print(f"  PDFs en: {settings.storage_dir}")
    if "--usuarios-prueba" in sys.argv:
        crear_usuarios_prueba()
        print(f"✓ Cuentas de prueba (contraseña {CLAVE_PRUEBA}):")
        for username, rol, *_ in USUARIOS_PRUEBA:
            print(f"   - {username:<18} rol {rol}")
