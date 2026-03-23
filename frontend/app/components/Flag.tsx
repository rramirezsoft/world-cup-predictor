"use client";

import { getFlagUrl } from "../types";

interface FlagProps {
  team: string;
  size?: number;
  className?: string;
}

export default function Flag({ team, size = 24, className = "" }: FlagProps) {
  const url = getFlagUrl(team, size <= 20 ? 20 : size <= 40 ? 40 : 80);

  if (!url) {
    return (
      <div
        className={`bg-white/10 rounded-sm flex items-center justify-center text-[8px] text-gray-500 ${className}`}
        style={{ width: size, height: size * 0.67 }}
      >
        {team.slice(0, 2)}
      </div>
    );
  }

  return (
    <img
      src={url}
      alt={team}
      width={size}
      height={Math.round(size * 0.67)}
      className={`flag-img ${className}`}
      loading="lazy"
    />
  );
}
