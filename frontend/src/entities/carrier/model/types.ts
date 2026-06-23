// Business entity: a carrier moving trucks on a corridor.
// Mirrors the backend `CarrierOut` DTO (spec 001 / 003).

export interface Carrier {
  name: string;
  trucks_per_day: number;
}
