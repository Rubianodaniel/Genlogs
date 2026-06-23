// The From/To inputs + Search button. Presentational composition of the
// search-corridor feature; all state/logic comes from the injected hook result.

import { CityInput } from '@/features/search-corridor/ui/CityInput';
import type { UseSearchCorridorResult } from '@/features/search-corridor/model/useSearchCorridor';

export function SearchPanel({ search: searchModel }: { search: UseSearchCorridorResult }) {
  const { fromCity, toCity, setFromCity, setToCity, canSearch, status, search } = searchModel;

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    void search();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-4 sm:flex-row sm:items-end"
    >
      <CityInput
        id="from-city"
        label="From (city)"
        value={fromCity}
        onChange={setFromCity}
        placeholder="e.g. New York City"
      />
      <CityInput
        id="to-city"
        label="To (city)"
        value={toCity}
        onChange={setToCity}
        placeholder="e.g. Washington DC"
      />
      <button
        type="submit"
        disabled={!canSearch || status === 'loading'}
        className="rounded-md bg-slate-800 px-5 py-2 font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {status === 'loading' ? 'Searching…' : 'Search'}
      </button>
    </form>
  );
}
