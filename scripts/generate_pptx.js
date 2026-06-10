// Presentación de defensa del TFG
// Ingeniería de variables para la predicción de la Copa Mundial de la FIFA 2026
const pptxgen = require("pptxgenjs");
const path = require("path");

const pptx = new pptxgen();

// ============================================================
// CONFIGURACIÓN GLOBAL
// ============================================================
pptx.layout = "LAYOUT_WIDE";  // 13.33 x 7.5 inches (16:9)
pptx.author = "Raúl Ramírez Adarve";
pptx.company = "U-tad";
pptx.title = "TFG - Predicción Mundial 2026";

// Paleta de colores: Midnight Executive con acento deportivo
const COLORS = {
  navy: "0F1A2E",       // dominante
  navyLight: "1E2761",
  red: "C0392B",        // acento deportivo
  redLight: "E74C3C",
  gold: "C9A227",       // detalle premium
  cream: "F8F6F1",      // fondo claro
  textDark: "1A1A1A",
  textGray: "555555",
  textMuted: "8B8B8B",
  white: "FFFFFF",
  green: "27AE60",      // accent positivo
  divider: "E5E2DC",
};

const FONTS = {
  title: "Georgia",
  body: "Calibri",
  mono: "Consolas",
};

const OUT = path.resolve(__dirname, "..", "outputs");

// Helpers ====================================================
function addFooter(slide, pageNum, total) {
  // Línea sutil arriba del pie
  slide.addShape("line", {
    x: 0.5, y: 7.05, w: 12.33, h: 0,
    line: { color: COLORS.divider, width: 0.5 },
  });
  slide.addText("TFG · Raúl Ramírez Adarve · 2026", {
    x: 0.5, y: 7.1, w: 8, h: 0.3,
    fontFace: FONTS.body, fontSize: 9, color: COLORS.textMuted,
    align: "left",
  });
  slide.addText(`${pageNum} / ${total}`, {
    x: 11.83, y: 7.1, w: 1, h: 0.3,
    fontFace: FONTS.body, fontSize: 9, color: COLORS.textMuted,
    align: "right",
  });
}

function darkSlide(slide) {
  slide.background = { color: COLORS.navy };
  // Banda lateral roja
  slide.addShape("rect", {
    x: 0, y: 0, w: 0.25, h: 7.5,
    fill: { color: COLORS.red }, line: { color: COLORS.red },
  });
}

function lightSlide(slide) {
  slide.background = { color: COLORS.cream };
  // Banda lateral roja fina
  slide.addShape("rect", {
    x: 0, y: 0, w: 0.18, h: 7.5,
    fill: { color: COLORS.red }, line: { color: COLORS.red },
  });
}

function sectionHeader(slide, sectionNum, sectionTitle) {
  // Etiqueta de sección pequeña
  slide.addShape("rect", {
    x: 0.6, y: 0.55, w: 0.5, h: 0.4,
    fill: { color: COLORS.red }, line: { color: COLORS.red },
  });
  slide.addText(`0${sectionNum}`, {
    x: 0.6, y: 0.55, w: 0.5, h: 0.4,
    fontFace: FONTS.title, fontSize: 14, color: COLORS.white,
    bold: true, align: "center", valign: "middle",
  });
  slide.addText(sectionTitle.toUpperCase(), {
    x: 1.25, y: 0.6, w: 6, h: 0.35,
    fontFace: FONTS.body, fontSize: 10, color: COLORS.textMuted,
    bold: true, charSpacing: 2,
  });
}

function slideTitle(slide, title) {
  slide.addText(title, {
    x: 0.6, y: 1.0, w: 12, h: 0.8,
    fontFace: FONTS.title, fontSize: 32, color: COLORS.navy,
    bold: true, align: "left",
  });
}

const TOTAL = 15;

