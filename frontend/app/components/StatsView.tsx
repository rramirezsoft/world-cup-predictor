"use client";

import { motion } from "framer-motion";
import { MonteCarloTeam } from "../types";
import Flag from "./Flag";

interface StatsViewProps {
  data: MonteCarloTeam[];
  nSimulations: number;
}

// Odds reales de casas de apuestas (marzo 2026, fuentes: bet365, Betfair, William Hill)
// Convertidas de cuotas decimales a probabilidad implícita
const BOOKMAKER_ODDS: Record<string, number> = {
  Argentina: 14.0,
  Spain: 12.0,
  France: 11.0,
  England: 10.0,
  Brazil: 8.0,
  Germany: 6.5,
  Portugal: 5.5,
  Netherlands: 4.0,
  Colombia: 2.5,
  Belgium: 2.0,
  Italy: 2.0,
  Uruguay: 1.8,
  USA: 1.5,
  Denmark: 1.2,
  Croatia: 1.0,
  Mexico: 0.8,
  Japan: 0.8,
  "Korea Republic": 0.5,
  Switzerland: 0.5,
  Ecuador: 0.4,
};

const CONF_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  UEFA: { bg: "bg-blue-500/20", text: "text-blue-400", label: "Europa" },
  CONMEBOL: { bg: "bg-emerald-500/20", text: "text-emerald-400", label: "Sudamerica" },
  CONCACAF: { bg: "bg-red-500/20", text: "text-red-400", label: "Norteamerica" },
  CAF: { bg: "bg-yellow-500/20", text: "text-yellow-400", label: "Africa" },
  AFC: { bg: "bg-purple-500/20", text: "text-purple-400", label: "Asia" },
  OFC: { bg: "bg-teal-500/20", text: "text-teal-400", label: "Oceania" },
};

function MedalBadge({ rank }: { rank: number }) {
  const styles: Record<number, string> = {
    1: "bg-gradient-to-br from-yellow-400 to-yellow-600 text-yellow-900 shadow-yellow-500/20",
    2: "bg-gradient-to-br from-gray-300 to-gray-400 text-gray-700 shadow-gray-400/20",
    3: "bg-gradient-to-br from-amber-600 to-amber-700 text-amber-100 shadow-amber-600/20",
  };
  if (rank <= 3) {
    return <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-[10px] font-black shadow-md ${styles[rank]}`}>{rank}</span>;
  }
  return <span className="inline-flex items-center justify-center w-6 h-6 text-[11px] font-medium text-gray-600">{rank}</span>;
}

function PctBar({ pct, maxPct, color, delay }: { pct: number; maxPct: number; color: string; delay: number }) {
  const width = maxPct > 0 ? (pct / maxPct) * 100 : 0;
  return (
    <div className="w-full h-5 bg-white/[0.03] rounded overflow-hidden relative">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${Math.max(width, 0.5)}%` }}
        transition={{ duration: 0.8, delay, ease: "easeOut" }}
        className="h-full rounded"
        style={{ backgroundColor: color }}
      />
      <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white/80">
        {pct > 0 ? `${pct.toFixed(1)}%` : "-"}
      </span>
    </div>
  );
}

function DualBar({ ours, theirs, maxVal, delay }: { ours: number; theirs: number; maxVal: number; delay: number }) {
  const oursW = maxVal > 0 ? (ours / maxVal) * 100 : 0;
  const theirsW = maxVal > 0 ? (theirs / maxVal) * 100 : 0;
  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <span className="text-[9px] text-[#e94560] w-14 text-right font-semibold">{ours.toFixed(1)}%</span>
        <div className="flex-1 h-3.5 bg-white/[0.03] rounded overflow-hidden">
          <motion.div initial={{ width: 0 }} animate={{ width: `${oursW}%` }} transition={{ duration: 0.8, delay, ease: "easeOut" }} className="h-full rounded bg-[#e94560]/70" />
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-[9px] text-blue-400 w-14 text-right font-semibold">{theirs.toFixed(1)}%</span>
        <div className="flex-1 h-3.5 bg-white/[0.03] rounded overflow-hidden">
          <motion.div initial={{ width: 0 }} animate={{ width: `${theirsW}%` }} transition={{ duration: 0.8, delay: delay + 0.1, ease: "easeOut" }} className="h-full rounded bg-blue-500/50" />
        </div>
      </div>
    </div>
  );
}

