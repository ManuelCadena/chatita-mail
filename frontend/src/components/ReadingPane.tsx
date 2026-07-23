// Chatita Mail v3.0 — right pane: full email view + actions + XAI + Phase-2 tasks
import { useMemo } from "react";
import DOMPurify from "dompurify";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  Archive,
  Ban,
  CheckSquare,
  Square,
  MailOpen,
  ShieldCheck,
  Sparkles,
  Trash2,
  Paperclip,
  Bot,
  ShieldAlert,
} from "lucide-react";
import {
  extractTasks,
  getEmail,
  releaseFromQuarantine,
  setRead,
  setStatus,
  unsubscribeEmail,
  updateTask,
} from "../api/client";
import { useUI } from "../store";
import { CategoryBadge, SecurityBadge } from "./badges";
import { avatarColor, deadlineLabel, fullDate, initials } from "../lib/format";
import type { EmailStatus } from "../types";

export default function ReadingPane() {
  const { selectedEmailId, selectEmail } = useUI();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["email", selectedEmailId],
    queryFn: () => getEmail(selectedEmailId as string),
    enabled: !!selectedEmailId,
  });

  const refresh = () => qc.invalidateQueries();

  const statusMut = useMutation({
    mutationFn: (s: EmailStatus) => setStatus(selectedEmailId as string, s),
    onSuccess: (_d, s) => {
      toast.success(`Moved to ${s}`);
      selectEmail(null);
      refresh();
    },
  });
  const readMut = useMutation({
    mutationFn: (r: boolean) => setRead(selectedEmailId as string, r),
    onSuccess: () => refresh(),
  });
  const unsubMut = useMutation({
    mutationFn: () => unsubscribeEmail(selectedEmailId as string),
    onSuccess: (r) => {
      toast.success(r?.ok ? "Unsubscribed" : "Unsubscribe attempted");
      refresh();
    },
    onError: (e: unknown) => toast.error((e as Error).message),
  });
  const releaseMut = useMutation({
    mutationFn: () => releaseFromQuarantine(selectedEmailId as string),
    onSuccess: () => {
      toast.success("Released to inbox");
      refresh();
    },
  });
  const extractMut = useMutation({
    mutationFn: () => extractTasks(selectedEmailId as string),
    onSuccess: (r) => {
      toast.success(`Extracted ${r.tasks_extracted} task(s), ${r.commitments_extracted} commitment(s)`);
      refresh();
    },
    onError: (e: unknown) => toast.error((e as Error).message),
  });
  const taskMut = useMutation({
    mutationFn: (v: { id: string; status: string }) => updateTask(v.id, v.status),
    onSuccess: () => refresh(),
  });

  const sanitized = useMemo(() => {
    if (!data?.body_html) return null;
    return DOMPurify.sanitize(data.body_html, {
      FORBID_TAGS: ["script", "style", "iframe", "form", "input", "object", "embed"],
      FORBID_ATTR: ["onerror", "onload", "onclick"],
      ADD_ATTR: ["target"],
    });
  }, [data?.body_html]);

  if (!selectedEmailId) {
    return (
      <div className="flex-1 grid place-items-center text-slate-400">
        <div className="text-center">
          <MailOpen className="mx-auto mb-2" size={32} />
          <div>Select an email to read</div>
        </div>
      </div>
    );
  }

  if (isLoading || !data) {
    return <div className="flex-1 p-8 text-slate-400">Loading…</div>;
  }

  const name = data.from_name || data.from_address;
  const isQuarantined = data.status === "QUARANTINED" || data.status === "BLOCKED";

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-white">
      {/* Toolbar */}
      <div className="px-5 py-2.5 border-b border-slate-100 flex items-center gap-1.5 flex-wrap">
        <ToolbarBtn icon={<Archive size={16} />} label="Archive" onClick={() => statusMut.mutate("ARCHIVED")} />
        <ToolbarBtn icon={<Trash2 size={16} />} label="Delete" onClick={() => statusMut.mutate("DELETED")} />
        <ToolbarBtn
          icon={data.is_read ? <MailOpen size={16} /> : <MailOpen size={16} />}
          label={data.is_read ? "Mark unread" : "Mark read"}
          onClick={() => readMut.mutate(!data.is_read)}
        />
        {data.classification?.unsubscribe_url && (
          <ToolbarBtn icon={<Ban size={16} />} label="Unsubscribe" onClick={() => unsubMut.mutate()} />
        )}
        {isQuarantined && (
          <ToolbarBtn icon={<ShieldCheck size={16} />} label="Release" onClick={() => releaseMut.mutate()} />
        )}
        <ToolbarBtn
          icon={<Sparkles size={16} />}
          label={extractMut.isPending ? "Extracting…" : "Extract tasks"}
          onClick={() => extractMut.mutate()}
          disabled={extractMut.isPending}
        />
      </div>

      {/* Scroll body */}
      <div className="flex-1 overflow-y-auto px-6 py-5">
        <h1 className="text-2xl font-semibold text-slate-900 mb-3">
          {data.subject || "(no subject)"}
        </h1>

        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <CategoryBadge category={data.classification?.category ?? null} />
          <SecurityBadge
            level={data.security?.risk_level ?? null}
            score={data.security?.risk_score ?? null}
          />
        </div>

        {/* Sender block */}
        <div className="flex items-start gap-3 pb-4 mb-4 border-b border-slate-100">
          <div
            className={`h-10 w-10 shrink-0 rounded-full grid place-items-center text-white text-sm font-semibold ${avatarColor(
              name
            )}`}
          >
            {initials(data.from_name, data.from_address)}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-sm font-medium text-slate-800">
              {data.from_name ? `${data.from_name} ` : ""}
              <span className="text-slate-400 font-normal">&lt;{data.from_address}&gt;</span>
            </div>
            {data.to_addresses?.length > 0 && (
              <div className="text-xs text-slate-400 truncate">
                to {data.to_addresses.join(", ")}
              </div>
            )}
            <div className="text-xs text-slate-400">{fullDate(data.received_at)}</div>
          </div>
        </div>

        {/* XAI: classification */}
        {data.classification?.reasoning && (
          <Panel
            icon={<Bot size={14} />}
            tone="slate"
            title={`Why ${data.classification.category} · ${Math.round(
              (data.classification.confidence ?? 0) * 100
            )}% · ${data.classification.stage}`}
          >
            <p className="text-sm text-slate-700">{data.classification.reasoning}</p>
          </Panel>
        )}

        {/* XAI: security */}
        {data.security && data.security.risk_level !== "safe" && (
          <Panel
            icon={<ShieldAlert size={14} />}
            tone="amber"
            title={`Security: ${data.security.risk_level} (${data.security.risk_score}/100) · ${data.security.recommended_action}`}
          >
            {data.security.explanation && (
              <p className="text-sm text-amber-800 mb-1">{data.security.explanation}</p>
            )}
            {data.security.risk_factors?.length > 0 && (
              <ul className="list-disc list-inside text-sm text-amber-800">
                {data.security.risk_factors.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            )}
          </Panel>
        )}

        {/* Phase 2: tasks & commitments */}
        {(data.tasks.length > 0 || data.commitments.length > 0) && (
          <Panel icon={<CheckSquare size={14} />} tone="emerald" title="Action items (AION)">
            <ul className="space-y-1.5">
              {data.tasks.map((t) => (
                <li key={t.id} className="flex items-start gap-2 text-sm">
                  <button
                    onClick={() =>
                      taskMut.mutate({ id: t.id, status: t.status === "done" ? "pending" : "done" })
                    }
                    className="mt-0.5 text-emerald-600"
                  >
                    {t.status === "done" ? <CheckSquare size={16} /> : <Square size={16} />}
                  </button>
                  <span className={t.status === "done" ? "line-through text-slate-400" : "text-slate-700"}>
                    {t.description}
                    {t.deadline && (
                      <span className="ml-1 text-xs text-rose-500">· {deadlineLabel(t.deadline)}</span>
                    )}
                  </span>
                </li>
              ))}
              {data.commitments.map((c) => (
                <li key={c.id} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="mt-0.5 text-indigo-500">🤝</span>
                  <span>
                    <b>{c.who}</b>: {c.what}
                    {c.deadline && (
                      <span className="ml-1 text-xs text-rose-500">· {deadlineLabel(c.deadline)}</span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </Panel>
        )}

        {/* Attachments */}
        {data.attachments?.length > 0 && (
          <div className="mb-4 flex flex-wrap gap-2">
            {data.attachments.map((a, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs text-slate-600"
              >
                <Paperclip size={12} />
                {a.filename || `attachment-${i + 1}`}
              </span>
            ))}
          </div>
        )}

        {/* Body */}
        {sanitized ? (
          <div
            className="email-html prose prose-sm max-w-none text-slate-800"
            // eslint-disable-next-line react/no-danger
            dangerouslySetInnerHTML={{ __html: sanitized }}
          />
        ) : (
          <div className="whitespace-pre-wrap text-sm text-slate-800 leading-relaxed">
            {data.body_text || "(empty body)"}
          </div>
        )}
      </div>
    </div>
  );
}

function ToolbarBtn({
  icon,
  label,
  onClick,
  disabled,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 transition disabled:opacity-50"
    >
      {icon}
      {label}
    </button>
  );
}

const TONES: Record<string, string> = {
  slate: "border-slate-200 bg-slate-50",
  amber: "border-amber-200 bg-amber-50",
  emerald: "border-emerald-200 bg-emerald-50",
};

function Panel({
  icon,
  title,
  tone,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  tone: keyof typeof TONES | string;
  children: React.ReactNode;
}) {
  return (
    <div className={`mb-4 rounded-lg border p-3.5 ${TONES[tone] ?? TONES.slate}`}>
      <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5">
        {icon}
        {title}
      </div>
      {children}
    </div>
  );
}