// ============================================================
// SLIDE 1 — PORTADA
// ============================================================
{
  const s = pptx.addSlide();
  darkSlide(s);

  // Etiqueta superior
  s.addText("TRABAJO DE FIN DE GRADO · INGENIERÍA DEL SOFTWARE", {
    x: 0.7, y: 0.7, w: 12, h: 0.4,
    fontFace: FONTS.body, fontSize: 11, color: COLORS.gold,
    bold: true, charSpacing: 3,
  });

  // Año grande tipo deportivo
  s.addText("FIFA 2026", {
    x: 0.6, y: 1.4, w: 6, h: 1.2,
    fontFace: FONTS.title, fontSize: 64, color: COLORS.red,
    bold: true, italic: true,
  });

  // Título completo
  s.addText("Ingeniería de variables para la predicción\nde la Copa Mundial de la FIFA 2026\nmediante aprendizaje automático", {
    x: 0.7, y: 2.8, w: 12, h: 2.0,
    fontFace: FONTS.title, fontSize: 28, color: COLORS.white,
    bold: true, lineSpacingMultiple: 1.15,
  });

  // Línea separadora
  s.addShape("rect", {
    x: 0.7, y: 5.0, w: 1.5, h: 0.04,
    fill: { color: COLORS.red }, line: { color: COLORS.red },
  });

  // Datos
  s.addText([
    { text: "Autor: ", options: { bold: true, color: COLORS.gold } },
    { text: "Raúl Ramírez Adarve", options: { color: COLORS.white } },
  ], { x: 0.7, y: 5.25, w: 9, h: 0.4, fontFace: FONTS.body, fontSize: 16 });

  s.addText([
    { text: "Tutor: ", options: { bold: true, color: COLORS.gold } },
    { text: "Diego Rojo García", options: { color: COLORS.white } },
  ], { x: 0.7, y: 5.65, w: 9, h: 0.4, fontFace: FONTS.body, fontSize: 16 });

  s.addText([
    { text: "Convocatoria: ", options: { bold: true, color: COLORS.gold } },
    { text: "Ordinaria · Abril 2026", options: { color: COLORS.white } },
  ], { x: 0.7, y: 6.05, w: 9, h: 0.4, fontFace: FONTS.body, fontSize: 16 });

  // Footer estilo defensa
  s.addText("U-tad · Centro Universitario de Tecnología y Arte Digital", {
    x: 0.7, y: 6.85, w: 12, h: 0.3,
    fontFace: FONTS.body, fontSize: 10, color: COLORS.textMuted,
    italic: true,
  });
}

// ============================================================
// SLIDE 2 — JUSTIFICACIÓN Y CONTEXTO
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 1, "Introducción");
  slideTitle(s, "Por qué este trabajo");

  // 3 stat callouts grandes
  const stats = [
    { num: "1.500M", label: "espectadores en la final\nde Catar 2022" },
    { num: "48", label: "selecciones en 2026\n(antes 32)" },
    { num: "104", label: "partidos en total\n(antes 64)" },
  ];

  stats.forEach((stat, i) => {
    const x = 0.7 + i * 4.2;
    // Caja
    s.addShape("rect", {
      x, y: 2.3, w: 3.8, h: 3.0,
      fill: { color: COLORS.white }, line: { color: COLORS.divider, width: 1 },
    });
    // Número grande
    s.addText(stat.num, {
      x, y: 2.5, w: 3.8, h: 1.5,
      fontFace: FONTS.title, fontSize: 56, color: COLORS.red,
      bold: true, align: "center",
    });
    // Etiqueta
    s.addText(stat.label, {
      x: x + 0.2, y: 4.1, w: 3.4, h: 1.0,
      fontFace: FONTS.body, fontSize: 14, color: COLORS.textDark,
      align: "center", lineSpacingMultiple: 1.3,
    });
  });

  // Frase de cierre
  s.addText("Un torneo inédito, con un formato que jamás se ha disputado y del que apenas existen predicciones públicas consolidadas.", {
    x: 0.7, y: 5.7, w: 12.0, h: 1.0,
    fontFace: FONTS.title, fontSize: 18, color: COLORS.navy,
    italic: true, align: "center", lineSpacingMultiple: 1.2,
  });

  addFooter(s, 2, TOTAL);
}

// ============================================================
// SLIDE 3 — OBJETIVOS
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 1, "Introducción");
  slideTitle(s, "Objetivos del trabajo");

  // Objetivo general
  s.addShape("rect", {
    x: 0.7, y: 1.95, w: 11.9, h: 0.9,
    fill: { color: COLORS.navy }, line: { color: COLORS.navy },
  });
  s.addText("OG", {
    x: 0.85, y: 1.95, w: 0.6, h: 0.9,
    fontFace: FONTS.title, fontSize: 22, color: COLORS.gold,
    bold: true, align: "center", valign: "middle",
  });
  s.addText("Diseñar y desarrollar un sistema integral de predicción del Mundial 2026 que combine machine learning, simulación Monte Carlo y una aplicación web de visualización.", {
    x: 1.5, y: 1.95, w: 11.0, h: 0.9,
    fontFace: FONTS.body, fontSize: 14, color: COLORS.white,
    valign: "middle", lineSpacingMultiple: 1.15,
  });

  // 5 OEs en grid 5 columnas
  const oes = [
    { num: "OE1", txt: "Construir un conjunto amplio de variables predictivas." },
    { num: "OE2", txt: "Evaluar algoritmos de ML y seleccionar el mejor." },
    { num: "OE3", txt: "Implementar simulador del torneo con formato 48 equipos." },
    { num: "OE4", txt: "Desarrollar aplicación web interactiva." },
    { num: "OE5", txt: "Contrastar las predicciones con casas de apuestas." },
  ];

  oes.forEach((oe, i) => {
    const x = 0.7 + i * 2.42;
    s.addShape("rect", {
      x, y: 3.2, w: 2.25, h: 3.0,
      fill: { color: COLORS.white }, line: { color: COLORS.divider, width: 1 },
    });
    // Círculo con número
    s.addShape("ellipse", {
      x: x + 0.85, y: 3.4, w: 0.6, h: 0.6,
      fill: { color: COLORS.red }, line: { color: COLORS.red },
    });
    s.addText(`${i+1}`, {
      x: x + 0.85, y: 3.4, w: 0.6, h: 0.6,
      fontFace: FONTS.title, fontSize: 22, color: COLORS.white,
      bold: true, align: "center", valign: "middle",
    });
    // Etiqueta OE
    s.addText(oe.num, {
      x, y: 4.15, w: 2.25, h: 0.35,
      fontFace: FONTS.body, fontSize: 11, color: COLORS.red,
      bold: true, align: "center", charSpacing: 1,
    });
    // Texto
    s.addText(oe.txt, {
      x: x + 0.15, y: 4.55, w: 1.95, h: 1.55,
      fontFace: FONTS.body, fontSize: 12, color: COLORS.textDark,
      align: "center", lineSpacingMultiple: 1.25,
    });
  });

  addFooter(s, 3, TOTAL);
}

