// App root. Provides the Google Maps JS API context (key from env) to the whole
// tree and renders the portal page. A missing key is surfaced clearly instead
// of silently breaking the map.

import { APIProvider } from '@vis.gl/react-google-maps';
import { getConfig } from '@/shared/config/env';
import { PortalPage } from '@/pages/portal';

export function App() {
  const { googleMapsApiKey } = getConfig();

  if (!googleMapsApiKey) {
    return (
      <div className="mx-auto max-w-xl p-6 text-slate-700">
        <h1 className="text-xl font-bold">Configuration required</h1>
        <p className="mt-2">
          Missing <code>VITE_GOOGLE_MAPS_API_KEY</code>. Copy{' '}
          <code>.env.example</code> to <code>.env</code> and set your Google Maps API key.
        </p>
      </div>
    );
  }

  return (
    <APIProvider apiKey={googleMapsApiKey} libraries={['places', 'routes']}>
      <PortalPage />
    </APIProvider>
  );
}
