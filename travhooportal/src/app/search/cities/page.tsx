'use client';

import { FC, useEffect, useRef, useState, useCallback } from 'react';
import AnimatedBackground from '@/components/ui/AnimatedBackground';
import FlagBounce from '@/components/FlagBounce';
import ListCard from '@/components/ui/ListCard';
import { City, State } from '@/types/location';
import {
  queryCities,
  transformApiCityToCity,
  fetchStates,
  transformApiStateToState,
  fetchLabels,
  Label,
} from '@/utils/api';
import LoadingScreen from '@/components/ui/LoadingScreen';

const CitiesSearchPage: FC = () => {
  const headerRef = useRef<HTMLDivElement>(null);
  const [cities, setCities] = useState<City[]>([]);
  const [states, setStates] = useState<State[]>([]);
  const [labels, setLabels] = useState<Label[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize] = useState(20);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStateId, setSelectedStateId] = useState<string>('');
  const [selectedLabelIds, setSelectedLabelIds] = useState<string[]>([]);
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setCurrentPage(1); // Reset to first page on new search
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Load states and labels for filter dropdowns
  useEffect(() => {
    const loadFilters = async () => {
      try {
        // Load states
        const statesResponse = await fetchStates({
          view: 'minimal',
          ids: ['t_all'],
          offset: 0,
          size: 1000,
          fetch_all: true,
        });
        const transformedStates = statesResponse.states.map(transformApiStateToState);
        setStates(transformedStates);

        // Load labels
        const labelsResponse = await fetchLabels();
        setLabels(labelsResponse.labels);
      } catch (err) {
        console.error('Error loading filters:', err);
      }
    };

    loadFilters();
  }, []);

  // Load cities
  const loadCities = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const offset = (currentPage - 1) * pageSize;

      const response = await queryCities({
        offset,
        size: pageSize,
        search: debouncedSearch || undefined,
        state_id: selectedStateId || undefined,
        labels: selectedLabelIds.length > 0 ? selectedLabelIds : undefined,
        label_filter_type: 'any',
        view: 'full',
      });

      const transformedCities = response.cities.map(transformApiCityToCity);
      setCities(transformedCities);
      setTotal(response.total);
      setHasNext(response.has_next);
      setHasPrev(response.has_prev);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to load cities';
      setError(message);
      console.error('Error fetching cities:', err);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, pageSize, debouncedSearch, selectedStateId, selectedLabelIds]);

  useEffect(() => {
    loadCities();
  }, [loadCities]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFilterChange = () => {
    setCurrentPage(1); // Reset to first page when filters change
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedStateId('');
    setSelectedLabelIds([]);
    setCurrentPage(1);
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className='min-h-screen bg-gradient-to-br from-orange-50 via-white to-purple-50'>
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
                <div className='h-px w-12 sm:w-16 bg-gradient-to-r from-transparent to-orange-500'></div>
                <div className='w-2 h-2 rounded-full bg-orange-500 animate-pulse'></div>
                <div className='h-px w-12 sm:w-16 bg-gradient-to-l from-transparent to-orange-500'></div>
              </div>
            </div>

            {/* Title */}
            <h1 className='text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4 sm:mb-6 drop-shadow-2xl font-playfair px-4'>
              Explore Cities
            </h1>

            {/* Description */}
            <p className='text-base sm:text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed drop-shadow-md mb-6 sm:mb-8 px-4'>
              Discover vibrant cities and their unique cultures across the world
            </p>
            <FlagBounce />
          </div>
        </div>
      </div>

      {/* Search and Filters Section */}
      <div className='relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 mb-8'>
        <div className='bg-white rounded-xl shadow-lg p-6 border border-gray-200'>
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
            {/* Search Input */}
            <div>
              <label
                htmlFor='search'
                className='block text-sm font-medium text-gray-700 mb-2'
              >
                Search Cities
              </label>
              <input
                id='search'
                type='text'
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  handleFilterChange();
                }}
                placeholder='Search by city name or state...'
                className='w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none'
              />
            </div>

            {/* State Filter */}
            <div>
              <label
                htmlFor='state'
                className='block text-sm font-medium text-gray-700 mb-2'
              >
                Filter by State
              </label>
              <select
                id='state'
                value={selectedStateId}
                onChange={(e) => {
                  setSelectedStateId(e.target.value);
                  handleFilterChange();
                }}
                className='w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none bg-white'
              >
                <option value=''>All States</option>
                {states.map((state) => (
                  <option key={state.id} value={state.id}>
                    {state.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Labels Filter */}
            <div>
              <label
                htmlFor='labels'
                className='block text-sm font-medium text-gray-700 mb-2'
              >
                Filter by Labels
              </label>
              <select
                id='labels'
                multiple
                value={selectedLabelIds}
                onChange={(e) => {
                  const selected = Array.from(e.target.selectedOptions, option => option.value);
                  setSelectedLabelIds(selected);
                  handleFilterChange();
                }}
                className='w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none bg-white min-h-[42px]'
                size={3}
              >
                {labels.map((label) => (
                  <option key={label.id} value={label.id}>
                    {label.name}
                  </option>
                ))}
              </select>
              {selectedLabelIds.length > 0 && (
                <p className='mt-1 text-xs text-gray-500'>
                  {selectedLabelIds.length} label(s) selected
                </p>
              )}
            </div>
          </div>

          {/* Clear Filters Button */}
          {(searchQuery || selectedStateId || selectedLabelIds.length > 0) && (
            <div className='mt-4 flex justify-end'>
              <button
                onClick={clearFilters}
                className='px-4 py-2 text-sm font-medium text-orange-600 hover:text-orange-700 hover:underline'
              >
                Clear Filters
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Content Section */}
      <div className='relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16'>
        {isLoading && cities.length === 0 ? (
          <LoadingScreen />
        ) : error ? (
          <div className='rounded-xl border border-red-200 bg-red-50 p-8 text-center'>
            <p className='text-lg font-semibold text-red-700'>
              Error loading cities
            </p>
            <p className='mt-2 text-sm text-red-600'>{error}</p>
            <button
              onClick={() => loadCities()}
              className='mt-4 rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700'
            >
              Retry
            </button>
          </div>
        ) : cities.length === 0 ? (
          <div className='rounded-xl border border-gray-200 bg-gray-50 p-8 text-center'>
            <p className='text-lg font-semibold text-gray-700'>
              No cities found
            </p>
            <p className='mt-2 text-sm text-gray-600'>
              Try adjusting your search or filters
            </p>
          </div>
        ) : (
          <>
            {/* Results Count */}
            <div className='mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4'>
              <p className='text-lg font-semibold text-gray-700'>
                Showing {cities.length} of {total} cities
                {debouncedSearch && (
                  <span className='text-sm font-normal text-gray-500 ml-2'>
                    for &quot;{debouncedSearch}&quot;
                  </span>
                )}
              </p>
            </div>

            {/* Cities Grid */}
            <div className='p-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'>
              {cities.map((item, idx) => (
                <ListCard
                  key={`${item.id}-${idx}`}
                  item={item}
                  index={idx}
                  className='h-[350px] sm:h-[380px] md:h-[420px]'
                  type='city'
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className='mt-8 flex flex-col sm:flex-row justify-center items-center gap-4'>
                <div className='flex items-center gap-2'>
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={!hasPrev || isLoading}
                    className='px-4 py-2 rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
                  >
                    Previous
                  </button>

                  <div className='flex items-center gap-1'>
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum: number;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }

                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          disabled={isLoading}
                          className={`px-4 py-2 rounded-lg border transition-colors ${
                            currentPage === pageNum
                              ? 'bg-orange-600 text-white border-orange-600'
                              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                          } disabled:opacity-50 disabled:cursor-not-allowed`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                  </div>

                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={!hasNext || isLoading}
                    className='px-4 py-2 rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
                  >
                    Next
                  </button>
                </div>

                <p className='text-sm text-gray-600'>
                  Page {currentPage} of {totalPages}
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default CitiesSearchPage;