// ============================================================
// SLIDE 4 — AUTORES Y TIMELINE
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 2, "Estado de la cuestión");
  slideTitle(s, "Autores y trabajos de referencia");

  // Timeline horizontal
  const events = [
    { year: "1997", name: "Dixon & Coles", desc: "Modelo Poisson ataque/defensa" },
    { year: "2010", name: "Hvattum & Arntzen", desc: "ELO supera a FIFA ranking" },
    { year: "2015", name: "Groll, Schauberger & Tutz", desc: "Poisson + LASSO (WC 2014)", highlight: true },
    { year: "2019", name: "Groll, Ley et al.", desc: "Hybrid Random Forest (WC 2018)", highlight: true },
    { year: "2024", name: "Ogundeji, Aleem & Obute", desc: "Bayesian + CatBoost (WC 2026)", highlight: true },
  ];

  // Línea base
  s.addShape("rect", {
    x: 0.9, y: 4.2, w: 11.5, h: 0.04,
    fill: { color: COLORS.navy }, line: { color: COLORS.navy },
  });

  events.forEach((ev, i) => {
    const x = 0.9 + i * 2.4;
    // Punto
    const dotColor = ev.highlight ? COLORS.red : COLORS.navy;
    s.addShape("ellipse", {
      x: x + 0.85, y: 4.05, w: 0.3, h: 0.3,
      fill: { color: dotColor }, line: { color: dotColor },
    });
    // Año
    s.addText(ev.year, {
      x, y: 2.4, w: 2.0, h: 0.5,
      fontFace: FONTS.title, fontSize: 26, color: ev.highlight ? COLORS.red : COLORS.navy,
      bold: true, align: "center",
    });
    // Autor
    s.addText(ev.name, {
      x, y: 2.9, w: 2.0, h: 0.4,
      fontFace: FONTS.body, fontSize: 12, color: COLORS.textDark,
      bold: true, align: "center",
    });
    // Descripción
    s.addText(ev.desc, {
      x, y: 3.25, w: 2.0, h: 0.6,
      fontFace: FONTS.body, fontSize: 10, color: COLORS.textGray,
      align: "center", italic: true, lineSpacingMultiple: 1.2,
    });
  });

  // Caja inferior con los 3 papers clave
  s.addShape("rect", {
    x: 0.7, y: 5.0, w: 11.9, h: 1.6,
    fill: { color: COLORS.navy }, line: { color: COLORS.navy },
  });
  s.addText("3 papers analizados en profundidad:", {
    x: 0.9, y: 5.1, w: 11.5, h: 0.4,
    fontFace: FONTS.title, fontSize: 14, color: COLORS.gold, bold: true,
  });

  // 3 cajas internas
  const papers = [
    { who: "Groll 2015", what: "Poisson regularizado para WC 2014" },
    { who: "Groll 2019", what: "Hybrid Random Forest para WC 2018" },
    { who: "Ogundeji 2024", what: "Bayesian para WC 2026" },
  ];
  papers.forEach((p, i) => {
    const x = 0.9 + i * 3.9;
    s.addText([
      { text: p.who + "  ", options: { color: COLORS.red, bold: true } },
      { text: p.what, options: { color: COLORS.white } },
    ], { x, y: 5.55, w: 3.8, h: 0.9, fontFace: FONTS.body, fontSize: 12, valign: "top", lineSpacingMultiple: 1.3 });
  });

  addFooter(s, 4, TOTAL);
}

