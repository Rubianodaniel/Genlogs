// Renders the computed routes as polylines on the active Google Map.
// The fastest route is highlighted; alternatives are drawn lighter.

import { useEffect } from 'react';
import { useMap } from '@vis.gl/react-google-maps';
import type { RenderableRoute } from '@/widgets/route-map/model/useDirections';

const COLORS = ['#1d4ed8', '#0ea5e9', '#64748b']; // fastest -> slower

export function RoutePolylines({ routes }: { routes: RenderableRoute[] }) {
  const map = useMap();

  useEffect(() => {
    if (!map) {
      return;
    }

    const polylines = routes.map((route, index) => {
      const isFastest = index === 0;
      return new google.maps.Polyline({
        path: route.path,
        map,
        strokeColor: COLORS[index] ?? COLORS[COLORS.length - 1],
        strokeOpacity: isFastest ? 0.95 : 0.6,
        strokeWeight: isFastest ? 6 : 4,
        zIndex: routes.length - index,
      });
    });

    return () => {
      polylines.forEach((polyline) => polyline.setMap(null));
    };
  }, [map, routes]);

  return null;
}
