// Chatita Mail v3.0 — T4.3 Accessibility menu (header popover).
import { useEffect, useRef, useState } from "react";
import { Accessibility, Check } from "lucide-react";
import { applyA11y, loadA11y, saveA11y, type A11yKey, type A11ySettings } from "../lib/a11y";

const OPTIONS: { key: A11yKey; label: string; hint: string }[] = [
  { key: "dyslexia", label: "Fuente para dislexia", hint: "Tipografía legible + más espaciado" },
  { key: "large", label: "Texto grande", hint: "Aumenta el tamaño base 18%" },
  { key: "contrast", label: "Alto contraste", hint: "Texto y bordes más oscuros" },
  { key: "motion", label: "Reducir animaciones", hint: "Minimiza transiciones" },
];

export default function AccessibilityMenu() {
  const [open, setOpen] = useState(false);
  const [settings, setSettings] = useState<A11ySettings>(loadA11y);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    applyA11y(settings);
    saveA11y(settings);
  }, [settings]);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const toggle = (k: A11yKey) => setSettings((s) => ({ ...s, [k]: !s[k] }));
  const activeCount = Object.values(settings).filter(Boolean).length;

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        title="Accesibilidad"
        aria-label="Opciones de accesibilidad"
        aria-expanded={open}
        className="relative inline-flex items-center justify-center h-8 w-8 rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-700"
      >
        <Accessibility size={18} />
        {activeCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 h-3.5 w-3.5 rounded-full bg-indigo-600 text-white text-[8px] grid place-items-center">
            {activeCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-72 rounded-xl border border-slate-200 bg-white shadow-lg p-2 z-50">
          <div className="px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            Accesibilidad
          </div>
          {OPTIONS.map((o) => (
            <button
              key={o.key}
              onClick={() => toggle(o.key)}
              role="switch"
              aria-checked={settings[o.key]}
              className="w-full text-left flex items-start gap-2.5 rounded-lg px-2 py-2 hover:bg-slate-50"
            >
              <span
                className={`mt-0.5 h-4 w-4 shrink-0 rounded border grid place-items-center ${
                  settings[o.key]
                    ? "bg-indigo-600 border-indigo-600 text-white"
                    : "border-slate-300 bg-white"
                }`}
              >
                {settings[o.key] && <Check size={12} />}
              </span>
              <span>
                <span className="block text-sm text-slate-700">{o.label}</span>
                <span className="block text-[11px] text-slate-400">{o.hint}</span>
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
