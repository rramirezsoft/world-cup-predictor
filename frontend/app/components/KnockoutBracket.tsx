"use client";

import { motion } from "framer-motion";
import { MatchResult } from "../types";
import Flag from "./Flag";

interface KnockoutBracketProps {
  knockout: {
    r32: MatchResult[];
    r16: MatchResult[];
    qf: MatchResult[];
    sf: MatchResult[];
    final: MatchResult[];
  };
  champion: string;
  currentPhase?: string;
}

const ROUND_ORDER = ["r32", "r16", "qf", "sf", "final"] as const;
const ROUND_LABELS: Record<string, string> = {
  r32: "Ronda de 32",
  r16: "Octavos de Final",
  qf: "Cuartos de Final",
  sf: "Semifinales",
  final: "Final",
};

function MatchCard({
  match,
  variant = "normal",
}: {
  match: MatchResult;
  variant?: "normal" | "large" | "final";
}) {
  const isDraw = match.home_score === match.away_score;
  const isFinal = variant === "final";
  const isLarge = variant === "large" || isFinal;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={`bg-[#141b2d] rounded-lg border overflow-hidden ${
        isFinal
          ? "border-yellow-500/30 shadow-lg shadow-yellow-500/5 min-w-[260px]"
          : "border-white/[0.06] hover:border-white/[0.12] min-w-[210px]"
      } transition-colors`}
    >
      <TeamRow
        team={match.home_team}
        score={match.home_score}
        isWinner={match.winner === match.home_team}
        large={isLarge}
      />
      <div className="border-t border-white/[0.04]" />
      <TeamRow
        team={match.away_team}
        score={match.away_score}
        isWinner={match.winner === match.away_team}
        large={isLarge}
      />
      {isDraw && (
        <div className="text-center text-[9px] text-yellow-400/80 bg-yellow-400/[0.06] py-0.5 border-t border-white/[0.04]">
          Penaltis &rarr; {match.winner}
        </div>
      )}
    </motion.div>
  );
}

function TeamRow({
  team,
  score,
  isWinner,
  large,
}: {
  team: string;
  score: number;
  isWinner: boolean;
  large?: boolean;
}) {
  return (
    <div
      className={`flex items-center justify-between gap-2 ${
        large ? "px-3 py-2.5" : "px-2.5 py-1.5"
      } ${isWinner ? "bg-emerald-500/[0.06]" : ""}`}
    >
      <div className="flex items-center gap-2 flex-1 min-w-0">
        {isWinner && (
          <div className="w-0.5 h-4 rounded-full bg-emerald-500 shrink-0" />
        )}
        <Flag team={team} size={large ? 24 : 18} />
        <span
          className={`truncate ${large ? "text-sm" : "text-xs"} ${
            isWinner ? "font-bold text-emerald-400" : "text-gray-400"
          }`}
        >
          {team}
        </span>
      </div>
      <span
        className={`font-mono font-bold shrink-0 ${large ? "text-base" : "text-sm"} ${
          isWinner ? "text-white" : "text-gray-600"
        }`}
      >
        {score}
      </span>
    </div>
  );
}

export default function KnockoutBracket({
  knockout,
  champion,
  currentPhase = "champion",
}: KnockoutBracketProps) {
  const phaseIndex = ROUND_ORDER.indexOf(
    currentPhase as (typeof ROUND_ORDER)[number]
  );
  const showAll = currentPhase === "champion";

  return (
    <div className="overflow-x-auto pb-4 -mx-4 px-4">
      <div className="flex gap-6 items-start min-w-max">
        {ROUND_ORDER.map((round, roundIdx) => {
          const matches = knockout[round];
          const isVisible = showAll || roundIdx <= phaseIndex;
          const isCurrent = !showAll && round === currentPhase;

          if (!isVisible) return null;

          const variant =
            round === "final"
              ? "final"
              : round === "sf" || round === "qf"
              ? "large"
              : "normal";

          return (
            <motion.div
              key={round}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.4,
                delay: showAll ? roundIdx * 0.08 : 0,
              }}
              className="flex flex-col items-center shrink-0"
            >
              {/* Round label */}
              <div
                className={`text-[10px] font-bold uppercase tracking-widest mb-3 px-3 py-1 rounded-full ${
                  isCurrent
                    ? "bg-[#e94560]/15 text-[#e94560] border border-[#e94560]/20"
                    : round === "final"
                    ? "text-yellow-500/80"
                    : "text-gray-600"
                }`}
              >
                {ROUND_LABELS[round]}
              </div>

              {/* Matches */}
              <div
                className={`flex flex-col gap-2 ${
                  round === "final" ? "justify-center" : "justify-around"
                } flex-1`}
              >
                {matches.map((match, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{
                      delay: showAll ? roundIdx * 0.08 : idx * 0.06,
                      duration: 0.3,
                    }}
                  >
                    <MatchCard
                      match={match}
                      variant={variant as "normal" | "large" | "final"}
                    />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
