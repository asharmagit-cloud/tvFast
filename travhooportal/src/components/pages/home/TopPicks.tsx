'use client';

import { FC, useEffect, useState } from 'react';
import TopPicksCarousel from '../../ui/carousels/TopPicks';
import citiesData from '../../../data/cities.json';
import { City, State } from '@/types/location';
import { fetchStates, transformApiStateToState } from '@/utils/api';

export const TopPicks: FC = () => {
  const [states, setStates] = useState<State[]>([]);
  const [cities, setCities] = useState<City[]>([]);
  const [isLoadingStates, setIsLoadingStates] = useState(true);

  useEffect(() => {
    // Fetch states from API
    const loadStates = async () => {
      try {
        setIsLoadingStates(true);
        const response = await fetchStates({
          view: 'minimal',
          ids: ['t_all'],
          offset: 0,
          size: 10, // Limit to 10 for homepage carousel
          fetch_all: false,
        });
        const transformedStates = response.states.map(transformApiStateToState);
        setStates(transformedStates);
      } catch (err) {
        console.error('Error fetching states:', err);
        // Fallback to empty array on error
        setStates([]);
      } finally {
        setIsLoadingStates(false);
      }
    };

    loadStates();
    // Keep cities from static data for now
    setCities(citiesData.cities);
  }, []);

  return (
    <>
      <TopPicksCarousel
        id='popular-states'
        title='Explore States'
        backgroundImage='/images/default.jpg'
        data={states}
        type='state'
      />
      <TopPicksCarousel
        id='popular-cities'
        title='Explore Cities'
        backgroundImage='/images/default.jpg'
        data={cities}
        type='city'
      />
    </>
  );
};
