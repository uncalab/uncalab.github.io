"""Mapa de colaboraciones en SVG estático (sin teselas externas).

Geometría: world-atlas 2.0.2 (Natural Earth, licencia ISC/dominio público), en _build/.
Coordenadas de ciudades: aproximadas a dos decimales, para situar el punto en el mapa.
"""
import json, os, math, html
from collections import defaultdict
from colab import ORGS

HERE = os.path.dirname(os.path.abspath(__file__))

CITY = {  # ciudad (como viene en el Excel): (lat, lon)
    'Berlín': (52.52, 13.40), 'Bonn': (50.74, 7.10), 'Erlangen': (49.60, 11.00), 'Francfort': (50.11, 8.68),
    'Greifswald': (54.09, 13.38), 'Leipzig': (51.34, 12.37), 'Münster': (51.96, 7.63),
    'Buenos Aires': (-34.60, -58.38), 'Ciudad de Mendoza': (-32.89, -68.84),
    'Adelaida': (-34.93, 138.60), 'Brisbane': (-27.47, 153.03), 'Melbourne': (-37.81, 144.96),
    'Perth': (-31.95, 115.86), 'Sídney': (-33.87, 151.21),
    'Amberes': (51.22, 4.40), 'Bruselas': (50.85, 4.35),
    'Concepción': (-36.83, -73.05), 'Santiago de Chile': (-33.45, -70.67), 'Talca': (-35.43, -71.66),
    'Barranquilla': (10.96, -74.80), 'Medellín': (6.24, -75.58), 'Ambato': (-1.24, -78.62),
    'Barcelona': (41.39, 2.17), 'Girona': (41.98, 2.82), 'Logroño': (42.47, -2.45), 'Madrid': (40.42, -3.70),
    'Murcia': (37.99, -1.13), 'Málaga': (36.72, -4.42), 'Santiago de Compostela': (42.88, -8.54),
    'Sevilla': (37.39, -5.98), 'Valencia': (39.47, -0.38), "l'Hospitalet de Llobregat": (41.36, 2.10),
    'Austin': (30.27, -97.74), 'Boston': (42.36, -71.06), 'Houston': (29.76, -95.37), 'Iowa City': (41.66, -91.53),
    'Nueva York': (40.71, -74.01), 'Reno': (39.53, -119.81), 'San Antonio': (29.42, -98.49),
    'San Francisco': (37.77, -122.42), 'Stanford': (37.43, -122.17),
    'Tallin': (59.44, 24.75), 'Helsinki': (60.17, 24.94), 'Kuopio': (62.89, 27.68), 'Tampere': (61.50, 23.76),
    'Burdeos': (44.84, -0.58), 'Caen': (49.18, -0.37), 'Gif-sur-Yvette': (48.70, 2.13), 'París': (48.86, 2.35),
    'Dublín': (53.35, -6.26), 'Galway': (53.27, -9.05),
    'Brescia': (45.54, 10.22), 'Trento': (46.07, 11.12), 'Verona': (45.44, 10.99), 'Imsida': (35.90, 14.48),
    'Ciudad de México': (19.43, -99.13), 'Bergen': (60.39, 5.32),
    'Róterdam': (51.92, 4.48), 'Ámsterdam': (52.37, 4.90),
    'Cambridge': (52.21, 0.12), 'Londres': (51.51, -0.13), 'Mánchester': (53.48, -2.24),
    'Newcastle-upon-Tyne': (54.98, -1.62), 'Nottingham': (52.95, -1.15), 'Oxford': (51.75, -1.26),
    'Estocolmo': (59.33, 18.07), 'Gotemburgo': (57.71, 11.97), 'Karlskrona': (56.16, 15.59),
    'Lund': (55.70, 13.19), 'Upsala': (59.86, 17.64), 'Ginebra': (46.20, 6.14), 'Lausana': (46.52, 6.63),
}
CITY_EN = {'Berlín': 'Berlin', 'Francfort': 'Frankfurt', 'Ciudad de Mendoza': 'Mendoza', 'Adelaida': 'Adelaide',
           'Sídney': 'Sydney', 'Amberes': 'Antwerp', 'Bruselas': 'Brussels', 'Santiago de Chile': 'Santiago',
           'Sevilla': 'Seville', 'Nueva York': 'New York', 'Tallin': 'Tallinn', 'Burdeos': 'Bordeaux',
           'París': 'Paris', 'Dublín': 'Dublin', 'Imsida': 'Msida', 'Ciudad de México': 'Mexico City',
           'Róterdam': 'Rotterdam', 'Ámsterdam': 'Amsterdam', 'Londres': 'London', 'Mánchester': 'Manchester',
           'Estocolmo': 'Stockholm', 'Gotemburgo': 'Gothenburg', 'Upsala': 'Uppsala', 'Ginebra': 'Geneva',
           'Lausana': 'Lausanne'}
