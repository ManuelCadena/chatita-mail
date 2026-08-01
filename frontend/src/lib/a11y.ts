// Chatita Mail v3.0 — T4.3 Accessibility settings.
// Persists preferences in localStorage and reflects them as data-* attributes on
// <html>, which the CSS in index.css keys off. No external deps, no network.
export type A11yKey = "dyslexia" | "large" | "contrast" | "motion";

export interface A11ySettings {
  dyslexia: boolean;
  large: boolean;
  contrast: boolean;
  motion: boolean;
}

const STORAGE_KEY = "chatita-mail-a11y";
const DEFAULTS: A11ySettings = {
  dyslexia: false,
  large: false,
  contrast: false,
  motion: false,
};

export function loadA11y(): A11ySettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : { ...DEFAULTS };
  } catch {
    return { ...DEFAULTS };
  }
}

export function saveA11y(s: A11ySettings): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  } catch {
    /* ignore quota / private-mode errors */
  }
}

/** Reflect settings onto <html data-a11y-*="1">, removing the attr when off. */
export function applyA11y(s: A11ySettings): void {
  const el = document.documentElement;
  const map: Record<A11yKey, string> = {
    dyslexia: "data-a11y-dyslexia",
    large: "data-a11y-large",
    contrast: "data-a11y-contrast",
    motion: "data-a11y-motion",
  };
  (Object.keys(map) as A11yKey[]).forEach((k) => {
    if (s[k]) el.setAttribute(map[k], "1");
    else el.removeAttribute(map[k]);
  });
}

/** Call once at startup so persisted prefs apply before first paint of content. */
export function initA11y(): A11ySettings {
  const s = loadA11y();
  applyA11y(s);
  return s;
}
