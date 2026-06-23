// Presentational carrier list. Renders loading / error / empty / loaded states
// from the props it is given — no fetching, no business logic here.

import { CarrierItem, type Carrier } from '@/entities/carrier';
import { Spinner } from '@/shared/ui/Spinner';
import type { SearchStatus } from '@/features/search-corridor/model/useSearchCorridor';

export interface CarrierListWidgetProps {
  status: SearchStatus;
  carriers: Carrier[];
  error: string | null;
}

export function CarrierListWidget({ status, carriers, error }: CarrierListWidgetProps) {
  return (
    <section className="flex flex-col gap-3" aria-label="Carriers">
      <h2 className="text-lg font-semibold text-slate-800">Carriers</h2>

      {status === 'idle' && (
        <p className="text-sm text-slate-500">
          Enter an origin and destination, then search to see carriers.
        </p>
      )}

      {status === 'loading' && <Spinner label="Loading carriers…" />}

      {status === 'error' && (
        <p className="text-sm text-red-600" role="alert">
          {error ?? 'Something went wrong.'}
        </p>
      )}

      {status === 'loaded' && carriers.length === 0 && (
        <p className="text-sm text-slate-500">No carriers found for this corridor.</p>
      )}

      {status === 'loaded' && carriers.length > 0 && (
        <ul className="flex flex-col gap-2">
          {carriers.map((carrier) => (
            <CarrierItem key={carrier.name} carrier={carrier} />
          ))}
        </ul>
      )}
    </section>
  );
}
