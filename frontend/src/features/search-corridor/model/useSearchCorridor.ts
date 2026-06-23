// Business logic for the search-corridor feature. Lives in model/ (a hook),
// NOT in components (conventions §3). Holds the From/To state, orchestrates the
// carriers request, and exposes an explicit state machine the UI just renders.
//
// The carriers API is injected (default = real impl) so the hook is unit
// testable with a mock (Dependency Inversion).

import { useCallback, useState } from 'react';
import type { Carrier } from '@/entities/carrier';
import {
  carriersApi as defaultCarriersApi,
  type CarriersApi,
} from '@/features/search-corridor/api/carriersApi';

export type SearchStatus = 'idle' | 'loading' | 'loaded' | 'error';

/** A confirmed corridor the map widget can draw routes for. */
export interface Corridor {
  fromCity: string;
  toCity: string;
}

export interface UseSearchCorridorResult {
  fromCity: string;
  toCity: string;
  setFromCity: (value: string) => void;
  setToCity: (value: string) => void;
  status: SearchStatus;
  carriers: Carrier[];
  error: string | null;
  /** The submitted corridor (set on a successful submit); null until searched. */
  corridor: Corridor | null;
  /** Whether the form currently has both cities filled. */
  canSearch: boolean;
  search: () => Promise<void>;
}

export interface UseSearchCorridorOptions {
  api?: CarriersApi;
}

export function useSearchCorridor(
  options: UseSearchCorridorOptions = {},
): UseSearchCorridorResult {
  const api = options.api ?? defaultCarriersApi;

  const [fromCity, setFromCity] = useState('');
  const [toCity, setToCity] = useState('');
  const [status, setStatus] = useState<SearchStatus>('idle');
  const [carriers, setCarriers] = useState<Carrier[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [corridor, setCorridor] = useState<Corridor | null>(null);

  const canSearch = fromCity.trim().length > 0 && toCity.trim().length > 0;

  const search = useCallback(async () => {
    const from = fromCity.trim();
    const to = toCity.trim();
    if (from.length === 0 || to.length === 0) {
      return;
    }

    setStatus('loading');
    setError(null);
    // Publish the corridor immediately so the map can start drawing routes
    // (Google Directions) in parallel with the backend carriers call.
    setCorridor({ fromCity: from, toCity: to });

    try {
      const response = await api.getCarriers({ from_city: from, to_city: to });
      setCarriers(response.carriers);
      setStatus('loaded');
    } catch {
      setCarriers([]);
      setError('Could not load carriers. Please try again.');
      setStatus('error');
    }
  }, [api, fromCity, toCity]);

  return {
    fromCity,
    toCity,
    setFromCity,
    setToCity,
    status,
    carriers,
    error,
    corridor,
    canSearch,
    search,
  };
}
