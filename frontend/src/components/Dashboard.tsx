// Chatita Mail v3.0 — T4.4 Analytics dashboard.
// Visualizes ROI of the ≤5 min/day goal: time saved, throughput, reply rate,
// top senders, and inbound volume over time. All numbers come from real DB
// aggregates (GET /inbox/analytics) — no mock data.
import { useQuery } from "@tanstack/react-query";
import { Clock, Inbox, Send, ShieldCheck, Reply, TrendingUp, Loader2 } from "lucide-react";
import { getAnalytics, type Analytics } from "../api/client";

function StatCard({
  icon,
  label,
  value,
  hint,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center gap-2 text-slate-500 text-xs font-medium">
        {icon}
        {label}
      </div>
      <div className="mt-1.5 text-2xl font-bold text-slate-800">{value}</div>
      {hint && <div className="text-[11px] text-slate-400 mt-0.5">{hint}</div>}
    </div>
  );
}

function VolumeChart({ data }: { data: Analytics["volume_by_day"] }) {
  if (!data.length) return <div className="text-sm text-slate-400">Sin datos en el periodo.</div>;
  const max = Math.max(...data.map((d) => d.count), 1);
  return (
    <div className="flex items-end gap-1 h-32">
      {data.map((d) => (
        <div key={d.date} className="flex-1 flex flex-col items-center justify-end group">
          <div
            className="w-full rounded-t bg-indigo-400 group-hover:bg-indigo-600 transition"
            style={{ height: `${Math.max((d.count / max) * 100, 2)}%` }}
            title={`${d.date}: ${d.count}`}
          />
          <div className="text-[8px] text-slate-400 mt-1 rotate-45 origin-left whitespace-nowrap">
            {d.date.slice(5)}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["analytics", 14],
    queryFn: () => getAnalytics(14),
    refetchInterval: 30000,
  });

  if (isLoading)
    return (
      <div className="flex-1 grid place-items-center text-slate-400">
        <Loader2 className="animate-spin" />
      </div>
    );
  if (isError || !data)
    return <div className="flex-1 grid place-items-center text-slate-400">No se pudo cargar el panel.</div>;

  const h = Math.floor(data.time_saved_minutes / 60);
  const m = data.time_saved_minutes % 60;

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-slate-50">
      <h2 className="text-lg font-bold text-slate-800 mb-1">Panel de analíticas</h2>
      <p className="text-xs text-slate-500 mb-5">
        ROI de la meta ≤5 min/día · ventana {data.window_days} días · datos en vivo
      </p>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
        <StatCard
          icon={<Clock size={14} />}
          label="Tiempo ahorrado"
          value={`${h}h ${m}m`}
          hint={`${data.auto_handled.toLocaleString()} auto-gestionados`}
        />
        <StatCard icon={<Inbox size={14} />} label="Recibidos" value={data.received.toLocaleString()} />
        <StatCard icon={<Send size={14} />} label="Enviados" value={data.sent.toLocaleString()} />
        <StatCard
          icon={<Reply size={14} />}
          label="Tasa de respuesta"
          value={`${Math.round(data.reply_rate * 100)}%`}
          hint={`${data.actionable.toLocaleString()} accionables`}
        />
        <StatCard
          icon={<ShieldCheck size={14} />}
          label="Total"
          value={data.total.toLocaleString()}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-3">
            <TrendingUp size={15} className="text-indigo-500" /> Volumen recibido (por día)
          </div>
          <VolumeChart data={data.volume_by_day} />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="text-sm font-semibold text-slate-700 mb-3">Top remitentes</div>
          <div className="space-y-1.5">
            {data.top_senders.length === 0 && (
              <div className="text-sm text-slate-400">Sin datos.</div>
            )}
            {data.top_senders.map((s, i) => (
              <div key={s.sender} className="flex items-center gap-2 text-sm">
                <span className="text-slate-400 w-4 text-right">{i + 1}</span>
                <span className="flex-1 truncate text-slate-700" title={s.sender}>
                  {s.sender}
                </span>
                <span className="text-xs font-medium text-slate-500">
                  {s.count.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
