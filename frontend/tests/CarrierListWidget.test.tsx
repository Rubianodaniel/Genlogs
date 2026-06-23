// Presentational test for CarrierListWidget: renders a given carriers array and
// the various states. No fetching, no Google Maps.

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CarrierListWidget } from '@/widgets/carrier-list';
import type { Carrier } from '@/entities/carrier';

const carriers: Carrier[] = [
  { name: 'Knight-Swift Transport Services', trucks_per_day: 10 },
  { name: 'J.B. Hunt Transport Services Inc', trucks_per_day: 7 },
  { name: 'YRC Worldwide', trucks_per_day: 5 },
];

describe('CarrierListWidget', () => {
  it('renders each carrier name and trucks/day when loaded', () => {
    render(<CarrierListWidget status="loaded" carriers={carriers} error={null} />);

    expect(screen.getByText('Knight-Swift Transport Services')).toBeInTheDocument();
    expect(screen.getByText('J.B. Hunt Transport Services Inc')).toBeInTheDocument();
    expect(screen.getByText('YRC Worldwide')).toBeInTheDocument();
    expect(screen.getByText('10 trucks/day')).toBeInTheDocument();
    expect(screen.getByText('7 trucks/day')).toBeInTheDocument();
    expect(screen.getByText('5 trucks/day')).toBeInTheDocument();
  });

  it('shows a loading indicator while loading', () => {
    render(<CarrierListWidget status="loading" carriers={[]} error={null} />);
    expect(screen.getByText(/loading carriers/i)).toBeInTheDocument();
  });

  it('shows the error message on error', () => {
    render(
      <CarrierListWidget status="error" carriers={[]} error="Could not load carriers." />,
    );
    expect(screen.getByRole('alert')).toHaveTextContent('Could not load carriers.');
  });

  it('shows an empty message when loaded with no carriers', () => {
    render(<CarrierListWidget status="loaded" carriers={[]} error={null} />);
    expect(screen.getByText(/no carriers found/i)).toBeInTheDocument();
  });

  it('shows the idle hint before any search', () => {
    render(<CarrierListWidget status="idle" carriers={[]} error={null} />);
    expect(screen.getByText(/enter an origin and destination/i)).toBeInTheDocument();
  });
});
