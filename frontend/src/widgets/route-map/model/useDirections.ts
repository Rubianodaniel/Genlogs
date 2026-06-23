// Computes up to 3 alternative driving routes for a corridor via the Google
// Directions API. Encapsulated in a hook (logic out of the component).
//
// Strategy: request `provideRouteAlternatives: true`, then keep the 3 routes
// with the shortest total duration ("3 fastest"). The actual polyline rendering
// is done declaratively by the widget from the returned encoded paths.

import { useEffect, useState } from 'react';
import { useMap, useMapsLibrary } from '@vis.gl/react-google-maps';
import type { Corridor } from '@/features/search-corridor/model/useSearchCorridor';

const MAX_ROUTES = 3;

export interface RenderableRoute {
  /** Decoded path for a polyline. */
  path: google.maps.LatLng[];
  /** Total duration in seconds (used for ordering / labelling). */
  durationSeconds: number;
  durationText: string;
}

export interface UseDirectionsResult {
  routes: RenderableRoute[];
  status: 'idle' | 'loading' | 'ok' | 'error';
}

function totalDurationSeconds(route: google.maps.DirectionsRoute): number {
  return route.legs.reduce((sum, leg) => sum + (leg.duration?.value ?? 0), 0);
}

export function useDirections(corridor: Corridor | null): UseDirectionsResult {
  const map = useMap();
  const routesLib = useMapsLibrary('routes');
  const [routes, setRoutes] = useState<RenderableRoute[]>([]);
  const [status, setStatus] = useState<UseDirectionsResult['status']>('idle');

  useEffect(() => {
    if (!routesLib || !corridor) {
      return;
    }

    let cancelled = false;
    setStatus('loading');
    const service = new routesLib.DirectionsService();

    service
      .route({
        origin: corridor.fromCity,
        destination: corridor.toCity,
        travelMode: google.maps.TravelMode.DRIVING,
        provideRouteAlternatives: true,
      })
      .then((result) => {
        if (cancelled) return;

        const fastest = [...result.routes]
          .sort((a, b) => totalDurationSeconds(a) - totalDurationSeconds(b))
          .slice(0, MAX_ROUTES)
          .map<RenderableRoute>((route) => ({
            path: route.overview_path,
            durationSeconds: totalDurationSeconds(route),
            durationText: route.legs[0]?.duration?.text ?? '',
          }));

        setRoutes(fastest);
        setStatus('ok');

        // Fit the map to the first (fastest) route's bounds.
        const bounds = result.routes[0]?.bounds;
        if (map && bounds) {
          map.fitBounds(bounds);
        }
      })
      .catch(() => {
        if (cancelled) return;
        setRoutes([]);
        setStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, [routesLib, map, corridor]);

  return { routes, status };
}
