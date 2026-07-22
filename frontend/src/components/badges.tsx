import type { EmailCategory, RiskLevel } from "../types";

const CATEGORY_STYLE: Record<EmailCategory, string> = {
  CRITICAL: "bg-red-100 text-red-700 border-red-300",
  IMPORTANT: "bg-orange-100 text-orange-700 border-orange-300",
  MEDIUM: "bg-yellow-100 text-yellow-700 border-yellow-300",
  LOW: "bg-slate-100 text-slate-600 border-slate-300",
  SPAM: "bg-slate-200 text-slate-500 border-slate-300",
  NOISE: "bg-slate-100 text-slate-400 border-slate-200",
  UNCLASSIFIED: "bg-slate-50 text-slate-400 border-slate-200",
};

export function CategoryBadge({ category }: { category: EmailCategory | null }) {
  if (!category) return null;
  return (
    <span
      className={`text-xs font-semibold px-2 py-0.5 rounded border ${CATEGORY_STYLE[category]}`}
    >
      {category}
    </span>
  );
}

const RISK_STYLE: Record<RiskLevel, string> = {
  safe: "bg-green-100 text-green-700 border-green-300",
  suspicious: "bg-amber-100 text-amber-700 border-amber-300",
  dangerous: "bg-red-100 text-red-700 border-red-300",
};

export function SecurityBadge({
  level,
  score,
}: {
  level: RiskLevel | null;
  score: number | null;
}) {
  if (!level || level === "safe") return null;
  return (
    <span
      className={`text-xs font-semibold px-2 py-0.5 rounded border ${RISK_STYLE[level]}`}
      title={`Risk score: ${score ?? "?"}/100`}
    >
      🛡 {level.toUpperCase()} {score ?? ""}
    </span>
  );
}
