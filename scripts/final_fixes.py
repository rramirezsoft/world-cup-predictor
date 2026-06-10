"""Correcciones finales: intercambiar Fig 5/6, anadir Palabras clave, Keywords, Agradecimientos."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('docs/unpacked/word/document.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. Intercambiar Figura 5 y Figura 6 en pies de figura
#    (El contenido esta en orden correcto, solo los numeros estan mal)
#    Figura 6 (torneos) aparece antes que Figura 5 (ELO) en el doc
#    Solucion: renombrar Figura 6->Figura 5 y viceversa en esa zona
# ============================================================

# Find the two captions
cap5 = 'Figura 5. Top 15 selecciones'
cap6 = 'Figura 6. Distribucion de partidos'

# Check which appears first
pos5 = content.find(cap5)
pos6 = content.find(cap6)

if pos6 < pos5 and pos6 != -1:
    # Fig 6 appears before Fig 5 - they're swapped
    # Swap just the caption numbers
    content = content.replace('Figura 6. Distribucion de partidos', 'FIGSWAP_5. Distribucion de partidos')
    content = content.replace('Figura 5. Top 15 selecciones', 'FIGSWAP_6. Top 15 selecciones')
    content = content.replace('FIGSWAP_5', 'Figura 5')
    content = content.replace('FIGSWAP_6', 'Figura 6')

    # Also swap in the narrative text referencing them
    # Find "Figura 3d" reference text that now says "Figura 6"
    content = content.replace('La Figura 6 desglosa', 'La FIGSWAP_5 desglosa')
    content = content.replace('La Figura 5 muestra el ranking', 'La FIGSWAP_6 muestra el ranking')
    content = content.replace('FIGSWAP_5', 'Figura 5')
    content = content.replace('FIGSWAP_6', 'Figura 6')
    print('Figuras 5/6 intercambiadas OK')
else:
    print(f'Figuras 5/6: pos5={pos5}, pos6={pos6} - no swap needed or not found')

# ============================================================
# 2. Anadir Palabras clave y Keywords
# ============================================================
# Check if they already exist
if 'Palabras clave' not in content and 'palabras clave' not in content:
    # Find after Abstract section
    kw_marker = 'Keywords'
    idx = content.find(kw_marker)
    if idx == -1:
        # Find after the abstract text to add keywords
        abstract_marker = 'The 2026 FIFA World Cup will be the first'
        idx_abs = content.find(abstract_marker)
        if idx_abs != -1:
            p_end = content.find('</w:p>', idx_abs) + len('</w:p>')
            kw_xml = '''
    <w:p w14:paraId="D0000001" w:rsidR="00F917FE" w:rsidRDefault="00F917FE">
      <w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">Keywords: </w:t></w:r>
      <w:r><w:t>machine learning, sports prediction, FIFA World Cup 2026, Monte Carlo simulation, feature engineering, XGBoost.</w:t></w:r>
    </w:p>'''
            content = content[:p_end] + kw_xml + content[p_end:]
            print('Keywords added after Abstract')

    # Find after Resumen text to add Palabras clave
    resumen_kw_marker = 'machine learning, predicci'
    if resumen_kw_marker not in content:
        resumen_marker = 'sistema de predicci\u00f3n deportiva competitivo y reproducible'
        if resumen_marker in content:
            p_end = content.find('</w:p>', content.find(resumen_marker)) + len('</w:p>')
            pc_xml = '''
    <w:p w14:paraId="D0000002" w:rsidR="00F917FE" w:rsidRDefault="00F917FE">
      <w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">Palabras clave: </w:t></w:r>
      <w:r><w:t>aprendizaje autom\u00e1tico, predicci\u00f3n deportiva, Copa Mundial de la FIFA 2026, simulaci\u00f3n Monte Carlo, ingenier\u00eda de variables, XGBoost.</w:t></w:r>
    </w:p>'''
            content = content[:p_end] + pc_xml + content[p_end:]
            print('Palabras clave added after Resumen')
else:
    print('Palabras clave already exists')

# ============================================================
# 3. Anadir Agradecimientos (antes de la Introduccion)
# ============================================================
if 'Agradecimientos' not in content and 'agradecimientos' not in content:
    intro_marker = '1. INTRODUCCI'
    idx_intro = content.find(intro_marker)
    if idx_intro != -1:
        # Find the <w:p that contains the heading
        p_start = content.rfind('<w:p ', 0, idx_intro)

        agr_xml = '''
    <w:p w14:paraId="D0000010" w:rsidR="00F917FE" w:rsidRDefault="00F917FE" w:rsidP="00F917FE">
      <w:pPr><w:pStyle w:val="Ttulo1"/></w:pPr>
      <w:r><w:t>Agradecimientos</w:t></w:r>
    </w:p>
    <w:p w14:paraId="D0000011" w:rsidR="00F917FE" w:rsidRDefault="00F917FE">
      <w:r>
        <w:t>A mi familia, por su apoyo constante durante estos cuatro a\u00f1os de carrera. A mi novia, por su paciencia en los meses de mayor carga de trabajo. A mi tutor Diego, por sus orientaciones y por ayudarme a enfocar este proyecto de la mejor manera posible. Y a todos los que de una forma u otra han contribuido a que este trabajo salga adelante.</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="D0000012" w:rsidR="00F917FE" w:rsidRDefault="00F917FE">
      <w:r><w:br w:type="page"/></w:r>
    </w:p>
'''
        content = content[:p_start] + agr_xml + content[p_start:]
        print('Agradecimientos added')
else:
    print('Agradecimientos already exists')

with open('docs/unpacked/word/document.xml', 'w', encoding='utf-8') as f:
    f.write(content)

print('Final fixes done.')
