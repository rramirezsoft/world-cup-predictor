"""
Amplia seccion 2 (Estado de la cuestion) con analisis profundo de 3 papers cientificos:
- Groll, Ley, Schauberger y Van Eetvelde (2019) - Hybrid Random Forest
- Groll, Schauberger y Tutz (2015) - Regularized Poisson
- Ogundeji, Aleem y Obute (2024) - Bayesian WC 2026

Anade:
- Ampliacion 2.2 ELO con variantes literatura
- Nueva seccion 2.3 reescrita con analisis profundo por papers
- Tabla semaforo comparativa de features en 2.5
- Justificacion de features propias contra literatura
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('docs/unpacked/word/document.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# FIX 1: Corregir "Boussouf" por "Ogundeji, Aleem y Obute" en cuerpo texto
# ============================================================
if 'Boussouf' in content:
    # Only in body text, not in bibliography entry (already fixed)
    # Bibliography already says "R. Ogundeji, A. Aleem y D. Obute"
    content = content.replace('Boussouf [12]', 'Ogundeji et al. [12]')
    print('OK: Boussouf corregido a Ogundeji et al. en cuerpo de texto')

# ============================================================
# AMPLIACION 2.2 ELO - Anadir parrafos sobre variantes y uso en literatura
# ============================================================
# Insertar despues del parrafo que menciona Hvattum y Arntzen [5]
marker_22 = 'refletz\u00f3 su adopci\u00f3n en modelos acad\u00e9micos'
# Try ascii versions
marker_22_alt = 'reforz\u00f3 su adopci\u00f3n en modelos acad\u00e9micos'

for marker in [marker_22, marker_22_alt, 'adopci\u00f3n en modelos']:
    idx = content.find(marker)
    if idx > 0:
        p_end = content.find('</w:p>', idx) + len('</w:p>')
        new_22 = '''
    <w:p w14:paraId="E0000001" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A"><w:r><w:t>El uso del ELO en f&#xFA;tbol presenta varias diferencias importantes respecto al ajedrez original, y la literatura ha explorado distintas variantes. El trabajo de Hvattum y Arntzen [5] ya introduc&#xED;a el peso por importancia del partido (un amistoso cuenta menos que una final de torneo), mientras que World Football Elo Ratings [19] a&#xF1;ade un multiplicador por diferencia de goles y una correcci&#xF3;n por campo local de 100 puntos. Dixon y Coles [3] plantean una alternativa radicalmente distinta: en lugar de un rating agregado, utilizan dos par&#xE1;metros por equipo (ataque y defensa) que se estiman por m&#xE1;xima verosimilitud y se combinan con un decaimiento exponencial que da m&#xE1;s peso a los partidos recientes. Groll et al. [9][10] combinan el ranking FIFA (que desde 2018 tambi&#xE9;n es un sistema tipo Elo) con ratings de tipo Poisson estimados internamente, lo que da lugar a sus llamados hybrid random forests.</w:t></w:r></w:p>
    <w:p w14:paraId="E0000002" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A"><w:r><w:t>En el presente trabajo se opta por un sistema Elo propio, construido desde cero a partir del historial de partidos, con tres diferencias principales respecto al Elo est&#xE1;ndar de ajedrez. Primero, se pondera cada partido por un coeficiente de importancia del torneo que va de 0,6 (amistoso) a 1,5 (Mundial); esta idea es similar a la de Hvattum y Arntzen [5] y a la del proyecto World Football Elo Ratings, aunque los coeficientes concretos se han ajustado tras observar c&#xF3;mo evoluciona el ranking resultante. Segundo, se incluye un multiplicador por diferencia de goles, tambi&#xE9;n en l&#xED;nea con eloratings.net, que incrementa el cambio de rating cuando una selecci&#xF3;n vence por un margen amplio. Tercero, y a diferencia de la literatura revisada, se a&#xF1;ade una ligera regresi&#xF3;n hacia la media del 0,3% despu&#xE9;s de cada actualizaci&#xF3;n, que act&#xFA;a como un freno suave y evita que los ratings se disparen para selecciones con rachas at&#xED;picas en partidos de baja importancia.</w:t></w:r></w:p>
    <w:p w14:paraId="E0000003" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A"><w:r><w:t>Esta decisi&#xF3;n de construir un Elo propio en lugar de utilizar directamente el de eloratings.net o el ranking FIFA responde a tres consideraciones. Por un lado, se necesita un rating que pueda calcularse y actualizarse partido a partido dentro del pipeline, sin depender de un servicio externo. Por otro, permite controlar los par&#xE1;metros (factor K, ventaja de campo, pesos por torneo) para ajustarlos al tipo de problema. Y, finalmente, usar el ranking FIFA y el Elo propio como variables separadas aporta m&#xE1;s informaci&#xF3;n al modelo que utilizar solo una de las dos: ambos miden el nivel del equipo, pero lo hacen con f&#xF3;rmulas distintas y el modelo puede aprender a combinarlas.</w:t></w:r></w:p>'''
        content = content[:p_end] + new_22 + content[p_end:]
        print('OK: 2.2 ELO ampliado con variantes literatura')
        break
else:
    print('WARN: Marcador 2.2 no encontrado')

# ============================================================
# AMPLIACION 2.3: Insertar analisis profundo de 3 papers
# Insertar antes del heading 2.4
# ============================================================
marker_24 = '2.4 Simulaci'
idx_24 = content.find(marker_24)
if idx_24 > 0:
    # Ir al w:p que contiene el heading 2.4
    p_start = content.rfind('<w:p ', 0, idx_24)

    analisis = '''
    <w:p w14:paraId="E0000010" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:pPr><w:pStyle w:val="Ttulo3"/></w:pPr>
      <w:r><w:t>An&#xE1;lisis comparado de trabajos de referencia</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E0000011" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:r><w:t>Tres trabajos merecen un an&#xE1;lisis en profundidad por su proximidad metodol&#xF3;gica y tem&#xE1;tica con el presente TFG. Se trata de Groll, Schauberger y Tutz [9], que modelan el Mundial 2014 mediante regresi&#xF3;n de Poisson regularizada con LASSO; Groll, Ley, Schauberger y Van Eetvelde [10], que introducen el concepto de hybrid random forest combinando random forests con rankings basados en Poisson y en cuotas de apuestas; y Ogundeji, Aleem y Obute [12], que aplican regresi&#xF3;n log&#xED;stica bayesiana y gradient boosting al pron&#xF3;stico del Mundial 2026. Estos tres estudios son los que marcan el estado del arte en predicci&#xF3;n de Mundiales y sirven como referencia para posicionar las decisiones tomadas en este trabajo.</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E0000012" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:pPr><w:pStyle w:val="Ttulo3"/></w:pPr>
      <w:r><w:t>Groll, Schauberger y Tutz (2015): Poisson regularizado para el Mundial 2014</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E0000013" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:r><w:t>Este trabajo utiliza un modelo de regresi&#xF3;n de Poisson con efectos team-specific regularizados mediante Group LASSO para predecir el n&#xFA;mero de goles que anotar&#xE1; cada selecci&#xF3;n en cada partido. Como variables predictoras emplean: factores econ&#xF3;micos (PIB per c&#xE1;pita, poblaci&#xF3;n), el ranking FIFA, las cuotas del operador alem&#xE1;n ODDSET, factores de ventaja de campo (selecci&#xF3;n anfitriona y pertenencia al mismo continente que el anfitri&#xF3;n) y variables que describen la estructura de la plantilla de 23 jugadores (m&#xE1;ximo y segundo m&#xE1;ximo de compa&#xF1;eros en un mismo club, edad media, n&#xFA;mero de jugadores en semifinales de Champions o Europa League, n&#xFA;mero de jugadores en ligas extranjeras), adem&#xE1;s de variables sobre el seleccionador (edad, a&#xF1;os de permanencia en el cargo, nacionalidad). Sus resultados se&#xF1;alan que las variables m&#xE1;s relevantes tras la regularizaci&#xF3;n son las cuotas ODDSET, el ranking FIFA y el n&#xFA;mero de jugadores en Champions League.</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E0000014" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:r><w:t>La principal diferencia con este trabajo es el tipo de variables que utilizan. Groll et al. dedican una parte importante de su esfuerzo a recopilar manualmente datos de plantilla desde kicker.de y transfermarkt.de, y a integrar datos econ&#xF3;micos del Banco Mundial. El presente TFG sigue una l&#xED;nea distinta: se apoya exclusivamente en el historial de partidos internacionales y construye sobre esos datos indicadores din&#xE1;micos (Elo, forma reciente, H2H), renunciando a variables est&#xE1;ticas de plantilla y econom&#xED;a. Esta decisi&#xF3;n simplifica la reproducibilidad y permite actualizar el modelo autom&#xE1;ticamente cuando se a&#xF1;aden nuevos partidos, a costa de perder la informaci&#xF3;n que s&#xED; aportan las variables de valor de mercado y plantilla.</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E0000015" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:pPr><w:pStyle w:val="Ttulo3"/></w:pPr>
      <w:r><w:t>Groll, Ley, Schauberger y Van Eetvelde (2019): Hybrid Random Forest</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E0000016" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:r><w:t>En este trabajo los autores combinan random forests con dos rankings externos: uno basado en una regresi&#xF3;n de Poisson ajustada sobre todo el historial reciente de partidos internacionales (denotado PoisAbil), y otro basado en el bookmaker consensus de Leitner et al. a partir de cuotas agregadas de varias casas (OddsAbil). El random forest recibe como entrada las variables cl&#xE1;sicas de Groll et al. [9] (estructura de plantilla, factores econ&#xF3;micos, ranking FIFA) y a&#xF1;ade estas dos variables de ranking, que funcionan como una especie de resumen din&#xE1;mico del nivel de cada equipo. Aplican el modelo a los Mundiales femeninos de 2011 y 2015 y lo validan prediciendo el de 2019.</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E0000017" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:r><w:t>Este enfoque h&#xED;brido es conceptualmente similar al que se sigue en este TFG: en ambos casos se utilizan rankings din&#xE1;micos del nivel del equipo junto con otras variables descriptivas, y en ambos casos la variable del ranking es la que domina la importancia en el modelo. La diferencia principal es que Groll et al. construyen el ranking con regresi&#xF3;n de Poisson y lo combinan con cuotas de apuestas, mientras que aqu&#xED; se utiliza un Elo propio con pesos por torneo y regresi&#xF3;n a la media, complementado con el ranking FIFA oficial. Otra diferencia relevante es el algoritmo: Groll et al. utilizan random forests mientras que aqu&#xED; se emplea XGBoost, que en la literatura reciente tiende a obtener mejores resultados sobre este tipo de tareas tabulares [11].</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E0000018" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:pPr><w:pStyle w:val="Ttulo3"/></w:pPr>
      <w:r><w:t>Ogundeji, Aleem y Obute (2024): enfoque bayesiano para el Mundial 2026</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E0000019" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:r><w:t>Este es el trabajo m&#xE1;s cercano tem&#xE1;ticamente, ya que aborda exactamente el mismo problema (el Mundial 2026) aunque con un enfoque metodol&#xF3;gico diferente. Los autores combinan una regresi&#xF3;n log&#xED;stica bayesiana con CatBoost (gradient boosting) sobre un dataset de aproximadamente 23.921 partidos obtenido de Kaggle y FIFA. Las variables que utilizan incluyen el ranking FIFA, los puntos FIFA, el equipo local y visitante, detalles del torneo y factores geogr&#xE1;ficos. En sus an&#xE1;lisis destacan que la distribuci&#xF3;n de resultados se reparte en un 49,2% de victorias locales, 28,3% de visitantes y 22,5% de empates, cifras pr&#xE1;cticamente id&#xE9;nticas a las observadas en el presente trabajo (49,0%, 28,3% y 22,8% respectivamente). Sus principales favoritos son Brasil, B&#xE9;lgica, Francia, Argentina e Inglaterra.</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E000001A" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:r><w:t>Las diferencias con el presente TFG son significativas en cuanto a variables predictoras. Ogundeji et al. se apoyan fundamentalmente en rankings oficiales y atributos categ&#xF3;ricos (nombre del equipo, tipo de torneo, ubicaci&#xF3;n), sin construir indicadores din&#xE1;micos derivados del historial. Tampoco utilizan un sistema Elo propio ni variables de forma reciente, confederaci&#xF3;n o enfrentamientos directos. En ese sentido, puede considerarse que su modelo es m&#xE1;s compacto pero potencialmente menos expresivo para capturar la din&#xE1;mica temporal del nivel de las selecciones. Por otro lado, su enfoque bayesiano tiene la ventaja de incorporar expl&#xED;citamente la incertidumbre en las predicciones, algo que en este trabajo se aborda de forma indirecta mediante la simulaci&#xF3;n Monte Carlo y la calibraci&#xF3;n isot&#xF3;nica de las probabilidades.</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E000001B" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:pPr><w:pStyle w:val="Ttulo3"/></w:pPr>
      <w:r><w:t>Posicionamiento del trabajo respecto a la literatura</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E000001C" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:r><w:t>Comparando los tres trabajos anteriores con el presente TFG se observa que existen varias decisiones de dise&#xF1;o propias que conviene justificar. La primera es la renuncia deliberada a las variables de plantilla y mercado: Groll et al. demuestran que a&#xF1;aden poder predictivo, pero requieren una recopilaci&#xF3;n manual que dif&#xED;cilmente se puede automatizar y que pone en cuesti&#xF3;n la reproducibilidad del pipeline. La segunda es la construcci&#xF3;n de un sistema Elo propio en lugar de depender de rankings externos, lo que da control total sobre los par&#xE1;metros y permite a&#xF1;adir correcciones (regresi&#xF3;n a la media) que en la literatura revisada no aparecen. La tercera es la inclusi&#xF3;n de variables de contexto que los trabajos acad&#xE9;micos revisados tienden a omitir, como las rachas, los d&#xED;as de descanso, el porcentaje de porter&#xED;as a cero o la experiencia en grandes torneos; estas variables no tienen un impacto dominante (como se ver&#xE1; en el an&#xE1;lisis SHAP), pero aportan matices &#xFA;tiles en partidos igualados.</w:t></w:r>
    </w:p>
    <w:p w14:paraId="E000001D" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A">
      <w:r><w:t>La Tabla 3 presenta una comparativa visual entre las variables utilizadas en este trabajo y las tres referencias analizadas, distinguiendo entre variables comunes, variantes de una misma idea y variables espec&#xED;ficas de cada enfoque. Esta comparativa no pretende evaluar qu&#xE9; conjunto es mejor (los trabajos no son directamente comparables porque parten de datasets y problemas distintos), sino situar las decisiones tomadas en este TFG dentro de la literatura existente.</w:t></w:r>
    </w:p>'''
    # Insert BEFORE heading 2.4
    content = content[:p_start] + analisis + '\n' + content[p_start:]
    print('OK: Analisis profundo 3 papers insertado antes de 2.4')
else:
    print('WARN: heading 2.4 no encontrado')

# ============================================================
# TABLA 3 SEMAFORO: Comparativa features. Insertar despues de la ampliacion 2.3 (al final del ultimo parrafo insertado)
# ============================================================
marker_tabla = 'dentro de la literatura existente'
idx_tabla = content.find(marker_tabla)
if idx_tabla > 0:
    p_end = content.find('</w:p>', idx_tabla) + len('</w:p>')

    VERDE = 'C6EFCE'  # Verde claro (coincide)
    AMARILLO = 'FFEB9C'  # Amarillo claro (variante)
    ROJO = 'FFC7CE'  # Rojo claro (no coincide)
    GRIS = 'D9D9D9'  # Cabecera

    # Crear celdas reutilizables
    def cell(text, width, fill=None, bold=False, header=False):
        shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ''
        b_tag = '<w:b/>' if bold else ''
        sz = '<w:sz w:val="18"/>'
        return f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shd}</w:tcPr><w:p><w:pPr><w:spacing w:before="20" w:after="20"/><w:jc w:val="center"/><w:rPr>{b_tag}{sz}</w:rPr></w:pPr><w:r><w:rPr>{b_tag}{sz}</w:rPr><w:t>{text}</w:t></w:r></w:p></w:tc>'

    # Filas: familia, este TFG, Groll 2015, Groll 2019 (RF), Ogundeji 2024
    rows_data = [
        # (familia, TFG, G15, G19, O24)
        ('Rating ELO propio', ('V', 'Elo con pesos torneo, mult. goles y regresi\u00f3n media'),
         ('R', 'No usan Elo'),
         ('A', 'PoisAbil: ranking Poisson propio'),
         ('R', 'No usan Elo')),
        ('Ranking FIFA', ('V', 'Posici\u00f3n local, visitante, diferencia'),
         ('V', 'Ranking FIFA como covariable'),
         ('V', 'Inclu\u00eddo entre covariables'),
         ('V', 'Ranking y puntos FIFA')),
        ('Forma reciente (\u00faltimos 10 partidos)', ('V', 'Victorias/empates/derrotas, goles, puntos'),
         ('R', 'No incluida como tal'),
         ('R', 'No incluida como tal'),
         ('A', 'Forma mencionada sin ventana fija')),
        ('Enfrentamientos directos (H2H)', ('V', '\u00daltimos 5 enfrentamientos'),
         ('R', 'No'),
         ('R', 'No'),
         ('R', 'No')),
        ('Cuotas de casas de apuestas', ('R', 'No como entrada del modelo'),
         ('V', 'Cuotas ODDSET'),
         ('V', 'OddsAbil (Leitner et al.)'),
         ('R', 'No')),
        ('Valor mercado / plantilla', ('R', 'No'),
         ('V', 'Edad media, jugadores CL, jugadores extranjero'),
         ('V', 'Mismas variables de plantilla'),
         ('R', 'No')),
        ('Factores econ\u00f3micos (PIB, poblaci\u00f3n)', ('R', 'No'),
         ('V', 'PIB per c\u00e1pita y poblaci\u00f3n'),
         ('V', 'PIB y poblaci\u00f3n'),
         ('R', 'No')),
        ('Ventaja de campo / anfitri\u00f3n', ('V', 'Campo neutral y bonus de 100 ELO'),
         ('V', 'Dummy host y continente'),
         ('V', 'Dummy host y continente'),
         ('A', 'S\u00f3lo localizaci\u00f3n geogr\u00e1fica')),
        ('Importancia del torneo', ('V', 'Peso por tipo (0,6-1,5)'),
         ('A', 'Implicita en selecci\u00f3n de partidos'),
         ('A', 'Implicita en selecci\u00f3n de partidos'),
         ('A', 'Detalles del torneo como categ\u00f3rica')),
        ('Confederaci\u00f3n y fortaleza regional', ('V', 'Fortaleza local, visitante, inter-conf'),
         ('A', 'Continente del anfitri\u00f3n'),
         ('A', 'Confederaci\u00f3n del equipo'),
         ('R', 'No')),
        ('Rachas (win / unbeaten streak)', ('V', 'Positiva y negativa por equipo'),
         ('R', 'No'),
         ('R', 'No'),
         ('R', 'No')),
        ('D\u00edas de descanso entre partidos', ('V', 'Local, visitante y diferencia'),
         ('R', 'No'),
         ('R', 'No'),
         ('R', 'No')),
        ('Experiencia en grandes torneos', ('V', 'Contador por equipo'),
         ('A', 'Participaciones previas en WC'),
         ('R', 'No'),
         ('R', 'No')),
        ('Fase eliminatoria (knockout)', ('V', 'Dummy'),
         ('R', 'No usada'),
         ('V', 'Dummy group vs knockout'),
         ('R', 'No')),
    ]

    # Construir tabla XML
    widths = [2800, 1500, 1500, 1500, 1500]
    total_w = sum(widths)

    rows_xml = []
    # Header row
    header_cells = [
        cell('Familia de variable', widths[0], fill=GRIS, bold=True),
        cell('Este TFG', widths[1], fill=GRIS, bold=True),
        cell('Groll et al. 2015 [9]', widths[2], fill=GRIS, bold=True),
        cell('Groll et al. 2019 [10]', widths[3], fill=GRIS, bold=True),
        cell('Ogundeji et al. 2024 [12]', widths[4], fill=GRIS, bold=True),
    ]
    rows_xml.append(f'<w:tr><w:trPr><w:jc w:val="center"/></w:trPr>{"".join(header_cells)}</w:tr>')

    color_map = {'V': VERDE, 'A': AMARILLO, 'R': ROJO}

    for family, tfg, g15, g19, o24 in rows_data:
        row_cells = [cell(family, widths[0])]
        for code, desc in [tfg, g15, g19, o24]:
            row_cells.append(cell(desc, widths[1] if code != 'family' else widths[0], fill=color_map[code]))
        rows_xml.append(f'<w:tr><w:trPr><w:jc w:val="center"/></w:trPr>{"".join(row_cells)}</w:tr>')

    rows_str = ''.join(rows_xml)

    tabla_xml = f'''
    <w:tbl>
      <w:tblPr>
        <w:tblStyle w:val="Tablaconcuadrcula"/>
        <w:tblW w:w="{total_w}" w:type="dxa"/>
        <w:jc w:val="center"/>
        <w:tblBorders>
          <w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>
        </w:tblBorders>
      </w:tblPr>
      {rows_str}
    </w:tbl>
    <w:p w14:paraId="E000002A" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A"><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:i/><w:sz w:val="20"/></w:rPr><w:t>Tabla 3. Comparativa de familias de variables: verde indica coincidencia directa, amarillo variante de una misma idea, rojo ausencia en ese trabajo. Elaboraci&#xF3;n propia.</w:t></w:r></w:p>
'''

    content = content[:p_end] + tabla_xml + content[p_end:]
    print('OK: Tabla 3 semaforo insertada')

with open('docs/unpacked/word/document.xml', 'w', encoding='utf-8') as f:
    f.write(content)

print('\nExpansion estado del arte completada.')