// ============================================================
// SLIDE 5 — TABLA SEMÁFORO (LA CLAVE DEL ESTADO DEL ARTE)
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 2, "Estado de la cuestión");
  slideTitle(s, "Comparativa de variables con los 3 papers");

  // Tabla resumida (8 familias clave de 14)
  const rows = [
    ["", "Mi TFG", "Groll 2015", "Groll 2019", "Ogundeji 2024"],
    ["Sistema Elo dinámico", "V", "R", "V", "R"],
    ["Ranking FIFA", "V", "V", "V", "V"],
    ["Cuotas como input", "R", "V", "V", "R"],
    ["Forma reciente", "V", "R", "R", "A"],
    ["H2H (enfrentamientos)", "V", "R", "R", "R"],
    ["Plantilla (jugadores)", "R", "V", "V", "R"],
    ["Factores económicos", "R", "V", "V", "R"],
    ["Rachas y descanso", "V", "R", "R", "R"],
  ];

  const colorMap = { V: "27AE60", A: "F39C12", R: "C0392B" };
  const colW = [2.6, 1.7, 1.7, 1.7, 1.7];
  const tblX = 1.7;
  const tblY = 2.1;

  // Header
  let curX = tblX;
  rows[0].forEach((cell, i) => {
    s.addShape("rect", {
      x: curX, y: tblY, w: colW[i], h: 0.4,
      fill: { color: COLORS.navy }, line: { color: COLORS.navy },
    });
    s.addText(cell, {
      x: curX, y: tblY, w: colW[i], h: 0.4,
      fontFace: FONTS.body, fontSize: 11, color: COLORS.white,
      bold: true, align: "center", valign: "middle",
    });
    curX += colW[i];
  });

  // Data rows
  rows.slice(1).forEach((row, rIdx) => {
    let x = tblX;
    const y = tblY + 0.4 + rIdx * 0.4;
    row.forEach((cell, cIdx) => {
      const isLabel = cIdx === 0;
      const fill = isLabel ? COLORS.cream : colorMap[cell];
      s.addShape("rect", {
        x, y, w: colW[cIdx], h: 0.4,
        fill: { color: fill }, line: { color: "E5E2DC", width: 0.5 },
      });
      s.addText(isLabel ? cell : "", {
        x, y, w: colW[cIdx], h: 0.4,
        fontFace: FONTS.body, fontSize: 11,
        color: isLabel ? COLORS.textDark : COLORS.white,
        bold: isLabel, align: "left", valign: "middle",
        margin: 0.1,
      });
      x += colW[cIdx];
    });
  });

  // Leyenda al lado de la tabla (a la derecha)
  // La tabla termina aprox en y = 2.1 + 0.4 + 8*0.4 = 5.7
  const legendY = 6.1;
  const legendItems = [
    { color: colorMap.V, text: "Coincide" },
    { color: colorMap.A, text: "Variante similar" },
    { color: colorMap.R, text: "No la usan" },
  ];
  legendItems.forEach((item, i) => {
    const x = 3.0 + i * 2.6;
    s.addShape("rect", { x, y: legendY, w: 0.4, h: 0.3, fill: { color: item.color }, line: { color: item.color } });
    s.addText(item.text, { x: x + 0.5, y: legendY, w: 2.0, h: 0.3, fontFace: FONTS.body, fontSize: 12, color: COLORS.textDark, valign: "middle" });
  });

  addFooter(s, 5, TOTAL);
}

// ============================================================
// SLIDE 6 — PIPELINE
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 3, "Metodología");
  slideTitle(s, "Pipeline del sistema");

  // 5 fases horizontales
  const phases = [
    { num: "01", name: "Datos\nhistóricos", detail: "49.215 partidos\n1872–2026" },
    { num: "02", name: "Ingeniería\nde variables", detail: "50 features\nELO, forma, H2H..." },
    { num: "03", name: "Modelo\nXGBoost", detail: "Optimizado\ncon Optuna" },
    { num: "04", name: "Simulación\nMonte Carlo", detail: "10.000 ediciones\ndel torneo" },
    { num: "05", name: "Aplicación\nweb", detail: "FastAPI\n+ Next.js" },
  ];

  phases.forEach((p, i) => {
    const x = 0.55 + i * 2.55;
    // Caja principal
    s.addShape("rect", {
      x, y: 2.5, w: 2.3, h: 3.5,
      fill: { color: COLORS.white }, line: { color: COLORS.divider, width: 1 },
    });
    // Banda superior
    s.addShape("rect", {
      x, y: 2.5, w: 2.3, h: 0.4,
      fill: { color: COLORS.navy }, line: { color: COLORS.navy },
    });
    s.addText(p.num, {
      x, y: 2.5, w: 2.3, h: 0.4,
      fontFace: FONTS.title, fontSize: 14, color: COLORS.gold,
      bold: true, align: "center", valign: "middle",
    });
    // Nombre
    s.addText(p.name, {
      x: x + 0.1, y: 3.3, w: 2.1, h: 1.0,
      fontFace: FONTS.title, fontSize: 18, color: COLORS.navy,
      bold: true, align: "center", lineSpacingMultiple: 1.1,
    });
    // Detalle
    s.addText(p.detail, {
      x: x + 0.1, y: 4.5, w: 2.1, h: 1.2,
      fontFace: FONTS.body, fontSize: 11, color: COLORS.textGray,
      align: "center", lineSpacingMultiple: 1.3,
    });
    // Flecha entre fases
    if (i < 4) {
      s.addShape("rightTriangle", {
        x: x + 2.36, y: 4.0, w: 0.13, h: 0.5,
        fill: { color: COLORS.red }, line: { color: COLORS.red },
        rotate: 90,
      });
    }
  });

  // Mensaje
  s.addText("Arquitectura modular: cada componente es independiente y reemplazable.", {
    x: 0.7, y: 6.3, w: 12.0, h: 0.4,
    fontFace: FONTS.title, fontSize: 14, color: COLORS.navy,
    italic: true, align: "center",
  });

  addFooter(s, 6, TOTAL);
}

