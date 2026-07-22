import { useQuery } from "@tanstack/react-query";
import { getEmail } from "../api/client";
import { CategoryBadge, SecurityBadge } from "./badges";

export default function EmailDetail({ emailId }: { emailId: string | null }) {
  const { data, isLoading } = useQuery({
    queryKey: ["email", emailId],
    queryFn: () => getEmail(emailId as string),
    enabled: !!emailId,
  });

  if (!emailId) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-400">
        Select an email to view details
      </div>
    );
  }

  if (isLoading || !data) {
    return <div className="flex-1 p-6 text-slate-400">Loading…</div>;
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="flex items-center gap-2 mb-2">
        <CategoryBadge category={data.classification?.category ?? null} />
        <SecurityBadge
          level={data.security?.risk_level ?? null}
          score={data.security?.risk_score ?? null}
        />
      </div>

      <h1 className="text-xl font-semibold mb-1">
        {data.subject || "(no subject)"}
      </h1>
      <p className="text-sm text-slate-500 mb-4">
        {data.from_name ? `${data.from_name} · ` : ""}
        {data.from_address}
      </p>

      {/* XAI: Classification reasoning */}
      {data.classification?.reasoning && (
        <div className="mb-4 rounded-lg border border-slate-200 bg-white p-4">
          <div className="text-xs font-semibold uppercase text-slate-400 mb-1">
            🤖 Why this category ({Math.round((data.classification.confidence ?? 0) * 100)}% ·{" "}
            {data.classification.stage})
          </div>
          <p className="text-sm text-slate-700">{data.classification.reasoning}</p>
        </div>
      )}

      {/* XAI: Security explanation */}
      {data.security && data.security.risk_level !== "safe" && (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="text-xs font-semibold uppercase text-amber-600 mb-1">
            🛡 Security: {data.security.risk_level} ({data.security.risk_score}/100) ·{" "}
            {data.security.recommended_action}
          </div>
          <p className="text-sm text-amber-800 mb-2">{data.security.explanation}</p>
          {data.security.risk_factors.length > 0 && (
            <ul className="list-disc list-inside text-sm text-amber-800">
              {data.security.risk_factors.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Body */}
      <div className="rounded-lg border border-slate-200 bg-white p-4 whitespace-pre-wrap text-sm text-slate-800">
        {data.body_text || "(empty body)"}
      </div>
    </div>
  );
}
