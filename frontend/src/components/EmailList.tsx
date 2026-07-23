// Chatita Mail v3.0 — middle pane: email list for the active folder
import { useQuery } from "@tanstack/react-query";
import { Paperclip, Loader2, Inbox as InboxIcon } from "lucide-react";
import { listEmails } from "../api/client";
import { folderByKey, useUI } from "../store";
import { CategoryBadge, SecurityBadge } from "./badges";
import { avatarColor, initials, relativeDate } from "../lib/format";

export default function EmailList() {
  const { folderKey, selectedEmailId, selectEmail, search, unreadOnly } = useUI();
  const folder = folderByKey(folderKey);

  const { data: emails = [], isLoading } = useQuery({
    queryKey: ["emails", folder.key, folder.status, folder.category, search, unreadOnly],
    queryFn: () =>
      listEmails({
        status: folder.status,
        category: folder.category,
        search: search || undefined,
        unread_only: unreadOnly || undefined,
        limit: 100,
      }),
    refetchInterval: 20000,
  });

  return (
    <div className="w-[380px] shrink-0 border-r border-slate-200 bg-white flex flex-col">
      <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
        <h2 className="font-semibold text-slate-800">{folder.label}</h2>
        <span className="text-xs text-slate-400">{emails.length} shown</span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading && (
          <div className="p-6 flex items-center gap-2 text-slate-400">
            <Loader2 className="animate-spin" size={16} /> Loading…
          </div>
        )}

        {!isLoading && emails.length === 0 && (
          <div className="p-10 text-center text-slate-400">
            <InboxIcon className="mx-auto mb-2" size={28} />
            <div className="font-medium">Nothing here</div>
            <div className="text-xs mt-1">
              {search ? "No matches for your search." : "Inbox zero 🎉"}
            </div>
          </div>
        )}

        {emails.map((e) => {
          const active = selectedEmailId === e.id;
          const name = e.from_name || e.from_address;
          return (
            <button
              key={e.id}
              onClick={() => selectEmail(e.id)}
              className={`w-full text-left px-3 py-3 border-b border-slate-100 flex gap-3 transition ${
                active ? "bg-slate-100" : "hover:bg-slate-50"
              } ${!e.is_read ? "bg-blue-50/40" : ""}`}
            >
              {/* Avatar */}
              <div
                className={`h-9 w-9 shrink-0 rounded-full grid place-items-center text-white text-xs font-semibold ${avatarColor(
                  name
                )}`}
              >
                {initials(e.from_name, e.from_address)}
              </div>

              {/* Content */}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  {!e.is_read && <span className="h-2 w-2 rounded-full bg-blue-500 shrink-0" />}
                  <span
                    className={`truncate text-sm ${
                      !e.is_read ? "font-semibold text-slate-900" : "text-slate-700"
                    }`}
                  >
                    {name}
                  </span>
                  <span className="ml-auto text-[11px] text-slate-400 shrink-0">
                    {relativeDate(e.received_at)}
                  </span>
                </div>

                <div
                  className={`truncate text-sm ${
                    !e.is_read ? "font-medium text-slate-800" : "text-slate-600"
                  }`}
                >
                  {e.subject || "(no subject)"}
                </div>

                <div className="truncate text-xs text-slate-400">{e.snippet}</div>

                <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
                  <CategoryBadge category={e.category} size="xs" />
                  <SecurityBadge level={e.risk_level} score={e.risk_score} size="xs" />
                  {e.is_newsletter && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full border border-sky-200 bg-sky-50 text-sky-600">
                      Newsletter
                    </span>
                  )}
                  {e.has_attachments && <Paperclip size={12} className="text-slate-400" />}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