// ============================================================
// SLIDE 7 — LAS 50 VARIABLES
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 3, "Metodología");
  slideTitle(s, "50 variables en 14 familias");

  // Stat callout grande a la izquierda
  s.addShape("rect", {
    x: 0.7, y: 2.0, w: 3.5, h: 4.5,
    fill: { color: COLORS.navy }, line: { color: COLORS.navy },
  });
  s.addText("50", {
    x: 0.7, y: 2.3, w: 3.5, h: 2.0,
    fontFace: FONTS.title, fontSize: 120, color: COLORS.red,
    bold: true, align: "center",
  });
  s.addText("VARIABLES\nPREDICTIVAS", {
    x: 0.7, y: 4.5, w: 3.5, h: 0.8,
    fontFace: FONTS.body, fontSize: 14, color: COLORS.gold,
    bold: true, align: "center", charSpacing: 3, lineSpacingMultiple: 1.2,
  });
  s.addText("organizadas en\n14 familias", {
    x: 0.7, y: 5.4, w: 3.5, h: 0.8,
    fontFace: FONTS.body, fontSize: 13, color: COLORS.white,
    italic: true, align: "center",
  });

  // Familias en columna derecha (grid 2x7)
  const families = [
    ["ELO", "4"], ["Forma reciente", "14"],
    ["H2H", "6"], ["Diferencias forma", "3"],
    ["Contextuales", "3"], ["Confederación", "3"],
    ["Rachas", "4"], ["Descanso", "3"],
    ["Clean sheets", "2"], ["Knockout", "1"],
    ["Experiencia", "2"], ["Local/visitante", "2"],
    ["Ranking FIFA", "3"], ["", ""],
  ];

  families.forEach((f, i) => {
    if (!f[0]) return;
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 4.6 + col * 4.1;
    const y = 2.0 + row * 0.63;
    s.addShape("rect", {
      x, y, w: 3.9, h: 0.55,
      fill: { color: COLORS.white }, line: { color: COLORS.divider, width: 0.5 },
    });
    // Banda izquierda roja
    s.addShape("rect", {
      x, y, w: 0.08, h: 0.55,
      fill: { color: COLORS.red }, line: { color: COLORS.red },
    });
    s.addText(f[0], {
      x: x + 0.2, y, w: 2.8, h: 0.55,
      fontFace: FONTS.body, fontSize: 12, color: COLORS.textDark,
      bold: true, valign: "middle",
    });
    s.addText(f[1], {
      x: x + 3.0, y, w: 0.8, h: 0.55,
      fontFace: FONTS.title, fontSize: 16, color: COLORS.red,
      bold: true, align: "right", valign: "middle",
    });
  });

  addFooter(s, 7, TOTAL);
}

// ============================================================
// SLIDE 8 — EDA Y ELO
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 4, "Desarrollo");
  slideTitle(s, "EDA: calibrar el ELO fue lo más complejo");

  // Imagen del top ELO a la izquierda
  s.addImage({
    path: path.join(OUT, "fig_eda_top_elo.png"),
    x: 0.6, y: 1.95, w: 6.5, h: 4.3,
  });

  // Bloque derecho: hallazgos clave
  s.addText("HALLAZGOS DEL EDA", {
    x: 7.4, y: 1.95, w: 5.4, h: 0.4,
    fontFace: FONTS.body, fontSize: 11, color: COLORS.red, bold: true, charSpacing: 2,
  });

  const findings = [
    { key: "K = 40", val: "anomalías: selecciones menores inflaban su ELO." },
    { key: "K = 32", val: "ratings más estables, sin inflación." },
    { key: "+ regresión media", val: "0,3% tras cada partido evita que se disparen." },
    { key: "+ peso torneo", val: "Mundial pesa 1,5; amistoso 0,6." },
    { key: "+ ventana 10", val: "óptimo entre estabilidad y sensibilidad." },
  ];
  findings.forEach((f, i) => {
    const y = 2.5 + i * 0.7;
    s.addShape("rect", {
      x: 7.4, y, w: 0.15, h: 0.5,
      fill: { color: COLORS.red }, line: { color: COLORS.red },
    });
    s.addText([
      { text: f.key + "  ", options: { bold: true, color: COLORS.navy } },
      { text: f.val, options: { color: COLORS.textDark } },
    ], { x: 7.7, y, w: 5.0, h: 0.5, fontFace: FONTS.body, fontSize: 11, valign: "middle", lineSpacingMultiple: 1.2 });
  });

  addFooter(s, 8, TOTAL);
}

