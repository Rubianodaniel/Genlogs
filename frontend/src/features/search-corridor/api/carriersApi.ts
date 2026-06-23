// Backend contract for the carriers endpoint.
// The ONLY module that knows the shape of POST /carriers (spec 001 / 003).

import { postJson } from '@/shared/api/httpClient';
import type { Carrier } from '@/entities/carrier';

/** Request body for POST /carriers. */
export interface CarriersRequest {
  from_city: string;
  to_city: string;
}

/** Response body from POST /carriers. */
export interface CarriersResponse {
  from_city: string;
  to_city: string;
  carriers: Carrier[];
}

/**
 * The carriers API as an injectable interface so the search hook can be unit
 * tested with a mock (Dependency Inversion — conventions §0).
 */
export interface CarriersApi {
  getCarriers(request: CarriersRequest): Promise<CarriersResponse>;
}

export const carriersApi: CarriersApi = {
  getCarriers(request: CarriersRequest): Promise<CarriersResponse> {
    return postJson<CarriersResponse, CarriersRequest>('/carriers', request);
  },
};
