"""Genera las versiones .webp de las imágenes de la web (pesan menos y la web las usa si existen).

Necesita Pillow (una vez):  python3 -m pip install pillow

Uso (desde la carpeta de la web o cualquier subcarpeta):
  python3 _build/webp.py                                   todas las imágenes de assets/img
  python3 _build/webp.py assets/img/noticias               una carpeta (y sus subcarpetas)
  python3 _build/webp.py assets/img/pubs/foto.jpg …        uno o varios archivos

Cada .webp queda anotado en _build/webp.json con la huella de la foto de la que sale. Si después
cambias la foto (aunque tenga el mismo nombre), la web deja de usar el .webp viejo hasta que vuelvas
a ejecutar este script. Al terminar regenera la web.
"""
import hashlib
import json
import os
import sys

ORIGEN = ('.jpg', '.jpeg', '.png')
# Las fotos de galería (carpetas dentro de noticias/) se muestran en .jpg: no necesitan .webp
SIN_WEBP = ('assets/img/noticias/',)


def raiz():
    for inicio in (os.getcwd(), os.path.dirname(os.path.abspath(__file__))):
        d = inicio
        while True:
            if os.path.exists(os.path.join(d, '_build', 'build.py')):
                return d
            if os.path.dirname(d) == d:
                break
            d = os.path.dirname(d)
    sys.exit('No encuentro la carpeta de la web (la que contiene _build/build.py). Ejecuta el script desde dentro de ella.')


ROOT = raiz()
MANIFIESTO = os.path.join(ROOT, '_build', 'webp.json')


def huella(path):
    with open(path, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()[:16]


def leer():
    try:
        with open(MANIFIESTO, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def guardar_manifiesto(m):
    with open(MANIFIESTO, 'w', encoding='utf-8') as f:
        json.dump(dict(sorted(m.items())), f, indent=0, ensure_ascii=False)


def rel(path):
    return os.path.relpath(os.path.abspath(path), ROOT).replace(os.sep, '/')


def registrar(origen, m=None):
    """Anota que el .webp junto a 'origen' corresponde a su contenido actual."""
    propio = m is None
    m = leer() if propio else m
    m[rel(origen)] = huella(origen)
    if propio:
        guardar_manifiesto(m)
    return m


def es_galeria(r):
    # assets/img/noticias/<id>/foto.jpg (dentro de una subcarpeta de noticias)
    return r.startswith(SIN_WEBP[0]) and r.count('/') > 3


def convertir(path, m):
    from PIL import Image, ImageOps
    r = rel(path)
    base = os.path.splitext(path)[0]
    if m.get(r) == huella(path) and os.path.exists(base + '.webp'):
        return False  # ya está al día
    im = ImageOps.exif_transpose(Image.open(path))
    if im.mode not in ('RGB', 'RGBA'):
        im = im.convert('RGBA' if 'A' in im.getbands() or im.mode == 'P' else 'RGB')
    im.save(base + '.webp', quality=80, method=6)
    registrar(path, m)
    print('  →', rel(base) + '.webp')
    return True


def archivos(args):
    destinos = args or [os.path.join(ROOT, 'assets', 'img')]
    for a in destinos:
        p = a if os.path.isabs(a) else os.path.join(os.getcwd(), a)
        if not os.path.exists(p):
            p = os.path.join(ROOT, a)
        if os.path.isdir(p):
            for d, _, fs in os.walk(p):
                for f in sorted(fs):
                    if f.lower().endswith(ORIGEN):
                        yield os.path.join(d, f)
        elif os.path.isfile(p) and p.lower().endswith(ORIGEN):
            yield p
        else:
            print(f'  ✗ {a}: no existe o no es .jpg/.jpeg/.png')


def main(args):
    if args and args[0] in ('-h', '--help', 'ayuda'):
        sys.exit(__doc__)
    try:
        import PIL  # noqa: F401
    except ImportError:
        sys.exit('Falta Pillow. Instálalo con:  python3 -m pip install pillow')
    m = leer()
    hechos = 0
    for p in archivos(args):
        if es_galeria(rel(p)) and not args:
            continue
        try:
            hechos += convertir(p, m)
        except Exception as e:
            print(f'  ✗ {rel(p)}: {e}')
    guardar_manifiesto(m)
    print(f'{hechos} .webp nuevo(s) o actualizado(s).')
    import subprocess
    print('Regenerando la web…')
    subprocess.run([sys.executable, os.path.join(ROOT, '_build', 'build.py')], cwd=ROOT)


if __name__ == '__main__':
    main(sys.argv[1:])