// ============================================================
// SLIDE 9 — ANÁLISIS SHAP (LA ESTRELLA)
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 4, "Desarrollo");
  slideTitle(s, "Qué variables importan: análisis SHAP");

  // Imagen SHAP a la izquierda
  s.addImage({
    path: path.join(OUT, "fig_shap_beeswarm.png"),
    x: 0.5, y: 1.95, w: 7.5, h: 4.5,
  });

  // Insights a la derecha
  s.addShape("rect", {
    x: 8.3, y: 1.95, w: 4.5, h: 4.5,
    fill: { color: COLORS.navy }, line: { color: COLORS.navy },
  });
  s.addText("LO QUE REVELA SHAP", {
    x: 8.3, y: 2.1, w: 4.5, h: 0.4,
    fontFace: FONTS.body, fontSize: 12, color: COLORS.gold,
    bold: true, align: "center", charSpacing: 2,
  });

  const insights = [
    { icon: "1", label: "ELO domina con diferencia.", note: "Un solo rating sintetiza la historia del equipo." },
    { icon: "2", label: "Ranking FIFA aporta.", note: "Información complementaria al Elo." },
    { icon: "3", label: "Confederación importa.", note: "No es igual UEFA que OFC." },
    { icon: "4", label: "H2H aporta poco.", note: "Coincide con Groll [10]." },
  ];

  insights.forEach((it, i) => {
    const y = 2.65 + i * 0.85;
    s.addShape("ellipse", {
      x: 8.45, y, w: 0.4, h: 0.4,
      fill: { color: COLORS.red }, line: { color: COLORS.red },
    });
    s.addText(it.icon, {
      x: 8.45, y, w: 0.4, h: 0.4,
      fontFace: FONTS.title, fontSize: 14, color: COLORS.white,
      bold: true, align: "center", valign: "middle",
    });
    s.addText(it.label, {
      x: 8.95, y: y - 0.04, w: 3.7, h: 0.35,
      fontFace: FONTS.body, fontSize: 12, color: COLORS.white, bold: true,
    });
    s.addText(it.note, {
      x: 8.95, y: y + 0.32, w: 3.7, h: 0.45,
      fontFace: FONTS.body, fontSize: 10, color: COLORS.cream,
      italic: true, lineSpacingMultiple: 1.2,
    });
  });

  addFooter(s, 9, TOTAL);
}

// ============================================================
// SLIDE 10 — RESULTADOS DEL MODELO
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 4, "Desarrollo");
  slideTitle(s, "Resultados del modelo XGBoost");

  // 3 stat callouts arriba
  const stats = [
    { num: "60,7%", label: "Accuracy en test", sub: "2023 en adelante" },
    { num: "0,8645", label: "Log loss en test", sub: "métrica principal" },
    { num: "53,1%", label: "Accuracy WC 2022", sub: "evaluación independiente" },
  ];

  stats.forEach((stat, i) => {
    const x = 0.7 + i * 4.2;
    s.addShape("rect", { x, y: 2.0, w: 3.8, h: 1.7, fill: { color: COLORS.navy }, line: { color: COLORS.navy } });
    s.addText(stat.num, {
      x, y: 2.1, w: 3.8, h: 0.9,
      fontFace: FONTS.title, fontSize: 40, color: COLORS.red, bold: true, align: "center",
    });
    s.addText(stat.label, {
      x, y: 2.95, w: 3.8, h: 0.35,
      fontFace: FONTS.body, fontSize: 13, color: COLORS.white, bold: true, align: "center",
    });
    s.addText(stat.sub, {
      x, y: 3.3, w: 3.8, h: 0.3,
      fontFace: FONTS.body, fontSize: 10, color: COLORS.gold, italic: true, align: "center",
    });
  });

  // Tabla de modelos abajo
  s.addText("COMPARATIVA DE MODELOS (validación)", {
    x: 0.7, y: 4.0, w: 12.0, h: 0.4,
    fontFace: FONTS.body, fontSize: 12, color: COLORS.red, bold: true, charSpacing: 2,
  });

  const modelRows = [
    ["Modelo", "Accuracy", "Log Loss"],
    ["XGBoost (Optuna)", "60,0%", "0,9051"],
    ["Stacking Ensemble", "58,8%", "0,9060"],
    ["LightGBM (Optuna)", "53,8%", "0,9565"],
  ];

  const mColW = [5.0, 3.5, 3.5];
  const mTblX = 0.7;
  const mTblY = 4.45;
  modelRows.forEach((row, rIdx) => {
    let x = mTblX;
    const y = mTblY + rIdx * 0.45;
    const isHeader = rIdx === 0;
    const isBest = rIdx === 1;
    row.forEach((cell, cIdx) => {
      const fill = isHeader ? COLORS.navy : (isBest ? "FFF3CD" : COLORS.white);
      s.addShape("rect", {
        x, y, w: mColW[cIdx], h: 0.45,
        fill: { color: fill }, line: { color: COLORS.divider, width: 0.5 },
      });
      s.addText(cell, {
        x: x + 0.15, y, w: mColW[cIdx] - 0.3, h: 0.45,
        fontFace: FONTS.body, fontSize: 12,
        color: isHeader ? COLORS.white : (isBest ? COLORS.red : COLORS.textDark),
        bold: isHeader || isBest, valign: "middle",
        align: cIdx === 0 ? "left" : "center",
      });
      x += mColW[cIdx];
    });
  });

  addFooter(s, 10, TOTAL);
}

