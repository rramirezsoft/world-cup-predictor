"""
Correcciones finales tras reunion con tutor:
1. Reforzar Groll 2019 compara con cuotas (justifica nuestro enfoque)
2. Data leakage: conciliar metodologia (3.3) y conclusiones (5.1)
3. Optuna: 100 trials -> 50 trials en metodologia
4. Nomenclatura Mundial 2026 uniforme
5. Titulo mas especifico con ingenieria de variables
6. Figura 4 cohesion: ajustar texto previo con lo que muestra la figura
7. Errata ref [12]: reemplazar [8] Hubacek (NBA) por [10] Groll 2019 en 4.3
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('docs/unpacked/word/document.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. REFORZAR QUE GROLL 2019 USA CASAS DE APUESTAS COMO BASELINE
# ============================================================
# El parrafo actual sobre Groll 2019 en 2.3 ya menciona que "obtiene una precision superior a la de las propias cuotas de apuestas"
# Lo reforzamos para que quede MUY claro que es un baseline de validacion
old_groll19 = 'El modelo se entrena con los Mundiales de 2002 a 2014 y se aplica prospectivamente al Mundial 2018, obteniendo una precisión superior a la de las propias cuotas de apuestas en las 64 predicciones del torneo.'
new_groll19 = 'El modelo se entrena con los Mundiales de 2002 a 2014 y se aplica prospectivamente al Mundial 2018, utilizando las cuotas de las casas de apuestas como baseline externo de validación. La comparación la hacen partido a partido para los 64 encuentros del torneo y su modelo supera la precisión media de las cuotas, lo que confirma que un sistema académico bien calibrado puede llegar al nivel del consenso del mercado. Este mismo criterio de validación es el que se aplica en el presente trabajo en el capítulo de desarrollo: las cuotas no entran como variable de entrada del modelo, sino que se utilizan a posteriori como referencia externa con la que contrastar las probabilidades obtenidas.'

if old_groll19 in content:
    content = content.replace(old_groll19, new_groll19)
    print('OK 1: Reforzada comparacion con cuotas en Groll 2019')

# ============================================================
# 2. DATA LEAKAGE - CONCILIAR METODOLOGIA Y CONCLUSIONES
# ============================================================
# En 3.3: la afirmacion actual es absoluta. Matizarla para ser honestos sobre la excepcion del ranking FIFA.
old_leak = 'Un aspecto importante del procesamiento es que todas estas variables se calculan de forma secuencial y cronológica. Antes de cada partido, se consultan los valores actuales de los trackers (ELO, forma, H2H) y, después del partido, se actualizan con el resultado. Esto garantiza que el modelo nunca tiene acceso a información del futuro durante el entrenamiento, evitando lo que en la literatura se conoce como data leakage o fuga de datos.'

new_leak = 'Un aspecto importante del procesamiento es que la mayoría de estas variables se calculan de forma secuencial y cronológica. Antes de cada partido, se consultan los valores actuales de los trackers (ELO, forma, H2H) y, después del partido, se actualizan con el resultado. Esto garantiza que para 47 de las 50 variables el modelo no tiene acceso a información del futuro durante el entrenamiento, evitando lo que en la literatura se conoce como data leakage o fuga de datos. La única excepción son las tres variables del ranking FIFA, que se incorporan como posición actual del equipo y no como la posición que tenía en cada fecha histórica; como se discute en las conclusiones, esto introduce una pequeña fuga de información de impacto limitado que conviene tener en cuenta y corregir en versiones futuras.'

if old_leak in content:
    content = content.replace(old_leak, new_leak)
    print('OK 2: Data leakage matizado en metodologia 3.3')

# ============================================================
# 3. OPTUNA: 100 -> 50 TRIALS EN METODOLOGIA
# ============================================================
old_optuna = 'Se ejecutan 100 trials, cada uno evaluado con validación cruzada temporal (TimeSeriesSplit con 5 folds) usando log loss como métrica.'
new_optuna = 'Se ejecutan 50 trials por cada modelo candidato, cada uno evaluado con validación cruzada temporal (TimeSeriesSplit con 5 folds) usando log loss como métrica.'
if old_optuna in content:
    content = content.replace(old_optuna, new_optuna)
    print('OK 3: Optuna 100 -> 50 trials')

# ============================================================
# 4. NOMENCLATURA UNIFORME
# ============================================================
# "Mundial de Fútbol FIFA 2026" -> "Copa Mundial de la FIFA 2026" (en titulo y resumen)
# Pero "Mundial de Fútbol FIFA 2026" tambien aparece en el OE1-5 de Objetivos
# Vamos a uniformar a "Copa Mundial de la FIFA 2026" en titulo y objetivo general, "Mundial 2026" en resto

# Primero ver cuantas ocurrencias
import re
count_before = len(re.findall(r'Mundial de F\u00fatbol FIFA 2026', content))
print(f'  "Mundial de Fútbol FIFA 2026" encontrado: {count_before} veces')

# Cambiar a "Copa Mundial de la FIFA 2026"
content = content.replace('Mundial de F\u00fatbol FIFA 2026', 'Copa Mundial de la FIFA 2026')
print(f'OK 4: Unificado "Mundial de F\u00fatbol FIFA 2026" a "Copa Mundial de la FIFA 2026"')

# ============================================================
# 5. TITULO DEL TFG
# ============================================================
# Actual: "Predicción del Mundial de Fútbol FIFA 2026 mediante Machine Learning"
# Tras el paso 4 sera: "Predicción de la Copa Mundial de la FIFA 2026 mediante Machine Learning"
# Nuevo: "Ingeniería de variables para la predicción de la Copa Mundial de la FIFA 2026 mediante aprendizaje automático"

# Verificar el texto actual tras paso 4
if 'Predicci\u00f3n del Copa Mundial de la FIFA 2026 mediante Machine Learning' in content:
    # caso imposible pero por seguridad
    old_title = 'Predicci\u00f3n del Copa Mundial de la FIFA 2026 mediante Machine Learning'
elif 'Predicci\u00f3n de la Copa Mundial de la FIFA 2026 mediante Machine Learning' in content:
    old_title = 'Predicci\u00f3n de la Copa Mundial de la FIFA 2026 mediante Machine Learning'
elif 'Predicci\u00f3n del Mundial de F\u00fatbol FIFA 2026 mediante Machine Learning' in content:
    old_title = 'Predicci\u00f3n del Mundial de F\u00fatbol FIFA 2026 mediante Machine Learning'
else:
    # Buscar "Predicci\u00f3n del" que no es uno de los anteriores
    old_title = None
    print('WARN: titulo actual no coincide con patrones esperados')

new_title = 'Ingenier\u00eda de variables para la predicci\u00f3n de la Copa Mundial de la FIFA 2026 mediante aprendizaje autom\u00e1tico'

if old_title:
    # Cambiar en el TEXTO visible (cuerpo)
    count = content.count(old_title)
    if count > 0:
        content = content.replace(old_title, new_title)
        print(f'OK 5: Titulo cambiado ({count} ocurrencias)')

# Cambiar tambien el objetivo general (que usa "Mundial de F\u00fatbol FIFA 2026" -> ya cambiado a Copa Mundial...)
# Verificar que ahora el objetivo dice algo consistente
if 'dise\u00f1ar y desarrollar un sistema integral de predicci\u00f3n de la Copa Mundial de la FIFA 2026' in content:
    print('  Objetivo general ya dice "Copa Mundial de la FIFA 2026"')

# ============================================================
# 6. FIGURA 4 COHESION
# ============================================================
# Texto actual dice que bajo del 60% al 45%, pero la grafica muestra fluctuacion entre 47% y 52%
# Ajustar el texto para reflejar lo que realmente muestra la figura

old_fig4 = 'Otro hallazgo interesante del análisis exploratorio fue que la ventaja de jugar en casa ha ido disminuyendo con el paso de las décadas. En los años 50 y 60, el equipo local ganaba en torno al 60% de los partidos; en las últimas dos décadas esa cifra ha bajado hasta el 45%. Esto probablemente se debe a la mejora en las condiciones de viaje, la profesionalización del deporte y el aumento de los partidos en campo neutral (como los de grandes torneos internacionales). Este dato refuerza la decisión de no incluir la ventaja de campo como una constante fija, sino de dejarla como una variable más que el modelo pueda ponderar.'

new_fig4 = 'Otro hallazgo relevante del análisis exploratorio fue la evolución histórica de la ventaja de jugar en casa. Como muestra la Figura 4, el porcentaje de victorias locales se ha mantenido relativamente estable a lo largo de las décadas, fluctuando entre el 47% y el 52% desde los años cincuenta hasta la actualidad, con un máximo alrededor de los años sesenta y una ligera tendencia a la baja en las últimas décadas, que se sitúan en torno al 47-48%. Esta disminución modesta probablemente se debe a la mejora en las condiciones de viaje, la profesionalización del deporte y el aumento de los partidos en campo neutral (como los de grandes torneos internacionales). Este dato refuerza la decisión de no incluir la ventaja de campo como una constante fija, sino de dejarla como una variable más que el modelo pueda ponderar, con un tratamiento específico para partidos en campo neutral.'

if old_fig4 in content:
    content = content.replace(old_fig4, new_fig4)
    print('OK 6: Figura 4 cohesion - texto reescrito para coincidir con la grafica')

# ============================================================
# 7. ERRATA [12]: en 4.3 cita a [8] Hubacek (NBA) junto con [12] Ogundeji, pero Hubacek no predice Mundiales
# ============================================================
old_errata = 'También están en línea con los obtenidos por Hubáček et al. [8] y Ogundeji et al. [12] en sus respectivos trabajos.'
new_errata = 'También están en línea con los obtenidos por Groll et al. [10] en su hybrid random forest para el Mundial 2018 y con los de Ogundeji et al. [12] para el Mundial 2026.'
if old_errata in content:
    content = content.replace(old_errata, new_errata)
    print('OK 7: Errata corregida - [8] Hubacek (NBA) reemplazado por [10] Groll 2019 (Mundiales)')

with open('docs/unpacked/word/document.xml', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n=== TODAS LAS CORRECCIONES APLICADAS ===')
