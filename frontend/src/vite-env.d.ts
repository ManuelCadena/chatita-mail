/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** API base URL. Local dev: "/api" (Vite proxy). Prod: "/mail-api". */
  readonly VITE_API_BASE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
