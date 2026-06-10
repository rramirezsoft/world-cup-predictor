"""Revierte todos los cambios de la sesion actual al estado del arte.
Elimina los parrafos con paraId que empieza por E o F (los que se anadieron hoy)
y elimina la tabla semaforo insertada.
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('docs/unpacked/word/document.xml', 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Tamano inicial: {len(content)}')

# 1. Eliminar tabla semaforo (la que contiene "Familia de variable")
tbl_start_marker = 'Familia de variable'
idx = content.find(tbl_start_marker)
if idx > 0:
    # Find enclosing <w:tbl>...</w:tbl>
    tbl_start = content.rfind('<w:tbl>', 0, idx)
    tbl_end = content.find('</w:tbl>', idx) + len('</w:tbl>')
    # Also remove the caption paragraph that comes after
    caption_marker = 'Tabla 1. Comparativa de familias de variables'
    cap_idx = content.find(caption_marker, tbl_end)
    if cap_idx > 0 and cap_idx - tbl_end < 200:
        # Remove caption paragraph too
        cap_p_end = content.find('</w:p>', cap_idx) + len('</w:p>')
        content = content[:tbl_start] + content[cap_p_end:]
        print(f'Eliminada tabla semaforo + pie (desde {tbl_start} hasta {cap_p_end})')
    else:
        content = content[:tbl_start] + content[tbl_end:]
        print(f'Eliminada tabla semaforo (desde {tbl_start} hasta {tbl_end})')

# 2. Eliminar TODOS los parrafos con paraId empezando por "E" (E0000001 a E000001D)
# o "F" (F0000001 a F9999999)
pattern_new_paras = re.compile(
    r'<w:p w14:paraId="[EF][0-9A-F]{6,7}"[^<]*>.*?</w:p>',
    re.DOTALL
)

removed_count = 0
while True:
    match = pattern_new_paras.search(content)
    if not match:
        break
    content = content[:match.start()] + content[match.end():]
    removed_count += 1
    if removed_count > 100:
        break
print(f'Eliminados {removed_count} parrafos nuevos')

# 3. Restaurar numeracion tablas: Tabla 2 -> Tabla 1, Tabla 3 -> Tabla 2
# (ya que eliminamos la tabla 1 semaforo)
content = content.replace('Tabla 2', 'TBLPLACE_1')
content = content.replace('Tabla 3', 'TBLPLACE_2')
content = content.replace('TBLPLACE_1', 'Tabla 1')
content = content.replace('TBLPLACE_2', 'Tabla 2')
print('Renumeradas tablas: Tabla 2 -> 1, Tabla 3 -> 2')

# 4. Restaurar "Ogundeji et al. [12]" a "Boussouf [12]" NO, mantenemos Ogundeji porque es el autor real

# 5. Eliminar heading "Analisis comparado" si existe
heading_marker = 'An\u00e1lisis comparado de trabajos de referencia'
idx = content.find(heading_marker)
if idx > 0:
    p_start = content.rfind('<w:p ', 0, idx)
    p_end = content.find('</w:p>', idx) + len('</w:p>')
    content = content[:p_start] + content[p_end:]
    print('Eliminado heading An\u00e1lisis comparado')

# Otros headings Ttulo3 nuevos
headings_to_remove = [
    'Groll, Schauberger y Tutz (2015): Poisson regularizado',
    'Groll, Ley, Schauberger y Van Eetvelde (2019): Hybrid Random Forest',
    'Ogundeji, Aleem y Obute (2024): enfoque bayesiano',
    'Posicionamiento del trabajo respecto a la literatura',
]
for h in headings_to_remove:
    idx = content.find(h)
    if idx > 0:
        p_start = content.rfind('<w:p ', 0, idx)
        p_end = content.find('</w:p>', idx) + len('</w:p>')
        content = content[:p_start] + content[p_end:]
        print(f'Eliminado heading: {h[:40]}...')

print(f'\nTamano final: {len(content)}')

with open('docs/unpacked/word/document.xml', 'w', encoding='utf-8') as f:
    f.write(content)

print('Reversion completada.')
