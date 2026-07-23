// Chatita Mail v3.0 — workflow view: open tasks & commitments across the mailbox
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckSquare, Square, Loader2, Handshake } from "lucide-react";
import { listCommitments, listTasks, updateTask } from "../api/client";
import { deadlineLabel } from "../lib/format";
import { useUI } from "../store";

export default function TasksView({ mode }: { mode: "tasks" | "commitments" }) {
  const qc = useQueryClient();
  const { selectEmail } = useUI();

  const tasksQ = useQuery({
    queryKey: ["tasks", "pending"],
    queryFn: () => listTasks("pending"),
    enabled: mode === "tasks",
  });
  const commitsQ = useQuery({
    queryKey: ["commitments", "pending"],
    queryFn: () => listCommitments("pending"),
    enabled: mode === "commitments",
  });

  const taskMut = useMutation({
    mutationFn: (v: { id: string; status: string }) => updateTask(v.id, v.status),
    onSuccess: () => qc.invalidateQueries(),
  });

  const loading = mode === "tasks" ? tasksQ.isLoading : commitsQ.isLoading;

  return (
    <div className="flex-1 overflow-y-auto bg-white">
      <div className="px-6 py-4 border-b border-slate-100">
        <h2 className="text-lg font-semibold text-slate-800">
          {mode === "tasks" ? "Open Tasks" : "Commitments"}
        </h2>
        <p className="text-xs text-slate-400">
          Extracted by AION Brain from your important emails.
        </p>
      </div>

      {loading && (
        <div className="p-6 flex items-center gap-2 text-slate-400">
          <Loader2 className="animate-spin" size={16} /> Loading…
        </div>
      )}

      <div className="max-w-3xl mx-auto p-4 space-y-2">
        {mode === "tasks" &&
          (tasksQ.data ?? []).map((t) => (
            <div
              key={t.id}
              className="flex items-start gap-3 rounded-lg border border-slate-200 bg-white p-3 hover:shadow-sm transition"
            >
              <button
                onClick={() => taskMut.mutate({ id: t.id, status: "done" })}
                className="mt-0.5 text-emerald-600"
                title="Mark done"
              >
                <Square size={18} />
              </button>
              <div className="min-w-0 flex-1">
                <div className="text-sm text-slate-800">{t.description}</div>
                <div className="flex items-center gap-2 mt-1 text-xs">
                  {t.priority && (
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-600">
                      {t.priority}
                    </span>
                  )}
                  {t.task_type && (
                    <span className="rounded-full bg-sky-50 px-2 py-0.5 text-sky-600">
                      {t.task_type}
                    </span>
                  )}
                  {t.deadline && <span className="text-rose-500">{deadlineLabel(t.deadline)}</span>}
                </div>
              </div>
              <button
                onClick={() => selectEmail(t.email_id)}
                className="text-xs text-slate-400 hover:text-slate-600"
              >
                view email →
              </button>
            </div>
          ))}

        {mode === "tasks" && !loading && (tasksQ.data ?? []).length === 0 && (
          <Empty icon={<CheckSquare size={26} />} text="No open tasks. You're all caught up." />
        )}

        {mode === "commitments" &&
          (commitsQ.data ?? []).map((c) => (
            <div
              key={c.id}
              className="flex items-start gap-3 rounded-lg border border-slate-200 bg-white p-3"
            >
              <span className="mt-0.5 text-indigo-500">🤝</span>
              <div className="min-w-0 flex-1">
                <div className="text-sm text-slate-800">
                  <b>{c.who}</b>: {c.what}
                </div>
                {c.deadline && (
                  <div className="text-xs text-rose-500 mt-1">{deadlineLabel(c.deadline)}</div>
                )}
              </div>
              <button
                onClick={() => selectEmail(c.email_id)}
                className="text-xs text-slate-400 hover:text-slate-600"
              >
                view email →
              </button>
            </div>
          ))}

        {mode === "commitments" && !loading && (commitsQ.data ?? []).length === 0 && (
          <Empty icon={<Handshake size={26} />} text="No tracked commitments yet." />
        )}
      </div>
    </div>
  );
}

function Empty({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <div className="p-12 text-center text-slate-400">
      <div className="mx-auto mb-2 grid place-items-center">{icon}</div>
      <div className="text-sm">{text}</div>
    </div>
  );
}