export default function StatsView({ data, nSimulations }: StatsViewProps) {
  const maxChampion = Math.max(...data.map((t) => t.champion_pct), 1);
  const maxFinal = Math.max(...data.map((t) => t.final_pct), 1);
  const maxSf = Math.max(...data.map((t) => t.sf_pct), 1);
  const top3 = data.slice(0, 3);

  // Comparison data
  const comparisonTeams = data.filter((t) => BOOKMAKER_ODDS[t.team]).slice(0, 15);
  const maxComparison = Math.max(
    ...comparisonTeams.map((t) => Math.max(t.champion_pct, BOOKMAKER_ODDS[t.team] || 0)),
    1
  );

  // Confederation stats
  const confStats: Record<string, { total: number; champPct: number; teams: string[] }> = {};
  for (const team of data) {
    const conf = team.team === "USA" || team.team === "United States" ? "CONCACAF" :
      team.team === "Australia" ? "AFC" :
      team.team === "New Zealand" ? "OFC" :
      ["Argentina", "Brazil", "Uruguay", "Colombia", "Ecuador", "Paraguay", "Chile", "Peru", "Venezuela", "Bolivia"].includes(team.team) ? "CONMEBOL" :
      ["Mexico", "Canada", "Jamaica", "Honduras", "Costa Rica", "Panama", "Trinidad and Tobago", "El Salvador"].includes(team.team) ? "CONCACAF" :
      ["Japan", "South Korea", "Korea Republic", "Iran", "Saudi Arabia", "Qatar", "Iraq", "Uzbekistan", "China PR", "Indonesia", "Bahrain", "Jordan", "Palestine", "United Arab Emirates", "Oman"].includes(team.team) ? "AFC" :
      ["Morocco", "Senegal", "Nigeria", "Cameroon", "Egypt", "Ghana", "Tunisia", "Ivory Coast", "Cote d'Ivoire", "Algeria", "Mali", "DR Congo", "South Africa", "Burkina Faso", "Tanzania", "Mozambique", "Benin", "Uganda", "Congo", "Equatorial Guinea", "Cape Verde"].includes(team.team) ? "CAF" :
      "UEFA";
    if (!confStats[conf]) confStats[conf] = { total: 0, champPct: 0, teams: [] };
    confStats[conf].total++;
    confStats[conf].champPct += team.champion_pct;
    confStats[conf].teams.push(team.team);
  }

  return (
    <div className="space-y-10">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-[#e94560]" />
          Estadisticas del Modelo
        </h2>
        <p className="text-gray-600 text-sm mt-1.5 max-w-3xl leading-relaxed">
          Probabilidades calculadas a partir de {nSimulations.toLocaleString()} simulaciones
          completas del Mundial 2026. Modelo XGBoost con 47 features, entrenado sobre
          49,000+ partidos historicos.
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "Simulaciones", value: nSimulations.toLocaleString(), sub: "Monte Carlo" },
          { label: "Partidos/sim", value: "104", sub: "72 grupos + 32 elim." },
          { label: "Selecciones", value: "48", sub: "12 grupos de 4" },
          { label: "Features", value: "47", sub: "ELO, forma, H2H..." },
        ].map((card) => (
          <div key={card.label} className="bg-[#141b2d] rounded-xl border border-white/[0.06] p-4">
            <p className="text-[10px] text-gray-600 uppercase tracking-wider">{card.label}</p>
            <p className="text-2xl font-black text-white mt-1">{card.value}</p>
            <p className="text-[10px] text-gray-500 mt-0.5">{card.sub}</p>
          </div>
        ))}
      </div>

      {/* Top 3 podium */}
      <div className="grid grid-cols-3 gap-4 max-w-3xl mx-auto">
        {top3.map((team, idx) => {
          const borders = ["border-yellow-500/40 shadow-yellow-500/10", "border-gray-400/30 shadow-gray-400/10", "border-amber-600/30 shadow-amber-600/10"];
          const gradients = ["from-yellow-500/10 to-yellow-600/5", "from-gray-400/10 to-gray-500/5", "from-amber-600/10 to-amber-700/5"];
          const labels = ["Favorito", "2do Favorito", "3er Favorito"];
          return (
            <motion.div
              key={team.team}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.15, duration: 0.5 }}
              className={`bg-gradient-to-b ${gradients[idx]} border ${borders[idx]} rounded-xl p-5 text-center shadow-lg`}
              style={{ order: idx === 0 ? 1 : idx === 1 ? 0 : 2 }}
            >
              <p className="text-[10px] uppercase tracking-widest text-gray-500 mb-3">{labels[idx]}</p>
              <div className="flex justify-center mb-3"><Flag team={team.team} size={48} /></div>
              <p className="font-bold text-base text-white">{team.team}</p>
              <p className="text-[#e94560] font-black text-3xl mt-1">{team.champion_pct.toFixed(1)}%</p>
              <div className="mt-3 space-y-1 text-[10px] text-gray-500">
                <p>Final: <span className="text-gray-300 font-medium">{team.final_pct.toFixed(1)}%</span></p>
                <p>Semifinal: <span className="text-gray-300 font-medium">{team.sf_pct.toFixed(1)}%</span></p>
                <p>ELO: <span className="text-gray-300 font-medium">{team.elo.toFixed(0)}</span></p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* ===== COMPARISON WITH BOOKMAKERS ===== */}
      <div className="bg-[#141b2d] rounded-xl border border-white/[0.06] overflow-hidden">
        <div className="bg-[#0f1629] border-b border-white/[0.06] px-5 py-4">
          <h3 className="font-bold text-sm text-white">Nuestro Modelo vs. Casas de Apuestas</h3>
          <p className="text-[10px] text-gray-500 mt-1">
            Comparacion de probabilidades de campeon — Fuentes: bet365, Betfair, William Hill (marzo 2026)
          </p>
          <div className="flex gap-4 mt-2">
            <span className="flex items-center gap-1.5 text-[10px]">
              <span className="w-3 h-2 rounded-sm bg-[#e94560]/70" />
              <span className="text-gray-400">Nuestro modelo</span>
            </span>
            <span className="flex items-center gap-1.5 text-[10px]">
              <span className="w-3 h-2 rounded-sm bg-blue-500/50" />
              <span className="text-gray-400">Casas de apuestas</span>
            </span>
          </div>
        </div>
        <div className="p-4 space-y-3">
          {comparisonTeams.map((team, idx) => (
            <motion.div
              key={team.team}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.03, duration: 0.3 }}
              className="flex items-center gap-3"
            >
              <div className="flex items-center gap-2 w-36 shrink-0">
                <Flag team={team.team} size={20} />
                <span className="text-xs font-medium text-gray-300 truncate">{team.team}</span>
              </div>
              <div className="flex-1">
                <DualBar
                  ours={team.champion_pct}
                  theirs={BOOKMAKER_ODDS[team.team] || 0}
                  maxVal={maxComparison}
                  delay={idx * 0.03}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* ===== CONFEDERATION BREAKDOWN ===== */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
        {Object.entries(confStats)
          .sort(([, a], [, b]) => b.champPct - a.champPct)
          .map(([conf, stats]) => {
            const colors = CONF_COLORS[conf] || { bg: "bg-gray-500/20", text: "text-gray-400", label: conf };
            return (
              <motion.div
                key={conf}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`${colors.bg} rounded-xl border border-white/[0.04] p-4`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-xs font-bold ${colors.text}`}>{colors.label}</span>
                  <span className="text-[10px] text-gray-500">{stats.total} equipos</span>
                </div>
                <p className="text-xl font-black text-white">{stats.champPct.toFixed(1)}%</p>
                <p className="text-[10px] text-gray-500 mt-0.5">prob. acumulada de campeon</p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {stats.teams.slice(0, 5).map((t) => (
                    <Flag key={t} team={t} size={16} />
                  ))}
                  {stats.teams.length > 5 && (
                    <span className="text-[9px] text-gray-600 self-center ml-1">+{stats.teams.length - 5}</span>
                  )}
                </div>
              </motion.div>
            );
          })}
      </div>

      {/* ===== FULL TABLE ===== */}
      <div>
        <h3 className="text-base font-bold mb-3 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-[#e94560]" />
          Ranking Completo — 48 Selecciones
        </h3>
        <div className="bg-[#141b2d] rounded-xl border border-white/[0.06] overflow-hidden">
          <div className="bg-[#0f1629] border-b border-white/[0.06]">
            <div className="grid grid-cols-[3rem_1fr_7rem_7rem_7rem_5rem] gap-2 px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-500">
              <div className="text-center">#</div>
              <div>Seleccion</div>
              <div className="text-center">Campeon</div>
              <div className="text-center">Final</div>
              <div className="text-center">Semifinal</div>
              <div className="text-center">ELO</div>
            </div>
          </div>
          <div>
            {data.map((team, idx) => (
              <motion.div
                key={team.team}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.015, duration: 0.3 }}
                className={`grid grid-cols-[3rem_1fr_7rem_7rem_7rem_5rem] gap-2 px-4 py-2 items-center border-b border-white/[0.02] table-row-hover ${idx < 3 ? "bg-white/[0.02]" : ""}`}
              >
                <div className="flex justify-center"><MedalBadge rank={idx + 1} /></div>
                <div className="flex items-center gap-2.5">
                  <Flag team={team.team} size={24} />
                  <span className={`text-sm truncate ${idx < 3 ? "font-bold text-white" : idx < 8 ? "font-medium text-gray-200" : "text-gray-400"}`}>
                    {team.team}
                  </span>
                </div>
                <div>
                  <PctBar pct={team.champion_pct} maxPct={maxChampion} color={idx < 3 ? "rgba(233,69,96,0.7)" : idx < 8 ? "rgba(233,69,96,0.45)" : "rgba(233,69,96,0.2)"} delay={idx * 0.015} />
                </div>
                <div>
                  <PctBar pct={team.final_pct} maxPct={maxFinal} color={idx < 3 ? "rgba(59,130,246,0.6)" : "rgba(59,130,246,0.25)"} delay={idx * 0.015 + 0.1} />
                </div>
                <div>
                  <PctBar pct={team.sf_pct} maxPct={maxSf} color={idx < 3 ? "rgba(34,197,94,0.5)" : "rgba(34,197,94,0.2)"} delay={idx * 0.015 + 0.2} />
                </div>
                <div className="text-center text-xs font-mono text-gray-500">{team.elo.toFixed(0)}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-6 justify-center text-[10px] text-gray-600">
        <span className="flex items-center gap-1.5"><span className="w-3 h-2 rounded-sm bg-[#e94560]/60" /> % Campeon</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-2 rounded-sm bg-blue-500/50" /> % Finalista</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-2 rounded-sm bg-emerald-500/40" /> % Semifinalista</span>
      </div>
    </div>
  );
}