COUNTRY_EN = {'España': 'Spain', 'Reino Unido': 'United Kingdom', 'Estados Unidos': 'United States',
              'Alemania': 'Germany', 'Suecia': 'Sweden', 'Francia': 'France', 'Australia': 'Australia',
              'Chile': 'Chile', 'Suiza': 'Switzerland', 'Argentina': 'Argentina', 'Países Bajos': 'Netherlands',
              'Italia': 'Italy', 'Finlandia': 'Finland', 'Bélgica': 'Belgium', 'Colombia': 'Colombia',
              'Irlanda': 'Ireland', 'Ecuador': 'Ecuador', 'Estonia': 'Estonia', 'Noruega': 'Norway',
              'Malta': 'Malta', 'México': 'Mexico'}
HOME = 'Málaga'


def _rings(topo):
    sx, sy = topo['transform']['scale']
    tx, ty = topo['transform']['translate']
    arcs = []
    for arc in topo['arcs']:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(ids):
        out = []
        for i in ids:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(a if not out else a[1:])
        return out
    for g in topo['objects']['countries']['geometries']:
        polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']] if g['type'] == 'Polygon' else []
        for poly in polys:
            for r in poly:
                yield ring(r)


def _path(topo_file, proj, box, step=1.5):
    x0, y0, x1, y1 = box
    d = []
    for r in _rings(json.load(open(os.path.join(HERE, topo_file)))):
        uw, off, prev = [], 0, None  # desenrolla anillos que cruzan el antimeridiano
        for lon, lat in r:
            if prev is not None and abs(lon + off - prev) > 180:
                off += 360 if prev > lon + off else -360
            prev = lon + off
            uw.append((lon + off, lat))
        pts = [proj(lon, lat) for lon, lat in uw]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if max(xs) < x0 or min(xs) > x1 or max(ys) < y0 or min(ys) > y1:
            continue
        s, last = [], None
        for x, y in pts:
            if last and abs(x - last[0]) + abs(y - last[1]) < step:
                continue
            last = (x, y)
            s.append(f'{round(x):d},{round(y):d}')
        if len(s) > 2:
            d.append('M' + 'L'.join(s) + 'Z')
    return ''.join(d)


def cities():
    by = defaultdict(list)
    for name, kind, city, country, n in ORGS:
        by[(city, country)].append((name, n))
    return by


def land_file(topo_file, proj, box, out):
    x0, y0, x1, y1 = box
    open(out, 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0:.0f} {y1 - y0:.0f}">'
                         f'<path fill="#dfe5ec" stroke="#fff" stroke-width=".6" stroke-linejoin="round" d="{_path(topo_file, proj, box)}"/></svg>')


def _svg(lang, img, proj, box, rscale, label):
    x0, y0, x1, y1 = box
    by = cities()
    dots = []
    for i, ((city, country), orgs) in enumerate(sorted(by.items(), key=lambda kv: -len(kv[1]))):
        lat, lon = CITY[city]
        x, y = proj(lon, lat)
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            continue
        c = city if lang == 'es' else CITY_EN.get(city, city)
        k = country if lang == 'es' else COUNTRY_EN[country]
        r = rscale * (1 + 0.45 * math.sqrt(len(orgs) - 1))
        home = ' home' if city == HOME else ''
        lst = '|'.join(f'{o} ({n})' for o, n in sorted(orgs, key=lambda o: -o[1]))
        dots.append(f'<circle class="dot{home}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" tabindex="0" role="button" '
                    f'data-c="{html.escape(c)}, {html.escape(k)}" data-o="{html.escape(lst, quote=True)}">'
                    f'<title>{html.escape(c)}, {html.escape(k)} · {len(orgs)}</title></circle>')
    return (f'<svg viewBox="{x0} {y0} {x1 - x0:.0f} {y1 - y0:.0f}" role="img" aria-label="{label}">'
            f'<image href="{img}" x="{x0}" y="{y0}" width="{x1 - x0:.0f}" height="{y1 - y0:.0f}"/>{"".join(reversed(dots))}</svg>')


_K = 1000 / 360
W_PROJ = lambda lon, lat: ((lon + 180) * _K, (75 - lat) * _K * 1.15)
W_BOX = (0, 0, 1000, round(125 * _K * 1.15))
_C = math.cos(math.radians(50))
E_PROJ = lambda lon, lat: ((lon + 11) * _C * 14, (65 - lat) * 14)
E_BOX = (0, 0, round(42 * _C * 14), 31 * 14)


def write_land(img_dir):
    land_file('countries-110m.json', W_PROJ, W_BOX, os.path.join(img_dir, 'mapa-mundo.svg'))
    land_file('countries-50m.json', E_PROJ, E_BOX, os.path.join(img_dir, 'mapa-europa.svg'))


def world_svg(lang, pre, label):
    return _svg(lang, pre + 'assets/img/mapa-mundo.svg', W_PROJ, W_BOX, 3.2, label)


def europe_svg(lang, pre, label):
    return _svg(lang, pre + 'assets/img/mapa-europa.svg', E_PROJ, E_BOX, 4.2, label)
