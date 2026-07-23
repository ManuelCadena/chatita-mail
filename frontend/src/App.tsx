// Chatita Mail v3.0 — application shell (3-pane: Sidebar | List | Reading)
import { Search, Filter } from "lucide-react";
import Sidebar from "./components/Sidebar";
import EmailList from "./components/EmailList";
import ReadingPane from "./components/ReadingPane";
import TasksView from "./components/TasksView";
import { useUI } from "./store";

export default function App() {
  const { folderKey, search, setSearch, unreadOnly, toggleUnreadOnly } = useUI();
  const isWorkflow = folderKey === "tasks" || folderKey === "commitments";

  return (
    <div className="h-screen flex bg-slate-100 text-slate-900">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-14 shrink-0 border-b border-slate-200 bg-white px-4 flex items-center gap-3">
          <div className="relative flex-1 max-w-xl">
            <Search
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search sender, subject, content…"
              className="w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
            />
          </div>

          <button
            onClick={toggleUnreadOnly}
            className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-2 text-sm transition ${
              unreadOnly
                ? "border-slate-900 bg-slate-900 text-white"
                : "border-slate-200 text-slate-600 hover:bg-slate-50"
            }`}
          >
            <Filter size={14} />
            Unread
          </button>

          <span className="text-xs text-slate-400 hidden md:block">
            ≤5 min/day · AION Brain
          </span>
        </header>

        {/* Panes */}
        <div className="flex-1 flex overflow-hidden">
          {isWorkflow ? (
            <TasksView mode={folderKey as "tasks" | "commitments"} />
          ) : (
            <>
              <EmailList />
              <ReadingPane />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
