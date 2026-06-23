// The single portal page. Composition root for the feature + widgets: owns the
// search hook instance and wires its state into the panel, map and list.

import { SearchPanel, useSearchCorridor } from '@/features/search-corridor';
import { RouteMapWidget } from '@/widgets/route-map';
import { CarrierListWidget } from '@/widgets/carrier-list';

export function PortalPage() {
  const searchModel = useSearchCorridor();

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-6 p-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Genlogs Corridor Portal</h1>
        <p className="text-slate-500">
          Find the carriers and the 3 fastest routes between two cities.
        </p>
      </header>

      <SearchPanel search={searchModel} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[2fr_1fr]">
        <RouteMapWidget corridor={searchModel.corridor} />
        <CarrierListWidget
          status={searchModel.status}
          carriers={searchModel.carriers}
          error={searchModel.error}
        />
      </div>
    </main>
  );
}
