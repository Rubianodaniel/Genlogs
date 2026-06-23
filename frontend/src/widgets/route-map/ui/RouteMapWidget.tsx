// Embedded Google Map showing up to the 3 fastest driving routes for a
// corridor. Composition only; route computation lives in useDirections.

import { Map } from '@vis.gl/react-google-maps';
import type { Corridor } from '@/features/search-corridor/model/useSearchCorridor';
import { useDirections } from '@/widgets/route-map/model/useDirections';
import { RoutePolylines } from '@/widgets/route-map/ui/RoutePolylines';

// Continental-US default view before a search is run.
const DEFAULT_CENTER = { lat: 39.5, lng: -98.35 };
const DEFAULT_ZOOM = 4;

export function RouteMapWidget({ corridor }: { corridor: Corridor | null }) {
  const { routes, status } = useDirections(corridor);

  return (
    <div className="flex flex-col gap-2">
      <div className="h-[420px] w-full overflow-hidden rounded-lg border border-slate-200">
        <Map
          defaultCenter={DEFAULT_CENTER}
          defaultZoom={DEFAULT_ZOOM}
          gestureHandling="greedy"
          disableDefaultUI={false}
          mapId="genlogs-portal-map"
        >
          <RoutePolylines routes={routes} />
        </Map>
      </div>

      {status === 'error' && (
        <p className="text-sm text-red-600">Could not compute routes for this corridor.</p>
      )}
      {status === 'ok' && routes.length > 0 && (
        <ul className="flex flex-wrap gap-3 text-sm text-slate-600">
          {routes.map((route, index) => (
            <li key={index} className="flex items-center gap-2">
              <span
                className="inline-block h-2 w-6 rounded-full"
                style={{ backgroundColor: ['#1d4ed8', '#0ea5e9', '#64748b'][index] }}
              />
              {index === 0 ? 'Fastest' : `Alt ${index}`}
              {route.durationText ? ` — ${route.durationText}` : ''}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
