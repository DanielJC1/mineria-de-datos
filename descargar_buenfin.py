"""
Descarga los precios de "Quién es Quién en los Precios - El Buen Fin 2026" (Profeco)
y los guarda en dos archivos CSV:

  productos_buenfin_2026.csv          -> una fila por producto-tienda (último precio)
  historial_precios_buenfin_2026.csv  -> una fila por producto-tienda-fecha

Fuente: https://elbuenfin.profeco.gob.mx/  (API pública que usa el propio portal)

Uso:
  python descargar_buenfin.py                                   # todas las ciudades
  python descargar_buenfin.py --ciudades "ciudad de mexico"     # prueba rápida
  python descargar_buenfin.py --ciudades "ciudad de mexico,guadalajara,monterrey"

Solo usa la biblioteca estándar de Python (no hay que instalar nada).
Si se interrumpe, vuelve a correrlo: las respuestas ya descargadas se guardan en
la carpeta cache_buenfin/ y no se vuelven a pedir.
"""

import argparse
import csv
import json
import os
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://elbuenfin.profeco.gob.mx/api/get"
CACHE_DIR = "cache_buenfin"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (descarga para practica escolar)",
    "Accept": "application/json",
}

_print_lock = threading.Lock()


def normalizar(texto):
    """Quita acentos y pasa a minúsculas para comparar nombres de ciudades."""
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in texto if not unicodedata.combining(c)).lower().strip()


def obtener_json(ruta, delay, reintentos=4):
    """GET a la API con caché en disco, pausa entre peticiones y reintentos."""
    archivo_cache = os.path.join(CACHE_DIR, ruta.strip("/").replace("/", "_") + ".json")
    if os.path.exists(archivo_cache):
        with open(archivo_cache, encoding="utf-8") as f:
            return json.load(f)

    url = f"{BASE}/{ruta.strip('/')}"
    for intento in range(1, reintentos + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                datos = json.loads(resp.read().decode("utf-8"))
            with open(archivo_cache, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False)
            time.sleep(delay)
            return datos
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            espera = 2 ** intento
        except Exception:
            espera = 2 ** intento
        with _print_lock:
            print(f"  ! Falló {url} (intento {intento}/{reintentos}); reintento en {espera}s")
        time.sleep(espera)
    with _print_lock:
        print(f"  X No se pudo descargar {url}; se omite")
    return None


def tiendas_de_detalle(detalle):
    """El detalle viene como objeto {"0": {...}, "1": {...}} o como lista; devuelve las tiendas."""
    if detalle is None:
        return []
    valores = detalle.values() if isinstance(detalle, dict) else detalle
    return [v for v in valores if isinstance(v, dict) and "historial" in v]


def main():
    parser = argparse.ArgumentParser(description="Descarga precios del Buen Fin 2026 (Profeco)")
    parser.add_argument("--ciudades", default="todas",
                        help='Nombres separados por coma, p. ej. "ciudad de mexico,guadalajara". Por defecto: todas')
    parser.add_argument("--workers", type=int, default=4, help="Peticiones en paralelo (default 4)")
    parser.add_argument("--delay", type=float, default=0.3, help="Pausa en segundos tras cada petición (default 0.3)")
    parser.add_argument("--salida", default=".", help="Carpeta donde guardar los CSV")
    args = parser.parse_args()

    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(args.salida, exist_ok=True)

    # 1) Catálogos
    ciudades = obtener_json("ciudades", args.delay)
    categorias = obtener_json("ctg/productos", args.delay)
    if not ciudades or not categorias:
        sys.exit("No se pudieron obtener los catálogos. Revisa tu conexión o si el sitio está disponible.")

    if args.ciudades.strip().lower() != "todas":
        buscadas = [normalizar(c) for c in args.ciudades.split(",") if c.strip()]
        ciudades = [c for c in ciudades if any(b in normalizar(c["nombre"]) for b in buscadas)]
        if not ciudades:
            sys.exit("Ninguna ciudad coincide. Revisa los nombres (p. ej. \"ciudad de mexico\").")

    print(f"Ciudades: {', '.join(c['nombre'] for c in ciudades)}")
    print(f"Categorías: {len(categorias)}\n")

    # 2) Lista de productos por ciudad y categoría
    trabajos = []  # (ciudad, categoria, producto)
    for ciudad in ciudades:
        for cat in categorias:
            resp = obtener_json(f"productos/{ciudad['id']}/{cat['id_categoria']}", args.delay)
            productos = (resp or {}).get("data") or []
            for p in productos:
                trabajos.append((ciudad, cat, p))
        print(f"  {ciudad['nombre']}: listado listo ({len(trabajos)} productos acumulados)")

    total = len(trabajos)
    seg_estimados = total * (args.delay + 0.4) / max(args.workers, 1)
    print(f"\nProductos a consultar: {total}  (tiempo estimado: ~{seg_estimados/60:.0f} min)\n")

    # 3) Detalle (tiendas e historial) de cada producto, en paralelo
    filas_productos, filas_historial = [], []
    hechos = 0
    inicio = time.time()

    def procesar(trabajo):
        ciudad, cat, p = trabajo
        ruta = f"producto/{ciudad['id']}/{cat['id_categoria']}/0/{p['id_producto']}"
        return trabajo, obtener_json(ruta, args.delay)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futuros = [ex.submit(procesar, t) for t in trabajos]
        for fut in as_completed(futuros):
            (ciudad, cat, p), detalle = fut.result()
            base = {
                "id_ciudad": ciudad["id"],
                "ciudad": ciudad["nombre"],
                "id_categoria": cat["id_categoria"],
                "categoria": cat["categoria"],
                "id_producto": p.get("id_producto"),
                "id_tipo_producto": p.get("id_tipo_producto"),
                "tipo_producto": p.get("tipo_producto"),
                "marca": p.get("marca"),
                "descripcion": p.get("descripcion"),
            }
            for tienda in tiendas_de_detalle(detalle):
                historial = sorted(tienda.get("historial") or [], key=lambda h: h.get("fecha", ""))
                filas_productos.append({
                    **base,
                    "tienda": tienda.get("estacion"),
                    "direccion": tienda.get("direccion"),
                    "ultimo_precio": tienda.get("ultimo_precio"),
                    "fecha_ultimo_precio": historial[-1]["fecha"] if historial else "",
                    "n_registros_historial": len(historial),
                })
                for h in historial:
                    filas_historial.append({
                        **base,
                        "tienda": tienda.get("estacion"),
                        "fecha": h.get("fecha"),
                        "precio": h.get("precio"),
                    })
            hechos += 1
            if hechos % 100 == 0 or hechos == total:
                transcurrido = time.time() - inicio
                restante = transcurrido / hechos * (total - hechos)
                print(f"  {hechos}/{total} productos  |  {len(filas_productos)} filas  |  faltan ~{restante/60:.1f} min")

    # 4) Guardar CSV (utf-8-sig para que Excel muestre bien los acentos)
    def guardar(nombre, filas):
        ruta = os.path.join(args.salida, nombre)
        if not filas:
            print(f"Sin datos para {nombre}")
            return
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
            w.writeheader()
            w.writerows(filas)
        print(f"Guardado: {ruta}  ({len(filas):,} filas)")

    print()
    guardar("productos_buenfin_2026.csv", filas_productos)
    guardar("historial_precios_buenfin_2026.csv", filas_historial)
    print(f"\nListo en {(time.time() - inicio)/60:.1f} min.")


if __name__ == "__main__":
    main()
