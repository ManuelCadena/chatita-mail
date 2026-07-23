// Chatita Mail v3.0 — category & security badges
import type { EmailCategory, RiskLevel } from "../types";
import { CATEGORY_META, RISK_META } from "../lib/format";

export function CategoryBadge({
  category,
  size = "sm",
}: {
  category: EmailCategory | null;
  size?: "sm" | "xs";
}) {
  if (!category) return null;
  const m = CATEGORY_META[category];
  const pad = size === "xs" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-0.5 text-xs";
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border font-medium ${pad} ${m.chip}`}
    >
      <span>{m.emoji}</span>
      {m.label}
    </span>
  );
}

export function SecurityBadge({
  level,
  score,
  size = "sm",
}: {
  level: RiskLevel | null;
  score?: number | null;
  size?: "sm" | "xs";
}) {
  if (!level || level === "safe") return null;
  const m = RISK_META[level];
  const pad = size === "xs" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-0.5 text-xs";
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border font-medium ${pad} ${m.chip}`}
    >
      <span>{m.emoji}</span>
      {m.label}
      {typeof score === "number" ? ` ${score}` : ""}
    </span>
  );
}

export function Dot({ category }: { category: EmailCategory | null }) {
  if (!category) return <span className="h-2 w-2 rounded-full bg-slate-300" />;
  return <span className={`h-2 w-2 rounded-full ${CATEGORY_META[category].dot}`} />;
}
