"""Prepara imágenes para la web: recorta, redimensiona, comprime y las guarda con el nombre correcto.

Necesita Pillow (una vez):  python3 -m pip install pillow

Sin nada más, prepara todas las fotos del equipo y regenera la web:
  python3 _build/preparar_imagenes.py

Otros usos (desde la carpeta de la web o cualquier subcarpeta):
  python3 _build/preparar_imagenes.py equipo  foto.jpg  "María José Torres Prioris"  [zoom]
  python3 _build/preparar_imagenes.py todas-equipo  [carpeta]  [zoom]
  python3 _build/preparar_imagenes.py articulo figura.png  10.1016/j.cortex.2025.02.007
  python3 _build/preparar_imagenes.py portada foto.jpg  n-2026-presentaciones-en-la-snl-2026-ginebra
  python3 _build/preparar_imagenes.py fotos   n-2026-presentaciones-en-la-snl-2026-ginebra  f1.jpg f2.jpg …

En 'equipo', zoom acerca a la cara (por defecto 1.6, pensado para fotos de medio cuerpo).
Si la foto ya es un primer plano usa 1; si la cara sigue pequeña, 2 o 2.5.

'todas-equipo' procesa todas las fotos de la carpeta (por defecto assets/img/equipo). Cada foto tiene que
llamarse ya como el miembro (p. ej. diana-lopez-barroso.jpeg o "Diana López Barroso.png"). Las que ya están
preparadas (400×400) se saltan, así que se puede ejecutar las veces que haga falta.

El id de cada noticia está en el Excel (hoja Noticias). Al terminar regenera la web sola.
"""
import os
import re
import sys
import unicodedata

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit('Falta Pillow. Instálalo con:  python3 -m pip install pillow')

def _raiz():
    """Carpeta de la web: la primera, subiendo desde aquí o desde el script, que contenga _build/build.py."""
    for inicio in (os.getcwd(), os.path.dirname(os.path.abspath(__file__))):
        d = inicio
        while True:
            if os.path.exists(os.path.join(d, '_build', 'build.py')):
                return d
            if os.path.dirname(d) == d:
                break
            d = os.path.dirname(d)
    sys.exit('No encuentro la carpeta de la web (la que contiene _build/build.py). Ejecuta el script desde dentro de ella.')


ROOT = _raiz()


def slug(x):
    x = ''.join(c for c in unicodedata.normalize('NFD', x.lower()) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', x).strip('-')


def abrir(path):
    im = ImageOps.exif_transpose(Image.open(path))  # respeta la orientación de las fotos de móvil
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        fondo = Image.new('RGBA', im.size, 'white')
        fondo.alpha_composite(im)
        im = fondo
    return im.convert('RGB')


def recortar(im, w, h, alto=0.5, zoom=1.0):
    """Recorta a la proporción w:h y redimensiona. 'alto' sitúa el recorte vertical (0 arriba, 0.5 centro);
    'zoom' > 1 recorta una zona más pequeña (acerca)."""
    if zoom > 1:
        cw, ch = im.width / zoom, im.height / zoom
        x0 = (im.width - cw) / 2
        y0 = (im.height - ch) * alto
        im = im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch)))
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = round((im.height - h) * alto)
    return im.crop((x, y, x + w, y + h))


def guardar(im, base):
    os.makedirs(os.path.dirname(base), exist_ok=True)
    im.save(base + '.jpg', quality=82, optimize=True, progressive=True)
    im.save(base + '.webp', quality=80, method=6)
    print('  →', os.path.relpath(base, ROOT) + '.jpg (+ .webp)')


def todas_equipo(carpeta, zoom):
    destino = os.path.join(ROOT, 'assets/img/equipo')
    hechas = 0
    for f in sorted(os.listdir(carpeta)):
        base, ext = os.path.splitext(f)
        if ext.lower() not in ('.jpg', '.jpeg', '.png', '.webp', '.heic') or base.lower() == 'avatar':
            continue
        ruta = os.path.join(carpeta, f)
        if ext.lower() == '.webp' and os.path.exists(os.path.join(carpeta, base + '.jpg')):
            continue  # es la copia .webp de una foto ya preparada
        try:
            im = abrir(ruta)
        except Exception as e:
            print(f'  ✗ {f}: no se puede abrir ({e})')
            continue
        if im.size == (400, 400):
            continue  # ya preparada
        salida = os.path.join(destino, slug(base))
        guardar(recortar(im, 400, 400, alto=0.2, zoom=zoom), salida)
        if os.path.abspath(ruta) not in (os.path.abspath(salida + '.jpg'), os.path.abspath(salida + '.webp')) \
                and os.path.dirname(os.path.abspath(ruta)) == os.path.abspath(destino):
            os.remove(ruta)  # quita el original grande para que no quede duplicado en la web
        hechas += 1
    print(f'{hechas} foto(s) preparada(s).')


def regenerar():
    import subprocess
    print('Regenerando la web…')
    subprocess.run([sys.executable, os.path.join(ROOT, '_build', 'build.py')], cwd=ROOT)


def main(a):
    if not a:
        a = ['todas-equipo']
    if a[0] in ('-h', '--help', 'ayuda'):
        sys.exit(__doc__)
    if a[0] == 'todas-equipo':
        carpeta = a[1] if len(a) > 1 and not a[1].replace('.', '').replace(',', '').isdigit() else os.path.join(ROOT, 'assets/img/equipo')
        z = [x for x in a[1:] if x.replace('.', '').replace(',', '').isdigit()]
        todas_equipo(carpeta, float(z[0].replace(',', '.')) if z else 1.6)
        regenerar()
        return
    if len(a) < 3:
        sys.exit(__doc__)
    tipo = a[0]
    if tipo == 'equipo':
        foto, nombre = a[1], a[2]
        zoom = float(a[3].replace(',', '.')) if len(a) > 3 else 1.6
        guardar(recortar(abrir(foto), 400, 400, alto=0.2, zoom=zoom), os.path.join(ROOT, 'assets/img/equipo', slug(nombre)))
    elif tipo == 'articulo':
        foto, doi = a[1], a[2]
        guardar(recortar(abrir(foto), 320, 240), os.path.join(ROOT, 'assets/img/pubs', doi.replace('/', '_')))
    elif tipo == 'portada':
        foto, nid = a[1], a[2]
        guardar(recortar(abrir(foto), 720, 288, alto=0.35), os.path.join(ROOT, 'assets/img/noticias', nid))
    elif tipo == 'fotos':
        nid, fotos = a[1], a[2:]
        carpeta = os.path.join(ROOT, 'assets/img/noticias', nid)
        os.makedirs(carpeta, exist_ok=True)
        ya = len([f for f in os.listdir(carpeta) if f.endswith('.jpg')])
        for i, f in enumerate(fotos, ya + 1):
            im = abrir(f)
            im.thumbnail((1600, 1600), Image.LANCZOS)
            dest = os.path.join(carpeta, f'{i:02d}.jpg')
            im.save(dest, quality=82, optimize=True, progressive=True)
            print('  →', os.path.relpath(dest, ROOT))
    else:
        sys.exit(f'Tipo desconocido: {tipo}\n' + __doc__)
    regenerar()


if __name__ == '__main__':
    main(sys.argv[1:])
