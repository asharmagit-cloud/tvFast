'use client';

import { FC, useEffect, useRef, useState } from 'react';
import AnimatedBackground from '@/components/ui/AnimatedBackground';
import FlagBounce from '@/components/FlagBounce';
import ListCard from '@/components/ui/ListCard';
import { State } from '@/types/location';
import { fetchStates, transformApiStateToState } from '@/utils/api';
import LoadingScreen from '@/components/ui/LoadingScreen';

const StatesSearchPage: FC = () => {
  const headerRef = useRef<HTMLDivElement>(null);
  const [states, setStates] = useState<State[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStates = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch all states at once
      const response = await fetchStates({
        view: 'minimal',
        ids: ['t_all'],
        offset: 0,
        size: 1000, // Large size to get all states
        fetch_all: true, // Fetch all states without pagination
      });

      const transformedStates = response.states.map(transformApiStateToState);
      setStates(transformedStates);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to load states';
      setError(message);
      console.error('Error fetching states:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadStates();
  }, []);

  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50'>
      <div
        ref={headerRef}
        className='relative bg-gradient-to-br from-slate-800 via-gray-900 to-slate-900 pt-20 overflow-hidden'
      >
        <AnimatedBackground
          containerRef={headerRef as React.RefObject<HTMLElement>}
          particleCount={40}
          colors={[
            '#f85d01',
            '#ffffff',
            '#3b82f6',
            '#8b5cf6',
            '#06b6d4',
            '#10b981',
          ]}
          className='opacity-50'
        />
        <div className='relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20'>
          <div className='text-center'>
            {/* Top decorative line */}
            <div className='flex justify-center mb-6 sm:mb-8'>
              <div className='flex items-center gap-3'>
                <div className='h-px w-12 sm:w-16 bg-gradient-to-r from-transparent to-blue-500'></div>
                <div className='w-2 h-2 rounded-full bg-blue-500 animate-pulse'></div>
                <div className='h-px w-12 sm:w-16 bg-gradient-to-l from-transparent to-blue-500'></div>
              </div>
            </div>

            {/* Title */}
            <h1 className='text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4 sm:mb-6 drop-shadow-2xl font-playfair px-4'>
              Explore States
            </h1>

            {/* Description */}
            <p className='text-base sm:text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed drop-shadow-md mb-6 sm:mb-8 px-4'>
              Discover diverse states and their rich cultural heritage
            </p>
            <FlagBounce />
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className='relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16'>
        {isLoading && states.length === 0 ? (
          <LoadingScreen />
        ) : error ? (
          <div className='rounded-xl border border-red-200 bg-red-50 p-8 text-center'>
            <p className='text-lg font-semibold text-red-700'>Error loading states</p>
            <p className='mt-2 text-sm text-red-600'>{error}</p>
            <button
              onClick={() => loadStates()}
              className='mt-4 rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700'
            >
              Retry
            </button>
          </div>
        ) : states.length === 0 ? (
          <div className='rounded-xl border border-gray-200 bg-gray-50 p-8 text-center'>
            <p className='text-lg font-semibold text-gray-700'>No states found</p>
          </div>
        ) : (
          <>
            <div className='mb-6 text-center'>
              <p className='text-lg font-semibold text-gray-700'>
                Showing {states.length} {states.length === 1 ? 'state' : 'states'}
              </p>
            </div>
            <div className='p-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'>
              {states.map((item, idx) => (
                <ListCard
                  key={`${item.id}-${idx}`}
                  item={item}
                  index={idx}
                  type='state'
                  className='h-[350px] sm:h-[380px] md:h-[420px]'
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default StatesSearchPage;
