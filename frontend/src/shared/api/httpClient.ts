// Feature-agnostic HTTP client. The ONLY place that talks to `fetch` and knows
// the backend base URL. Higher layers depend on this thin wrapper, never on
// `fetch` directly (conventions §3: API calls only in api/shared-api segments).

import { getConfig } from '@/shared/config/env';

export class HttpError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'HttpError';
  }
}

/** POST a JSON body to `path` and parse the JSON response as `TResponse`. */
export async function postJson<TResponse, TBody = unknown>(
  path: string,
  body: TBody,
): Promise<TResponse> {
  const { apiBaseUrl } = getConfig();
  const url = `${apiBaseUrl}${path}`;

  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  } catch (cause) {
    // Network-level failure (server down, CORS, offline).
    throw new HttpError(0, 'Network request failed');
  }

  if (!response.ok) {
    throw new HttpError(response.status, `Request failed with status ${response.status}`);
  }

  return (await response.json()) as TResponse;
}
