"""Genera los SVG/PNG de marca a partir de la malla cerebral (coordenadas 718x529, anterior a la izquierda)."""
import json, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'assets', 'img')
SIL = open(os.path.join(HERE, 'silhouette.d')).read()
DOTS = json.load(open(os.path.join(HERE, 'dots_dense.json')))
NAVY, DOT, TINT = '#003669', '#5A9BD0', '#DCE8F3'
BBOX = (20, 26, 669, 482)

def tract(n, spread, w, color, op, fall=.9, op_add=0.0):
    """Fascículo arqueado: giro frontal inferior -> sobre la cisura de Silvio -> giro temporal superior posterior."""
    s = []
    for i in range(n):
        t = 0 if n == 1 else i/(n-1) - .5
        o = t*spread
        d = (f"M{190+o*.2:.1f} {320+o*.6:.1f} C240 {255+o:.1f} 400 {200+o:.1f} {488+o*.5:.1f} {222+o*.6:.1f}"
             f" S{498+o*.8:.1f} 275 {458+o*.3:.1f} {272+o*.4:.1f}")
        a = min(1, op*(1-abs(t)*fall)+op_add)
        s.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:.2f}" stroke-linecap="round" opacity="{a:.2f}"/>')
    s.append(f'<circle cx="190" cy="320" r="{w*1.5:.2f}" fill="{color}"/><circle cx="458" cy="272" r="{w*1.5:.2f}" fill="{color}"/>')
    return ''.join(s)

def dots(dr=1.0, color=DOT):
    return ''.join(f'<circle cx="{x}" cy="{y}" r="{(1.2+2.6*v)*dr:.1f}" fill="{color}" opacity="{0.3+0.7*v:.2f}"/>' for x, y, v in DOTS)

vb = ' '.join(map(str, BBOX))
def svg(body, viewbox=vb):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">{body}</svg>'

# Marca del logo (cerebro de puntos + 16 hebras muy finas)
open(os.path.join(OUT, 'marca.svg'), 'w').write(svg(dots(1.35) + tract(16, 64, 1.5*.6, NAVY, 1, op_add=1)))
open(os.path.join(OUT, 'marca-blanca.svg'), 'w').write(svg(dots(1.35, '#8FBDE3') + tract(16, 64, 1.5*.6, '#FFFFFF', 1, op_add=1)))
# Favicon simplificado: silueta + haz grueso de 3 hebras
open(os.path.join(OUT, 'favicon.svg'), 'w').write(svg(f'<path d="{SIL}" fill="{TINT}" stroke="{DOT}" stroke-width="18"/>' + tract(3, 44, 15, NAVY, 1, fall=0)))
# Haz para la portada (se superpone a la malla transparente)
open(os.path.join(OUT, 'haz-portada.svg'), 'w').write(svg(tract(16, 64, 1.5, NAVY, .85), '0 0 718 529'))

# Malla cerebral con transparencia: las líneas pasan a azul UNCA y el blanco a transparente
im = Image.open(os.path.join(HERE, 'cerebro-malla-original.png')).convert('RGBA')
px = im.load()
out = Image.new('RGBA', im.size)
po = out.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        lum = (r+g+b)/3
        alpha = int(max(0, min(255, (255-lum)*1.25)) * a/255)
        po[x, y] = (0, 54, 105, alpha)
out.save(os.path.join(OUT, 'cerebro-malla.png'), optimize=True)
print('ok')
