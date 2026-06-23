// City text input wired to Google Maps Places autocomplete.
// Presentational + thin Maps glue only; no business logic. The selected/typed
// value is lifted up to the search hook via `onChange`.

import { useEffect, useRef } from 'react';
import { useMapsLibrary } from '@vis.gl/react-google-maps';

export interface CityInputProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function CityInput({ id, label, value, onChange, placeholder }: CityInputProps) {
  const places = useMapsLibrary('places');
  const inputRef = useRef<HTMLInputElement>(null);
  // Keep latest onChange without re-binding the Maps listener on every render.
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    if (!places || !inputRef.current) {
      return;
    }

    const autocomplete = new places.Autocomplete(inputRef.current, {
      types: ['(cities)'],
      fields: ['name', 'formatted_address'],
    });

    const listener = autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      const selected = place.name ?? place.formatted_address ?? '';
      if (selected) {
        onChangeRef.current(selected);
      }
    });

    return () => {
      listener.remove();
    };
  }, [places]);

  return (
    <label htmlFor={id} className="flex flex-1 flex-col gap-1">
      <span className="text-sm font-medium text-slate-600">{label}</span>
      <input
        id={id}
        ref={inputRef}
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-md border border-slate-300 px-3 py-2 text-slate-800 focus:border-slate-500 focus:outline-none"
      />
    </label>
  );
}
