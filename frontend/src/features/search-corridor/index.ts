// Public API of the search-corridor feature slice.
export { SearchPanel } from '@/features/search-corridor/ui/SearchPanel';
export {
  useSearchCorridor,
  type UseSearchCorridorResult,
  type Corridor,
  type SearchStatus,
} from '@/features/search-corridor/model/useSearchCorridor';
export {
  carriersApi,
  type CarriersApi,
  type CarriersRequest,
  type CarriersResponse,
} from '@/features/search-corridor/api/carriersApi';
