"use client";

import { motion } from "framer-motion";
import { GroupData } from "../types";
import Flag from "./Flag";

interface GroupTableProps {
  groupName: string;
  data: GroupData;
}

export default function GroupTable({ groupName, data }: GroupTableProps) {
  return (
    <div className="bg-[#141b2d] rounded-xl border border-white/[0.06] overflow-hidden hover:border-white/[0.12] transition-all duration-300 group/card">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#e94560] to-[#c73e54] px-4 py-2.5 flex items-center justify-between">
        <h3 className="text-white font-bold text-sm tracking-wide">
          GRUPO {groupName}
        </h3>
        <span className="text-white/50 text-[10px] font-medium">
          {data.matches.length} partidos
        </span>
      </div>

      {/* Standings */}
      <table className="w-full text-sm">
        <thead>
          <tr className="text-[10px] text-gray-500 uppercase tracking-wider border-b border-white/[0.04]">
            <th className="text-left pl-3 pr-1 py-2 w-5">#</th>
            <th className="text-left px-2 py-2">Equipo</th>
            <th className="text-center w-7 py-2">PJ</th>
            <th className="text-center w-7 py-2">G</th>
            <th className="text-center w-7 py-2">E</th>
            <th className="text-center w-7 py-2">P</th>
            <th className="text-center w-9 py-2">DG</th>
            <th className="text-center w-9 py-2 text-white/80">Pts</th>
          </tr>
        </thead>
        <tbody>
          {data.standings.map((team, idx) => {
            // Green for qualified (top 2), yellow for possible 3rd, red for eliminated
            const qualBorder =
              idx < 2
                ? "border-l-emerald-500"
                : idx === 2
                ? "border-l-yellow-500"
                : "border-l-red-500/50";
            const qualBg =
              idx < 2
                ? "bg-emerald-500/[0.04]"
                : idx === 2
                ? "bg-yellow-500/[0.03]"
                : "";

            return (
              <motion.tr
                key={team.team}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.08, duration: 0.3 }}
                className={`border-b border-white/[0.03] border-l-2 ${qualBorder} ${qualBg} table-row-hover`}
              >
                <td className="pl-3 pr-1 py-1.5 text-gray-600 text-[10px] font-medium">
                  {idx + 1}
                </td>
                <td className="px-2 py-1.5">
                  <div className="flex items-center gap-2">
                    <Flag team={team.team} size={20} />
                    <span className="font-medium text-xs text-gray-200 truncate">
                      {team.team}
                    </span>
                  </div>
                </td>
                <td className="text-center py-1.5 text-gray-500 text-[11px]">
                  {team.played}
                </td>
                <td className="text-center py-1.5 text-emerald-400/80 text-[11px] font-medium">
                  {team.wins}
                </td>
                <td className="text-center py-1.5 text-gray-500 text-[11px]">
                  {team.draws}
                </td>
                <td className="text-center py-1.5 text-red-400/80 text-[11px] font-medium">
                  {team.losses}
                </td>
                <td className="text-center py-1.5 text-[11px]">
                  <span
                    className={
                      team.gd > 0
                        ? "text-emerald-400/80"
                        : team.gd < 0
                        ? "text-red-400/80"
                        : "text-gray-600"
                    }
                  >
                    {team.gd > 0 ? "+" : ""}
                    {team.gd}
                  </span>
                </td>
                <td className="text-center py-1.5 font-bold text-white text-xs">
                  {team.points}
                </td>
              </motion.tr>
            );
          })}
        </tbody>
      </table>

      {/* Matches */}
      <div className="px-3 py-2 space-y-0.5 border-t border-white/[0.04] bg-black/20">
        {data.matches.map((match, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between text-[10px] py-0.5"
          >
            <span
              className={`flex-1 text-right truncate flex items-center justify-end gap-1.5 ${
                match.winner === match.home_team
                  ? "text-emerald-400 font-semibold"
                  : "text-gray-500"
              }`}
            >
              <span className="truncate">{match.home_team}</span>
              <Flag team={match.home_team} size={14} />
            </span>
            <span className="mx-2 bg-white/[0.06] px-2 py-0.5 rounded font-mono font-bold text-white min-w-[34px] text-center text-[10px]">
              {match.home_score} - {match.away_score}
            </span>
            <span
              className={`flex-1 text-left truncate flex items-center gap-1.5 ${
                match.winner === match.away_team
                  ? "text-emerald-400 font-semibold"
                  : "text-gray-500"
              }`}
            >
              <Flag team={match.away_team} size={14} />
              <span className="truncate">{match.away_team}</span>
            </span>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="px-3 py-1.5 border-t border-white/[0.03] flex gap-3 text-[9px] text-gray-600">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-emerald-500/60" /> Clasifica
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-yellow-500/60" /> Posible 3ro
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red-500/40" /> Eliminado
        </span>
      </div>
    </div>
  );
}
