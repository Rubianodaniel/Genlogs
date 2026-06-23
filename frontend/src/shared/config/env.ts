// Single source of truth for environment configuration.
// All config (backend URL, Google Maps key) comes from Vite env vars — never
// hardcoded (conventions §3). Accessing them only here keeps the rest of the
// codebase decoupled from `import.meta.env`.

export interface AppConfig {
  /** Base URL of the FastAPI backend, no trailing slash. */
  apiBaseUrl: string;
  /** Google Maps JavaScript API key (Maps JS + Places + Directions). */
  googleMapsApiKey: string;
}

function readEnv(key: string): string {
  const value = import.meta.env[key];
  return typeof value === 'string' ? value.trim() : '';
}

/** Strip any trailing slashes so callers can safely append `/path`. */
function normalizeBaseUrl(url: string): string {
  return url.replace(/\/+$/, '');
}

export function getConfig(): AppConfig {
  return {
    apiBaseUrl: normalizeBaseUrl(readEnv('VITE_API_BASE_URL')),
    googleMapsApiKey: readEnv('VITE_GOOGLE_MAPS_API_KEY'),
  };
}
