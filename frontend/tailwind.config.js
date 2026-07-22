/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        critical: "#dc2626",
        important: "#ea580c",
        medium: "#ca8a04",
        low: "#64748b",
        spam: "#94a3b8",
        noise: "#cbd5e1",
      },
    },
  },
  plugins: [],
};