// ============================================================
// SLIDE 11 — PREDICCIÓN MUNDIAL 2026
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 4, "Desarrollo");
  slideTitle(s, "Predicciones del Mundial 2026");

  // Imagen lollipop
  s.addImage({
    path: path.join(OUT, "fig_lollipop_monte_carlo.png"),
    x: 0.4, y: 1.9, w: 6.5, h: 4.6,
  });

  // Comparativa con bookmakers
  s.addImage({
    path: path.join(OUT, "fig_modelo_vs_bookmakers.png"),
    x: 6.95, y: 1.9, w: 6.2, h: 3.5,
  });

  // Caja info clave
  s.addShape("rect", {
    x: 6.95, y: 5.5, w: 6.2, h: 1.2,
    fill: { color: COLORS.navy }, line: { color: COLORS.navy },
  });
  s.addText("VALIDACIÓN", {
    x: 7.15, y: 5.6, w: 5.8, h: 0.3,
    fontFace: FONTS.body, fontSize: 10, color: COLORS.gold, bold: true, charSpacing: 2,
  });
  s.addText("Comparamos con cuotas de Polymarket, DraftKings, FanDuel y bet365 como baseline externo (mismo criterio que Groll 2019 [10]).", {
    x: 7.15, y: 5.95, w: 5.8, h: 0.7,
    fontFace: FONTS.body, fontSize: 11, color: COLORS.white,
    italic: true, lineSpacingMultiple: 1.2,
  });

  addFooter(s, 11, TOTAL);
}

// ============================================================
// SLIDE 12 — APLICACIÓN WEB
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 5, "Aplicación web");
  slideTitle(s, "Visualización interactiva");

  // Captura 1
  s.addImage({
    path: path.join(OUT, "Captura de pantalla 2026-04-07 164520.png"),
    x: 0.5, y: 1.95, w: 6.3, h: 3.5,
  });
  s.addText("Página principal: simulación o estadísticas", {
    x: 0.5, y: 5.5, w: 6.3, h: 0.3,
    fontFace: FONTS.body, fontSize: 10, color: COLORS.textGray, italic: true, align: "center",
  });

  // Captura 2
  s.addImage({
    path: path.join(OUT, "Captura de pantalla 2026-04-07 164503.png"),
    x: 7.0, y: 1.95, w: 6.1, h: 3.5,
  });
  s.addText("Vista de estadísticas: favoritos, probabilidades, baseline bookmakers", {
    x: 7.0, y: 5.5, w: 6.1, h: 0.3,
    fontFace: FONTS.body, fontSize: 10, color: COLORS.textGray, italic: true, align: "center",
  });

  addFooter(s, 12, TOTAL);
}

// ============================================================
// SLIDE 13 — CONCLUSIONES: APORTACIONES
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 6, "Conclusiones");
  slideTitle(s, "Aportaciones respecto al estado del arte");

  // 3 columnas con las aportaciones clave
  const aports = [
    {
      title: "Sistema ELO propio",
      desc: "Calibrado con K=32, pesos por torneo y regresión a la media.",
      vs: "Ningún paper revisado construye un ELO así.",
    },
    {
      title: "Reproducibilidad",
      desc: "100% datos públicos, código abierto, sin variables manuales de plantilla.",
      vs: "Groll requiere recopilación manual de plantillas.",
    },
    {
      title: "Análisis SHAP",
      desc: "Importancia de variables documentada de forma transparente.",
      vs: "Groll usa LASSO; Ogundeji no analiza importancia.",
    },
  ];

  aports.forEach((a, i) => {
    const x = 0.7 + i * 4.15;
    // Caja
    s.addShape("rect", {
      x, y: 2.0, w: 3.85, h: 4.6,
      fill: { color: COLORS.white }, line: { color: COLORS.divider, width: 1 },
    });
    // Banda superior
    s.addShape("rect", {
      x, y: 2.0, w: 3.85, h: 0.8,
      fill: { color: COLORS.navy }, line: { color: COLORS.navy },
    });
    // Número grande
    s.addText(`0${i+1}`, {
      x, y: 2.05, w: 3.85, h: 0.7,
      fontFace: FONTS.title, fontSize: 26, color: COLORS.gold,
      bold: true, align: "center", valign: "middle",
    });
    // Título
    s.addText(a.title, {
      x: x + 0.2, y: 3.0, w: 3.5, h: 0.7,
      fontFace: FONTS.title, fontSize: 18, color: COLORS.navy,
      bold: true, align: "center",
    });
    // Línea
    s.addShape("rect", {
      x: x + 1.3, y: 3.85, w: 1.25, h: 0.03,
      fill: { color: COLORS.red }, line: { color: COLORS.red },
    });
    // Desc
    s.addText(a.desc, {
      x: x + 0.25, y: 4.0, w: 3.4, h: 1.4,
      fontFace: FONTS.body, fontSize: 12, color: COLORS.textDark,
      align: "center", lineSpacingMultiple: 1.3,
    });
    // VS
    s.addShape("rect", { x: x + 0.25, y: 5.5, w: 3.4, h: 1.0, fill: { color: COLORS.cream }, line: { color: COLORS.divider, width: 0.5 } });
    s.addText([
      { text: "vs. literatura: ", options: { color: COLORS.red, bold: true } },
      { text: a.vs, options: { color: COLORS.textGray, italic: true } },
    ], { x: x + 0.35, y: 5.55, w: 3.2, h: 0.9, fontFace: FONTS.body, fontSize: 10, align: "left", valign: "middle", lineSpacingMultiple: 1.3 });
  });

  addFooter(s, 13, TOTAL);
}

