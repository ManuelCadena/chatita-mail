import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listEmails } from "./api/client";
import type { EmailCategory } from "./types";
import { CategoryBadge, SecurityBadge } from "./components/badges";
import EmailDetail from "./components/EmailDetail";

const FILTERS: { label: string; value: EmailCategory | "ALL" }[] = [
  { label: "All", value: "ALL" },
  { label: "🔴 Critical", value: "CRITICAL" },
  { label: "🟠 Important", value: "IMPORTANT" },
  { label: "🟡 Medium", value: "MEDIUM" },
  { label: "⚪ Low", value: "LOW" },
];

export default function App() {
  const [filter, setFilter] = useState<EmailCategory | "ALL">("ALL");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: emails = [], isLoading } = useQuery({
    queryKey: ["emails", filter],
    queryFn: () =>
      listEmails({
        status: "INBOX",
        category: filter === "ALL" ? undefined : filter,
        limit: 100,
      }),
  });

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold">📬 Chatita Mail</span>
          <span className="text-xs text-slate-400">v3.0</span>
        </div>
        <span className="text-xs text-slate-400">≤5 min/day · AION Brain</span>
      </header>

      {/* Filters */}
      <div className="border-b border-slate-200 bg-white px-4 py-2 flex gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`text-sm px-3 py-1 rounded-full border transition ${
              filter === f.value
                ? "bg-slate-800 text-white border-slate-800"
                : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Body: list + detail */}
      <div className="flex-1 flex overflow-hidden">
        {/* List */}
        <div className="w-96 border-r border-slate-200 overflow-y-auto bg-white">
          {isLoading && <div className="p-4 text-slate-400">Loading…</div>}
          {!isLoading && emails.length === 0 && (
            <div className="p-6 text-center text-slate-400">
              Inbox zero 🎉<br />No emails in this view.
            </div>
          )}
          {emails.map((e) => (
            <button
              key={e.id}
              onClick={() => setSelectedId(e.id)}
              className={`w-full text-left px-4 py-3 border-b border-slate-100 hover:bg-slate-50 ${
                selectedId === e.id ? "bg-slate-100" : ""
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <CategoryBadge category={e.category} />
                <SecurityBadge level={e.risk_level} score={e.risk_score} />
              </div>
              <div className="text-sm font-medium truncate">
                {e.from_name || e.from_address}
              </div>
              <div className="text-sm text-slate-700 truncate">
                {e.subject || "(no subject)"}
              </div>
              <div className="text-xs text-slate-400 truncate">{e.snippet}</div>
            </button>
          ))}
        </div>

        {/* Detail (XAI) */}
        <EmailDetail emailId={selectedId} />
      </div>
    </div>
  );
}
