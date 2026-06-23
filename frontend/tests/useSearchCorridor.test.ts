// Unit test for the search hook with the carriers API MOCKED (dependency
// injection). Verifies the state machine: idle -> loading -> loaded, the
// corridor publication, and error handling.

import { describe, it, expect, vi } from 'vitest';
import { act, renderHook, waitFor } from '@testing-library/react';
import {
  useSearchCorridor,
  type Corridor,
} from '@/features/search-corridor/model/useSearchCorridor';
import type {
  CarriersApi,
  CarriersResponse,
} from '@/features/search-corridor/api/carriersApi';

function makeApi(impl: CarriersApi['getCarriers']): CarriersApi {
  return { getCarriers: vi.fn(impl) };
}

describe('useSearchCorridor', () => {
  it('starts in idle with empty fields and cannot search', () => {
    const api = makeApi(async () => ({ from_city: '', to_city: '', carriers: [] }));
    const { result } = renderHook(() => useSearchCorridor({ api }));

    expect(result.current.status).toBe('idle');
    expect(result.current.carriers).toEqual([]);
    expect(result.current.corridor).toBeNull();
    expect(result.current.canSearch).toBe(false);
  });

  it('transitions idle -> loading -> loaded and stores carriers + corridor', async () => {
    const response: CarriersResponse = {
      from_city: 'New York City',
      to_city: 'Washington DC',
      carriers: [{ name: 'UPS Inc.', trucks_per_day: 11 }],
    };

    let resolve!: (value: CarriersResponse) => void;
    const pending = new Promise<CarriersResponse>((r) => {
      resolve = r;
    });
    const api = makeApi(() => pending);

    const { result } = renderHook(() => useSearchCorridor({ api }));

    act(() => {
      result.current.setFromCity('New York City');
      result.current.setToCity('Washington DC');
    });
    expect(result.current.canSearch).toBe(true);

    let searchPromise: Promise<void>;
    act(() => {
      searchPromise = result.current.search();
    });

    // Loading + corridor published immediately (so the map can draw routes).
    expect(result.current.status).toBe('loading');
    expect(result.current.corridor).toEqual<Corridor>({
      fromCity: 'New York City',
      toCity: 'Washington DC',
    });

    await act(async () => {
      resolve(response);
      await searchPromise;
    });

    expect(result.current.status).toBe('loaded');
    expect(result.current.carriers).toEqual(response.carriers);
    expect(api.getCarriers).toHaveBeenCalledWith({
      from_city: 'New York City',
      to_city: 'Washington DC',
    });
  });

  it('sets error status and clears carriers when the api rejects', async () => {
    const api = makeApi(async () => {
      throw new Error('boom');
    });
    const { result } = renderHook(() => useSearchCorridor({ api }));

    act(() => {
      result.current.setFromCity('A');
      result.current.setToCity('B');
    });

    await act(async () => {
      await result.current.search();
    });

    await waitFor(() => expect(result.current.status).toBe('error'));
    expect(result.current.carriers).toEqual([]);
    expect(result.current.error).toBeTruthy();
  });

  it('does not call the api when a city is blank', async () => {
    const api = makeApi(async () => ({ from_city: '', to_city: '', carriers: [] }));
    const { result } = renderHook(() => useSearchCorridor({ api }));

    act(() => {
      result.current.setFromCity('   ');
      result.current.setToCity('B');
    });

    await act(async () => {
      await result.current.search();
    });

    expect(api.getCarriers).not.toHaveBeenCalled();
    expect(result.current.status).toBe('idle');
  });
});