// ============================================================
// SLIDE 14 — LÍNEAS FUTURAS
// ============================================================
{
  const s = pptx.addSlide();
  lightSlide(s);
  sectionHeader(s, 6, "Conclusiones");
  slideTitle(s, "Líneas futuras de investigación");

  const futures = [
    {
      label: "DATOS DE JUGADOR",
      desc: "Incorporar valor de mercado, estadísticas individuales y datos físicos desde Transfermarkt y FBref para enriquecer el modelo con información que actualmente solo manejan las casas de apuestas.",
    },
    {
      label: "OTRAS COMPETICIONES",
      desc: "Aplicar el pipeline a Champions League, ligas nacionales o competiciones continentales, donde la disponibilidad de datos es mayor y las muestras de evaluación más amplias.",
    },
    {
      label: "PREDICCIÓN DE MARCADOR",
      desc: "Modelo Poisson bivariante para predecir el número exacto de goles de cada equipo en lugar de solo la clase de resultado, permitiendo simulaciones con distribuciones de goles más realistas.",
    },
  ];

  futures.forEach((f, i) => {
    const y = 2.3 + i * 1.45;
    // Número
    s.addShape("ellipse", {
      x: 0.7, y, w: 0.9, h: 0.9,
      fill: { color: COLORS.red }, line: { color: COLORS.red },
    });
    s.addText(`${i+1}`, {
      x: 0.7, y, w: 0.9, h: 0.9,
      fontFace: FONTS.title, fontSize: 30, color: COLORS.white,
      bold: true, align: "center", valign: "middle",
    });
    // Label
    s.addText(f.label, {
      x: 1.85, y: y, w: 11.0, h: 0.35,
      fontFace: FONTS.body, fontSize: 13, color: COLORS.red,
      bold: true, charSpacing: 2,
    });
    // Desc
    s.addText(f.desc, {
      x: 1.85, y: y + 0.4, w: 10.8, h: 0.95,
      fontFace: FONTS.body, fontSize: 14, color: COLORS.textDark,
      lineSpacingMultiple: 1.3,
    });
  });

  addFooter(s, 14, TOTAL);
}

// ============================================================
// SLIDE 15 — CIERRE
// ============================================================
{
  const s = pptx.addSlide();
  darkSlide(s);

  // Detalle estilo "marca"
  s.addText("FIFA 2026", {
    x: 0.7, y: 1.0, w: 6, h: 0.6,
    fontFace: FONTS.title, fontSize: 24, color: COLORS.gold,
    italic: true, bold: true,
  });

  // Frase central
  s.addText("Gracias por su\natención.", {
    x: 0.7, y: 2.3, w: 12, h: 2.0,
    fontFace: FONTS.title, fontSize: 64, color: COLORS.white,
    bold: true, lineSpacingMultiple: 1.05,
  });

  // Línea
  s.addShape("rect", { x: 0.7, y: 4.6, w: 2.5, h: 0.06, fill: { color: COLORS.red }, line: { color: COLORS.red } });

  // Subtítulo
  s.addText("Quedo a su disposición para preguntas y comentarios.", {
    x: 0.7, y: 4.85, w: 12, h: 0.6,
    fontFace: FONTS.title, fontSize: 18, color: COLORS.cream, italic: true,
  });

  // Datos
  s.addText("Raúl Ramírez Adarve", {
    x: 0.7, y: 6.2, w: 12, h: 0.4,
    fontFace: FONTS.body, fontSize: 14, color: COLORS.gold, bold: true,
  });
  s.addText("Grado en Ingeniería del Software · Mención en Ingeniería de Datos", {
    x: 0.7, y: 6.55, w: 12, h: 0.4,
    fontFace: FONTS.body, fontSize: 11, color: COLORS.textMuted, italic: true,
  });
}

// Guardar
const outPath = path.resolve(OUT, "TFG-Defensa-Raul-Ramirez.pptx");
pptx.writeFile({ fileName: outPath }).then(() => {
  console.log("OK -> " + outPath);
});
