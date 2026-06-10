"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import GroupTable from "./components/GroupTable";
import KnockoutBracket from "./components/KnockoutBracket";
import StatsView from "./components/StatsView";
import Confetti from "./components/Confetti";
import Flag from "./components/Flag";
import { SimulationResult, MonteCarloTeam } from "./types";

const API_BASE = "/api";

type Tab = "simulation" | "stats";
type Phase = "idle" | "loading" | "groups" | "r32" | "r16" | "qf" | "sf" | "final" | "champion" | "stats-loading" | "stats";

const KNOCKOUT_PHASES: Phase[] = ["r32", "r16", "qf", "sf", "final"];
const SIMULATION_PHASES: Phase[] = ["groups", ...KNOCKOUT_PHASES];

const PHASE_LABELS: Record<string, string> = {
  groups: "Fase de Grupos",
  r32: "Ronda de 32",
  r16: "Octavos de Final",
  qf: "Cuartos de Final",
  sf: "Semifinales",
  final: "La Gran Final",
};

export default function Home() {
  const [tab, setTab] = useState<Tab>("simulation");
  const [phase, setPhase] = useState<Phase>("idle");
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [statsData, setStatsData] = useState<{ teams: MonteCarloTeam[]; nSims: number } | null>(null);
  const [visibleGroups, setVisibleGroups] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);

  // Progressive group reveal
  useEffect(() => {
    if (phase !== "groups" || !simulation) return;
    const totalGroups = Object.keys(simulation.groups).length;
    if (visibleGroups < totalGroups) {
      const timer = setTimeout(() => setVisibleGroups((v) => v + 1), 250);
      return () => clearTimeout(timer);
    }
    const timer = setTimeout(() => setPhase("r32"), 1200);
    return () => clearTimeout(timer);
  }, [phase, visibleGroups, simulation]);

  // Knockout auto-progression
  useEffect(() => {
    if (!simulation) return;
    const next: Record<string, Phase> = { r32: "r16", r16: "qf", qf: "sf", sf: "final", final: "champion" };
    const nextPhase = next[phase];
    if (!nextPhase) return;
    const delay = phase === "r32" ? 2500 : phase === "final" ? 2500 : 2000;
    const timer = setTimeout(() => {
      setPhase(nextPhase);
      if (nextPhase === "champion") {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 5000);
      }
    }, delay);
    return () => clearTimeout(timer);
  }, [phase, simulation]);

  const runSimulation = async () => {
    setTab("simulation");
    setPhase("loading");
    setError(null);
    setVisibleGroups(0);
    setShowConfetti(false);
    try {
      const seed = Math.floor(Math.random() * 100000);
      const res = await fetch(`${API_BASE}/simulation?seed=${seed}`);
      if (!res.ok) throw new Error(`Error ${res.status}`);
      setSimulation(await res.json());
      setPhase("groups");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error desconocido");
      setPhase("idle");
    }
  };

  const loadStats = async () => {
    setTab("stats");
    if (statsData) {
      setPhase("stats");
      return;
    }
    setPhase("stats-loading");
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/monte-carlo`);
      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = await res.json();
      setStatsData({ teams: data.teams, nSims: data.n_simulations });
      setPhase("stats");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error desconocido");
      setPhase(simulation ? "champion" : "idle");
    }
  };

  const skipToEnd = () => {
    if (!simulation) return;
    setPhase("champion");
    setVisibleGroups(Object.keys(simulation.groups).length);
    setShowConfetti(true);
    setTimeout(() => setShowConfetti(false), 5000);
  };

  const isSimulating = SIMULATION_PHASES.includes(phase);
  const groupEntries = simulation
    ? Object.entries(simulation.groups).sort(([a], [b]) => a.localeCompare(b))
    : [];

  return (
    <main className="min-h-screen relative z-10">
      {showConfetti && <Confetti />}

      {/* Header */}
      <header className="border-b border-white/[0.06] bg-[#0a0e1a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#e94560] to-[#c73e54] flex items-center justify-center text-lg font-black text-white shadow-lg shadow-[#e94560]/20">
              WC
            </div>
            <div>
              <h1 className="text-sm sm:text-lg font-black tracking-tight">
                <span className="hidden sm:inline">World Cup 2026 </span>
                <span className="sm:hidden">WC 2026 </span>
                <span className="text-[#e94560]">Predictor</span>
              </h1>
              <p className="text-[9px] text-gray-600 uppercase tracking-[0.2em] hidden sm:block">
                USA &middot; Mexico &middot; Canada 2026
              </p>
            </div>
          </div>

          <div className="flex gap-1.5 sm:gap-2 items-center flex-wrap justify-end">
            {isSimulating && (
              <button onClick={skipToEnd} className="text-[10px] sm:text-[11px] text-gray-500 hover:text-white px-2 sm:px-3 py-1.5 rounded-lg border border-white/[0.06] hover:border-white/[0.12] transition-all">
                Saltar
              </button>
            )}
            <button
              onClick={runSimulation}
              disabled={phase === "loading"}
              className="bg-[#e94560] hover:bg-[#d13a54] disabled:opacity-50 text-white px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg font-semibold text-[11px] sm:text-xs transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-[#e94560]/15"
            >
              {phase === "loading" ? (
                <span className="flex items-center gap-2">
                  <span className="inline-block w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span className="hidden sm:inline">Simulando...</span>
                  <span className="sm:hidden">...</span>
                </span>
              ) : <><span className="hidden sm:inline">Simular Mundial</span><span className="sm:hidden">Simular</span></>}
            </button>
            <button
              onClick={loadStats}
              disabled={phase === "stats-loading"}
              className="bg-white/[0.04] hover:bg-white/[0.08] disabled:opacity-50 text-white px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg font-semibold text-[11px] sm:text-xs border border-white/[0.06] hover:border-white/[0.12] transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              {phase === "stats-loading" ? (
                <span className="flex items-center gap-2">
                  <span className="inline-block w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span className="hidden sm:inline">Cargando...</span>
                  <span className="sm:hidden">...</span>
                </span>
              ) : <><span className="hidden sm:inline">Estadisticas</span><span className="sm:hidden">Stats</span></>}
            </button>
          </div>
        </div>

        {/* Tab bar */}
        {(simulation || statsData) && phase !== "idle" && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 flex gap-1 pb-2">
            <button
              onClick={() => { setTab("simulation"); if (phase === "stats") setPhase(simulation ? "champion" : "idle"); }}
              className={`text-xs px-4 py-1.5 rounded-md transition-all ${tab === "simulation" ? "bg-white/[0.08] text-white font-semibold" : "text-gray-500 hover:text-gray-300"}`}
            >
              Simulacion
            </button>
            <button
              onClick={loadStats}
              className={`text-xs px-4 py-1.5 rounded-md transition-all ${tab === "stats" ? "bg-white/[0.08] text-white font-semibold" : "text-gray-500 hover:text-gray-300"}`}
            >
              Estadisticas
            </button>
          </div>
        )}
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="bg-red-500/[0.08] border border-red-500/20 rounded-xl px-5 py-4 mb-6"
            >
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-red-500/15 flex items-center justify-center text-red-400 shrink-0 mt-0.5">!</div>
                <div>
                  <p className="text-sm text-red-300 font-medium">{error}</p>
                  <p className="text-xs mt-1 text-red-400/60">
                    Asegurate de que el backend esta corriendo en el puerto 8001
                  </p>
                </div>
                <button onClick={() => setError(null)} className="text-red-400/50 hover:text-red-300 ml-auto text-lg">&times;</button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ===== IDLE ===== */}
        {phase === "idle" && !simulation && !statsData && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6 }} className="text-center py-10 sm:py-16">
            <motion.div animate={{ y: [0, -8, 0] }} transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }} className="mb-8">
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-gradient-to-br from-[#e94560]/20 to-[#e94560]/5 border border-[#e94560]/10">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="w-12 h-12 text-[#e94560]" strokeWidth={1.5}>
                  <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" />
                  <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" />
                  <path d="M4 22h16" />
                  <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
                  <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
                  <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
                </svg>
              </div>
            </motion.div>

            <h2 className="text-3xl sm:text-5xl font-black mb-4 tracking-tight">
              FIFA World Cup <span className="text-[#e94560]">2026</span>
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto mb-3 text-base sm:text-lg leading-relaxed px-2">
              Descubre quien tiene mas probabilidades de ganar el proximo Mundial
              y simula el torneo completo.
            </p>
            <p className="text-gray-600 max-w-xl mx-auto mb-8 sm:mb-10 text-sm leading-relaxed px-2">
              48 selecciones. 12 grupos. 104 partidos. El primer Mundial
              con este formato — y nosotros lo predecimos.
            </p>

            <div className="flex gap-4 justify-center flex-wrap">
              <button onClick={runSimulation} className="bg-gradient-to-r from-[#e94560] to-[#c73e54] hover:from-[#d13a54] hover:to-[#b03548] text-white px-8 sm:px-10 py-3 sm:py-4 rounded-xl font-bold text-sm sm:text-base transition-all hover:scale-[1.03] active:scale-[0.98] shadow-xl shadow-[#e94560]/20">
                Simular el Mundial
              </button>
              <button onClick={loadStats} className="bg-white/[0.04] hover:bg-white/[0.08] text-white px-8 sm:px-10 py-3 sm:py-4 rounded-xl font-bold text-sm sm:text-base border border-white/[0.08] hover:border-white/[0.15] transition-all hover:scale-[1.03] active:scale-[0.98]">
                Estadisticas
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mt-10 sm:mt-16 max-w-3xl mx-auto px-2 sm:px-0">
              {[
                { title: "48 Selecciones", desc: "Todas las clasificadas para USA, Mexico y Canada 2026" },
                { title: "12 Grupos", desc: "Fase de grupos completa con los 104 partidos del torneo" },
                { title: "10,000 Escenarios", desc: "Probabilidades basadas en miles de simulaciones del torneo" },
              ].map((f) => (
                <div key={f.title} className="bg-white/[0.02] rounded-xl p-5 border border-white/[0.04] hover:border-white/[0.08] transition-colors">
                  <h3 className="font-bold text-sm text-white">{f.title}</h3>
                  <p className="text-xs text-gray-600 mt-1.5 leading-relaxed">{f.desc}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ===== LOADING ===== */}
        {(phase === "loading" || phase === "stats-loading") && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-24">
            <div className="relative inline-block">
              <div className="h-16 w-16 rounded-full border-[3px] border-white/[0.06] border-t-[#e94560] animate-spin" />
            </div>
            <p className="mt-8 text-gray-300 text-lg font-medium">
              {phase === "loading" ? "Simulando el Mundial 2026..." : "Cargando estadisticas..."}
            </p>
          </motion.div>
        )}

        {/* ===== SIMULATION ===== */}
        {tab === "simulation" && simulation && (isSimulating || phase === "champion") && (
          <>
            {isSimulating && (
              <motion.div key={phase} initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
                <div className="inline-flex items-center gap-2 bg-[#e94560]/[0.08] border border-[#e94560]/15 rounded-full px-6 py-2">
                  <span className="w-2 h-2 rounded-full bg-[#e94560] animate-pulse" />
                  <span className="text-[#e94560] font-bold text-sm">{PHASE_LABELS[phase] || phase}</span>
                </div>
                <div className="flex gap-1 sm:gap-1.5 justify-center mt-4">
                  {SIMULATION_PHASES.map((p) => (
                    <div key={p} className={`h-1 rounded-full transition-all duration-500 ${
                      SIMULATION_PHASES.indexOf(phase) >= SIMULATION_PHASES.indexOf(p) ? "bg-[#e94560] w-6 sm:w-10" : "bg-white/[0.06] w-5 sm:w-8"
                    }`} />
                  ))}
                </div>
              </motion.div>
            )}

            {/* Groups */}
            {(phase === "groups" || phase === "champion") && (
              <section className="mb-8">
                {phase === "champion" && (
                  <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#e94560]" />
                    Fase de Grupos
                    <span className="text-xs font-normal text-gray-600 ml-2">12 grupos &middot; 48 selecciones</span>
                  </h2>
                )}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {groupEntries.map(([name, data], idx) => (
                    <AnimatePresence key={name}>
                      {(phase === "champion" || idx < visibleGroups) && (
                        <motion.div initial={{ opacity: 0, scale: 0.95, y: 10 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ duration: 0.35 }}>
                          <GroupTable groupName={name} data={data} />
                        </motion.div>
                      )}
                    </AnimatePresence>
                  ))}
                </div>
              </section>
            )}

            {/* Knockout progressive */}
            {isSimulating && phase !== "groups" && (
              <section className="mt-8">
                <KnockoutBracket knockout={simulation.knockout} champion={simulation.champion} currentPhase={phase} />
              </section>
            )}

            {/* Champion */}
            {phase === "champion" && (
              <section className="mt-10">
                <motion.div initial={{ opacity: 0, scale: 0.85 }} animate={{ opacity: 1, scale: 1 }} transition={{ type: "spring", bounce: 0.35, duration: 0.8 }} className="text-center mb-10">
                  <div className="inline-block bg-gradient-to-b from-yellow-500/20 via-yellow-600/10 to-transparent border border-yellow-500/20 rounded-2xl px-6 sm:px-12 py-6 sm:py-8 champion-glow max-w-[90vw]">
                    <p className="text-[9px] sm:text-[10px] text-yellow-500/70 font-bold uppercase tracking-[0.2em] sm:tracking-[0.3em] mb-3 sm:mb-4">Campeon del Mundo 2026</p>
                    <div className="flex justify-center mb-3 sm:mb-4"><Flag team={simulation.champion} size={80} /></div>
                    <p className="text-2xl sm:text-4xl font-black text-white mb-2">{simulation.champion}</p>
                    <div className="flex items-center justify-center gap-2 mt-3 text-sm text-gray-500">
                      <span>Subcampeon:</span>
                      <Flag team={simulation.runner_up} size={20} />
                      <span className="text-gray-300 font-medium">{simulation.runner_up}</span>
                    </div>
                  </div>
                </motion.div>

                <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#e94560]" />
                  Cuadro de Eliminatorias
                </h2>
                <KnockoutBracket knockout={simulation.knockout} champion={simulation.champion} currentPhase="champion" />
              </section>
            )}
          </>
        )}

        {/* ===== STATS ===== */}
        {tab === "stats" && statsData && phase === "stats" && (
          <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <StatsView data={statsData.teams} nSimulations={statsData.nSims} />
          </motion.section>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-white/[0.04] mt-16 py-6 text-center">
        <p className="text-[11px] text-gray-700">World Cup 2026 Predictor</p>
      </footer>
    </main>
  );
}
