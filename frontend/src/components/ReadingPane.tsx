// Chatita Mail v3.0 — right pane: full email view + actions + XAI + Phase-2 tasks
import { useEffect, useMemo, useState } from "react";
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
  FileText,
  Reply,
  ReplyAll,
  Forward,
  Send,
  X,
  Loader2,
  Layers,
} from "lucide-react";
import {
  draftReply,
  extractTasks,
  getEmail,
  releaseFromQuarantine,
  setRead,
  forwardEmail,
  replyEmail,
  setStatus,
  similarEmails,
  summarizeEmail,
  unsubscribeEmail,
  updateTask,
  type EmailSummary,
} from "../api/client";
import { useUI } from "../store";
import { CategoryBadge, SecurityBadge } from "./badges";
import { avatarColor, deadlineLabel, fullDate, initials } from "../lib/format";
import type { EmailDetail, EmailListItem, EmailStatus } from "../types";

// ── Composer (reply / reply-all / forward) ──────────────────
type ComposeMode = "reply" | "replyAll" | "forward";
interface ComposeState {
  mode: ComposeMode;
  to: string;
  cc: string;
  subject: string;
  body: string;
  includeAttachments: boolean;
}
// Display-only: the mailbox the service account impersonates for sending.
const MAILBOX = "jose@manuelcadena.com";
const splitAddrs = (s: string) => s.split(",").map((x) => x.trim()).filter(Boolean);
const reSubject = (p: "Re:" | "Fwd:", s: string | null) => {
  const subj = (s || "").trim();
  if (p === "Re:" && /^re:/i.test(subj)) return subj;
  if (p === "Fwd:" && /^(fwd|fw):/i.test(subj)) return subj;
  return `${p} ${subj}`.trim();
};
function emptyReplyState(data: EmailDetail | undefined, mode: ComposeMode = "reply"): ComposeState {
  const cc =
    mode === "replyAll" && data
      ? [...(data.to_addresses || []), ...(data.cc_addresses || [])]
          .filter((a) => a && a !== data.from_address)
          .join(", ")
      : "";
  return {
    mode,
    to: data?.from_address ?? "",
    cc,
    subject: reSubject("Re:", data?.subject ?? null),
    body: "",
    includeAttachments: false,
  };
}
function emptyForwardState(data: EmailDetail): ComposeState {
  return {
    mode: "forward",
    to: "",
    cc: "",
    subject: reSubject("Fwd:", data.subject),
    body: "",
    includeAttachments: true,
  };
}

