// Unit test for carriersApi: mocks global fetch and asserts it POSTs the correct
// body to /carriers and parses the JSON response. No real network.

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { carriersApi } from '@/features/search-corridor/api/carriersApi';
import { HttpError } from '@/shared/api/httpClient';

const BASE_URL = 'http://localhost:8000';

beforeEach(() => {
  vi.stubEnv('VITE_API_BASE_URL', BASE_URL);
});

describe('carriersApi.getCarriers', () => {
  it('POSTs from_city/to_city as JSON and parses the response', async () => {
    const responseBody = {
      from_city: 'New York City',
      to_city: 'Washington DC',
      carriers: [
        { name: 'Knight-Swift Transport Services', trucks_per_day: 10 },
        { name: 'J.B. Hunt Transport Services Inc', trucks_per_day: 7 },
      ],
    };

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => responseBody,
    });
    vi.stubGlobal('fetch', fetchMock);

    const result = await carriersApi.getCarriers({
      from_city: 'New York City',
      to_city: 'Washington DC',
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [calledUrl, calledInit] = fetchMock.mock.calls[0];
    expect(calledUrl).toBe(`${BASE_URL}/carriers`);
    expect(calledInit.method).toBe('POST');
    expect(calledInit.headers).toMatchObject({ 'Content-Type': 'application/json' });
    expect(JSON.parse(calledInit.body)).toEqual({
      from_city: 'New York City',
      to_city: 'Washington DC',
    });
    expect(result).toEqual(responseBody);
  });

  it('throws HttpError on a non-2xx response', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 422, json: async () => ({}) }),
    );

    await expect(
      carriersApi.getCarriers({ from_city: 'a', to_city: 'b' }),
    ).rejects.toBeInstanceOf(HttpError);
  });

  it('throws HttpError(0) when the network request fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    await expect(
      carriersApi.getCarriers({ from_city: 'a', to_city: 'b' }),
    ).rejects.toMatchObject({ status: 0 });
  });
});
