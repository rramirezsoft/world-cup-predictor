"""Amplia seccion 2.5 con justificacion de features propias vs literatura."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('docs/unpacked/word/document.xml', 'r', encoding='utf-8') as f:
    content = f.read()

def p(text):
    t = text.replace('&', '&amp;')
    return f'    <w:p w14:paraId="F{hash(text) % 999999:06d}" w:rsidR="002F4A1A" w:rsidRDefault="002F4A1A"><w:r><w:t>{t}</w:t></w:r></w:p>'

# Insertar al final de 2.5 (antes del heading 3.)
marker = 'entender qu\u00e9 caracter\u00edsticas del f\u00fatbol internacional'
idx = content.find(marker)
if idx > 0:
    # Find the end of the paragraph containing this marker
    p_end = content.find('</w:p>', idx) + len('</w:p>')

    nuevos = '\n'.join([
        p('Las variables seleccionadas para este TFG se pueden agrupar en dos bloques seg\u00fan su relaci\u00f3n con la literatura. En el primero est\u00e1n las que son pr\u00e1cticamente universales en cualquier modelo serio de predicci\u00f3n de f\u00fatbol: el rating Elo (o alguna variante equivalente) y el ranking FIFA. Los tres trabajos de referencia analizados en el apartado anterior utilizan alg\u00fan tipo de ranking din\u00e1mico y, como confirma el posterior an\u00e1lisis SHAP, estas variables son las que concentran la mayor parte del poder predictivo del modelo.'),
        p('En el segundo bloque est\u00e1n las variables derivadas del historial de partidos, que la mayor\u00eda de los trabajos acad\u00e9micos revisados no incluyen y que aqu\u00ed se han construido de forma expl\u00edcita. La forma reciente se calcula sobre una ventana deslizante de los \u00faltimos diez partidos de cada selecci\u00f3n, los enfrentamientos directos se limitan a los \u00faltimos cinco para evitar que partidos de hace d\u00e9cadas tengan peso predictivo, las rachas se normalizan a un rango m\u00e1ximo y los d\u00edas de descanso entre partidos se capean para evitar valores extremos en selecciones que llevan mucho tiempo sin competir. Todas estas decisiones se han tomado tras observar los datos y ajustando los par\u00e1metros para que el modelo capture la din\u00e1mica temporal sin sobreajustarse a patrones poco robustos.'),
        p('Por otro lado, se han descartado algunas variables que s\u00ed aparecen en la literatura revisada. Las m\u00e1s relevantes son las variables de plantilla (edad media, n\u00famero de jugadores en Champions League, legionarios en el extranjero, valor de mercado agregado) que utilizan Groll et al. tanto en sus trabajos de 2015 como de 2019. Estas variables han demostrado tener poder predictivo, pero requieren una recopilaci\u00f3n manual partido a partido que complicar\u00eda mucho la reproducibilidad del pipeline. Tambi\u00e9n se han descartado las cuotas de casas de apuestas como entrada del modelo, algo que s\u00ed hacen Groll et al. [9][10] a trav\u00e9s de las variables ODDSET o OddsAbil. La decisi\u00f3n responde a un criterio metodol\u00f3gico: si se incluyen las cuotas como variable, el modelo acaba siendo una versi\u00f3n suavizada de lo que ya hacen las casas de apuestas, lo que limita el valor acad\u00e9mico de la comparaci\u00f3n posterior. En este TFG las cuotas se utilizan solo como baseline externo de validaci\u00f3n en la secci\u00f3n de resultados, no como entrada del modelo.'),
        p('Esta forma de plantear la ingenier\u00eda de variables tiene implicaciones directas sobre las t\u00e9cnicas de interpretabilidad. Dado que gran parte de las variables est\u00e1n correlacionadas entre s\u00ed (el Elo, el ranking FIFA, la forma reciente y la fortaleza de la confederaci\u00f3n son medidas distintas de un mismo fen\u00f3meno subyacente: el nivel del equipo), t\u00e9cnicas como la importancia de permutaci\u00f3n pueden dar resultados enga\u00f1osos. SHAP, al descomponer la predicci\u00f3n de forma aditiva y respetar las interacciones, resulta una elecci\u00f3n m\u00e1s robusta para este contexto. El trabajo de Moustakidis et al. [14] sobre aplicaci\u00f3n de SHAP al an\u00e1lisis de rendimiento de equipos de f\u00fatbol refuerza esta elecci\u00f3n metodol\u00f3gica.'),
    ])

    content = content[:p_end] + '\n' + nuevos + '\n' + content[p_end:]
    print('OK: 2.5 ampliado con justificacion features')
else:
    print('WARN: marcador 2.5 no encontrado')

with open('docs/unpacked/word/document.xml', 'w', encoding='utf-8') as f:
    f.write(content)
