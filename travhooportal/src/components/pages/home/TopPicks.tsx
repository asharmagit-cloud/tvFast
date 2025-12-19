'use client';

import { FC, useEffect, useState, useRef } from 'react';
import TopPicksCarousel from '../../ui/carousels/TopPicks';
import { City, State } from '@/types/location';
import {
  fetchStates,
  transformApiStateToState,
  queryCities,
  transformApiCityToCity,
} from '@/utils/api';

export const TopPicks: FC = () => {
  const [states, setStates] = useState<State[]>([]);
  const [cities, setCities] = useState<City[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const hasLoadedRef = useRef(false);

  useEffect(() => {
    // Use ref to prevent duplicate calls
    if (hasLoadedRef.current) {
      return;
    }
    hasLoadedRef.current = true;

    // Fetch both states and cities from API
    const loadData = async () => {
      try {
        setIsLoading(true);

        // Fetch states from API
        const statesResponse = await fetchStates({
          view: 'minimal',
          ids: ['t_all'],
          offset: 0,
          size: 10, // Limit to 10 for homepage carousel
          fetch_all: false,
        });
        const transformedStates = statesResponse.states.map(transformApiStateToState);
        setStates(transformedStates);

        // Fetch cities from API
        let citiesResponse = await queryCities({
          view: 'minimal',
          offset: 0,
          size: 10, // Limit to 10 for homepage carousel
        });
        
        // If minimal view returns empty but total > 0, try full view
        if ((!citiesResponse.cities || citiesResponse.cities.length === 0) && citiesResponse.total > 0) {
          citiesResponse = await queryCities({
            view: 'full',
            offset: 0,
            size: 10,
          });
        }
        
        if (citiesResponse.cities && citiesResponse.cities.length > 0) {
          const transformedCities = citiesResponse.cities.map(transformApiCityToCity);
          setCities(transformedCities);
        } else {
          setCities([]);
        }
      } catch (err) {
        // Fallback to empty arrays on error
        setStates([]);
        setCities([]);
      } finally {
        setIsLoading(false);
      }
    };

    // Load data immediately
    loadData();
  }, []);

  // Don't render carousels if data is still loading and both are empty
  if (isLoading && states.length === 0 && cities.length === 0) {
    return (
      <section className='relative min-h-screen w-full overflow-hidden bg-cover bg-center bg-no-repeat flex items-center justify-center'
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('/images/default.jpg')`,
        }}
      >
        <div className='text-white text-xl'>Loading...</div>
      </section>
    );
  }

  return (
    <>
      {states.length > 0 && (
        <TopPicksCarousel
          id='popular-states'
          title='Explore States'
          backgroundImage='/images/default.jpg'
          data={states}
          type='state'
        />
      )}
      {cities.length > 0 && (
        <TopPicksCarousel
          id='popular-cities'
          title='Explore Cities'
          backgroundImage='/images/default.jpg'
          data={cities}
          type='city'
        />
      )}
    </>
  );
};
