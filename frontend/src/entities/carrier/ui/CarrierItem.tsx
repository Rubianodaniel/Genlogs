// Presentational render of a single carrier. No business logic.

import type { Carrier } from '@/entities/carrier/model/types';

export function CarrierItem({ carrier }: { carrier: Carrier }) {
  return (
    <li className="flex items-center justify-between rounded-md border border-slate-200 bg-white px-4 py-3">
      <span className="font-medium text-slate-800">{carrier.name}</span>
      <span className="text-sm text-slate-500">
        {carrier.trucks_per_day} trucks/day
      </span>
    </li>
  );
}