// Force every link inside a rendered email body to open in a NEW browser tab.
// The Mail app runs inside an iframe (chatita.ai/mail/). A default (same-frame)
// click navigates that iframe to the external URL, which most sites refuse via
// X-Frame-Options / frame-ancestors → the browser shows a blank grey
// "This content is blocked" screen. Opening top-level (_blank) loads the site
// normally and keeps Mail untouched so the user can return to it.
DOMPurify.addHook("afterSanitizeAttributes", (node) => {
  if (node.tagName === "A" && node.getAttribute("href")) {
    node.setAttribute("target", "_blank");
    node.setAttribute("rel", "noopener noreferrer");
  }
});

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

  // Phase 2: composer state
  const [summary, setSummary] = useState<EmailSummary | null>(null);
  const [tone, setTone] = useState("professional");
  const [similar, setSimilar] = useState<EmailListItem[] | null>(null);
  const [compose, setCompose] = useState<ComposeState | null>(null);

  const similarMut = useMutation({
    mutationFn: () => similarEmails(selectedEmailId as string, 8),
    onSuccess: (r) => setSimilar(r),
    onError: (e: unknown) => toast.error((e as Error).message),
  });

  const summarizeMut = useMutation({
    mutationFn: () => summarizeEmail(selectedEmailId as string),
    onSuccess: (r) => setSummary(r),
    onError: (e: unknown) => toast.error((e as Error).message),
  });
  // AI draft fills the open composer (opens a reply first if none is open).
  const draftMut = useMutation({
    mutationFn: () => draftReply(selectedEmailId as string, tone),
    onSuccess: (r) =>
      setCompose((prev) => {
        const base = prev ?? emptyReplyState(data);
        return { ...base, body: r.body, subject: base.subject || r.subject };
      }),
    onError: (e: unknown) => toast.error((e as Error).message),
  });

  const sendMut = useMutation({
    mutationFn: async () => {
      if (!compose || !selectedEmailId) throw new Error("Nada para enviar");
      const to = splitAddrs(compose.to);
      const cc = splitAddrs(compose.cc);
      if (compose.mode === "forward") {
        return forwardEmail(selectedEmailId, {
          to,
          cc,
          subject: compose.subject,
          body: compose.body,
          include_attachments: compose.includeAttachments,
        });
      }
      return replyEmail(selectedEmailId, {
        body: compose.body,
        to,
        cc,
        subject: compose.subject,
        reply_all: compose.mode === "replyAll",
      });
    },
    onSuccess: (r) => {
      toast.success(`Enviado${r.to?.length ? ` a ${r.to.join(", ")}` : ""}`);
      setCompose(null);
      refresh();
    },
    onError: (e: unknown) => toast.error((e as Error).message),
  });

  const openCompose = (mode: ComposeMode) => {
    if (!data) return;
    setCompose(mode === "forward" ? emptyForwardState(data) : emptyReplyState(data, mode));
  };

  // Clear AI summary/composer/similar when the selected email changes.
  useEffect(() => {
    setSummary(null);
    setSimilar(null);
    setCompose(null);
  }, [selectedEmailId]);

  // Open any clicked in-email link OUTSIDE the Mail iframe so external sites
  // (which refuse framing via X-Frame-Options) never render the grey
  // "This content is blocked" screen.
  //   1. Try a SEPARATE browser window (popup with dimensions).
  //   2. If the popup blocker nixes it (common inside an embedded iframe),
  //      fall back to a new top-level TAB via the native anchor (target=_blank),
  //      which browsers do NOT popup-block — so a link ALWAYS opens somewhere
  //      and Mail stays intact for the user to return to.
  const openLinkInWindow = (e: React.MouseEvent<HTMLDivElement>) => {
    const anchor = (e.target as HTMLElement).closest("a");
    const href = anchor?.getAttribute("href");
    if (!href || !/^https?:\/\//i.test(href)) return; // ignore anchors/mailto/etc.
    const w = Math.min(1280, Math.round(window.screen.availWidth * 0.8));
    const h = Math.min(900, Math.round(window.screen.availHeight * 0.85));
    const left = Math.round((window.screen.availWidth - w) / 2);
    const top = Math.round((window.screen.availHeight - h) / 2);
    let win: Window | null = null;
    try {
      win = window.open(
        href,
        "_blank",
        `popup=yes,width=${w},height=${h},left=${left},top=${top}`
      );
    } catch {
      win = null;
    }
    if (win) {
      // Popup allowed → separate window. Sever opener for security and stop the
      // native navigation so the link does NOT also load inside the iframe.
      try { win.opener = null; } catch { /* cross-origin, ignore */ }
      e.preventDefault();
    }
    // else: popup blocked → let the native target=_blank anchor open a new tab.
  };

  const sanitized = useMemo(() => {
    if (!data?.body_html) return null;
    return DOMPurify.sanitize(data.body_html, {
      FORBID_TAGS: ["script", "style", "iframe", "form", "input", "object", "embed", "base"],
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
        <div className="mx-1 h-5 w-px bg-slate-200" />
        <ToolbarBtn icon={<Reply size={16} />} label="Responder" onClick={() => openCompose("reply")} />
        <ToolbarBtn icon={<ReplyAll size={16} />} label="Resp. todos" onClick={() => openCompose("replyAll")} />
        <ToolbarBtn icon={<Forward size={16} />} label="Reenviar" onClick={() => openCompose("forward")} />
        <div className="mx-1 h-5 w-px bg-slate-200" />
        <ToolbarBtn
          icon={summarizeMut.isPending ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
          label={summarizeMut.isPending ? "Summarizing…" : "Summarize"}
          onClick={() => summarizeMut.mutate()}
          disabled={summarizeMut.isPending}
        />
        <ToolbarBtn
          icon={similarMut.isPending ? <Loader2 size={16} className="animate-spin" /> : <Layers size={16} />}
          label={similarMut.isPending ? "Buscando…" : "Similares"}
          onClick={() => similarMut.mutate()}
          disabled={similarMut.isPending}
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

        {/* AI summary (Phase 2) */}
        {summary && (
          <Panel
            icon={<FileText size={14} />}
            tone="slate"
            title={`AI summary${summary.source === "fallback" ? " (fallback)" : ""}`}
          >
            <p className="text-sm text-slate-800 mb-2">{summary.tldr}</p>
            {summary.key_points.length > 0 && (
              <ul className="list-disc list-inside text-sm text-slate-600 mb-2">
                {summary.key_points.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            )}
            {summary.suggested_action && (
              <p className="text-xs text-slate-500">
                <b>Next:</b> {summary.suggested_action}
              </p>
            )}
          </Panel>
        )}

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
            onClick={openLinkInWindow}
            // eslint-disable-next-line react/no-danger
            dangerouslySetInnerHTML={{ __html: sanitized }}
          />
        ) : (
          <div className="whitespace-pre-wrap text-sm text-slate-800 leading-relaxed">
            {data.body_text || "(empty body)"}
          </div>
        )}

        {/* Similar emails (semantic) */}
        {similar && (
          <Panel icon={<Layers size={14} />} tone="slate" title={`Emails similares (${similar.length})`}>
            {similar.length === 0 ? (
              <p className="text-sm text-slate-500">
                Sin similares aún (este correo o los relacionados pueden no estar indexados todavía).
              </p>
            ) : (
              <ul className="space-y-1">
                {similar.map((s) => (
                  <li key={s.id}>
                    <button
                      onClick={() => selectEmail(s.id)}
                      className="w-full text-left flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-white transition"
                    >
                      {typeof s.similarity === "number" && (
                        <span className="shrink-0 text-[10px] px-1.5 py-0.5 rounded-full border border-indigo-200 bg-indigo-50 text-indigo-600">
                          {Math.round(s.similarity * 100)}%
                        </span>
                      )}
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-sm text-slate-800">
                          {s.subject || "(no subject)"}
                        </span>
                        <span className="block truncate text-xs text-slate-400">
                          {s.from_name || s.from_address}
                        </span>
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </Panel>
        )}

        {/* Composer: reply / reply-all / forward (sends via gmail.send) */}
        {compose && (
          <div className="mt-6 rounded-xl border border-indigo-200 bg-indigo-50/50 p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-indigo-600">
                {compose.mode === "forward" ? (
                  <Forward size={14} />
                ) : compose.mode === "replyAll" ? (
                  <ReplyAll size={14} />
                ) : (
                  <Reply size={14} />
                )}
                {compose.mode === "forward"
                  ? "Reenviar"
                  : compose.mode === "replyAll"
                  ? "Responder a todos"
                  : "Responder"}
              </div>
              <button
                onClick={() => setCompose(null)}
                title="Cerrar"
                className="text-slate-400 hover:text-slate-600"
              >
                <X size={16} />
              </button>
            </div>

            <label className="block text-[11px] font-medium text-slate-500 mb-0.5">Para</label>
            <input
              value={compose.to}
              onChange={(e) => setCompose({ ...compose, to: e.target.value })}
              placeholder="correo@dominio.com, otro@dominio.com"
              className="w-full mb-2 rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-sm"
            />

            <label className="block text-[11px] font-medium text-slate-500 mb-0.5">CC</label>
            <input
              value={compose.cc}
              onChange={(e) => setCompose({ ...compose, cc: e.target.value })}
              placeholder="(opcional)"
              className="w-full mb-2 rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-sm"
            />

            <input
              value={compose.subject}
              onChange={(e) => setCompose({ ...compose, subject: e.target.value })}
              className="w-full mb-2 rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-sm font-medium"
            />

            <textarea
              value={compose.body}
              onChange={(e) => setCompose({ ...compose, body: e.target.value })}
              rows={9}
              placeholder="Escribe tu mensaje…"
              className="w-full rounded-md border border-slate-200 bg-white px-2.5 py-2 text-sm leading-relaxed resize-y"
            />

            {compose.mode === "forward" && (
              <label className="mt-2 flex items-center gap-2 text-xs text-slate-600">
                <input
                  type="checkbox"
                  checked={compose.includeAttachments}
                  onChange={(e) => setCompose({ ...compose, includeAttachments: e.target.checked })}
                />
                Incluir adjuntos originales
                {data.attachments?.length ? ` (${data.attachments.length})` : ""}
              </label>
            )}

            <div className="mt-3 flex items-center gap-2 flex-wrap">
              <button
                onClick={() => {
                  const dest = compose.to || "(sin destinatario)";
                  if (
                    window.confirm(
                      `Se enviará como ${MAILBOX}\n\nPara: ${dest}\nAsunto: ${compose.subject}\n\n¿Enviar ahora?`
                    )
                  ) {
                    sendMut.mutate();
                  }
                }}
                disabled={sendMut.isPending || !compose.to.trim()}
                className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 text-white text-xs px-3 py-1.5 hover:bg-indigo-500 disabled:opacity-50"
              >
                {sendMut.isPending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                {sendMut.isPending ? "Enviando…" : "Enviar"}
              </button>

              {compose.mode !== "forward" && (
                <>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="text-xs rounded-md border border-slate-200 bg-white px-2 py-1.5"
                  >
                    {["professional", "friendly", "brief", "formal", "warm"].map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => draftMut.mutate()}
                    disabled={draftMut.isPending}
                    className="inline-flex items-center gap-1.5 rounded-md border border-indigo-200 bg-white text-indigo-600 text-xs px-3 py-1.5 hover:bg-indigo-50 disabled:opacity-50"
                  >
                    {draftMut.isPending ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                    {draftMut.isPending ? "Generando…" : "Generar con IA"}
                  </button>
                </>
              )}

              <button
                onClick={() => setCompose(null)}
                className="text-xs rounded-md border border-slate-200 bg-white px-3 py-1.5 text-slate-600 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <span className="text-[11px] text-slate-400">Envía como {MAILBOX}</span>
            </div>
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
