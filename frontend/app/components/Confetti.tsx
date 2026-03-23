"use client";

import { useEffect, useState } from "react";

const COLORS = ["#ffd700", "#e94560", "#22c55e", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899", "#ffffff"];

interface ConfettiPiece {
  id: number;
  left: number;
  color: string;
  size: number;
  duration: number;
  delay: number;
  shape: "square" | "rect" | "circle";
}

export default function Confetti() {
  const [pieces, setPieces] = useState<ConfettiPiece[]>([]);

  useEffect(() => {
    const generated: ConfettiPiece[] = [];
    for (let i = 0; i < 80; i++) {
      generated.push({
        id: i,
        left: Math.random() * 100,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        size: Math.random() * 8 + 4,
        duration: Math.random() * 2 + 2,
        delay: Math.random() * 1.5,
        shape: (["square", "rect", "circle"] as const)[Math.floor(Math.random() * 3)],
      });
    }
    setPieces(generated);

    const timer = setTimeout(() => setPieces([]), 5000);
    return () => clearTimeout(timer);
  }, []);

  if (pieces.length === 0) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-[100] overflow-hidden">
      {pieces.map((p) => (
        <div
          key={p.id}
          className="confetti-piece"
          style={{
            left: `${p.left}%`,
            width: p.shape === "rect" ? p.size * 0.4 : p.size,
            height: p.shape === "circle" ? p.size : p.size * (p.shape === "rect" ? 1.5 : 1),
            backgroundColor: p.color,
            borderRadius: p.shape === "circle" ? "50%" : "1px",
            animationDuration: `${p.duration}s, 0.4s`,
            animationDelay: `${p.delay}s, ${p.delay}s`,
          }}
        />
      ))}
    </div>
  );
}
