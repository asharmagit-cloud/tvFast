'use client';

import { useMemo, useState } from 'react';

type City = {
  _id: string;
  id?: string;
  name: string;
  state_id: string;
  is_active: boolean;
  location?: Array<{
    country: { id: string; name?: string };
    region?: { id: string; name?: string };
    state?: { id: string; name?: string };
  }>;
  [key: string]: unknown;
};

type CitiesApiResponse = {
  cities: City[];
  total: number;
  page: number;
  size: number;
  has_next: boolean;
  has_prev: boolean;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, '') ||
  'http://localhost:8000';

const TestApiPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<CitiesApiResponse | null>(null);

  const handleTestApi = async () => {
    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/cities/`, {
        method: 'GET',
        cache: 'no-store',
      });

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      const data: CitiesApiResponse = await res.json();
      setResponse(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unexpected error occurred';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className='mt-15 mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-10'>
      <section className='rounded-2xl border border-gray-200 bg-white p-6 shadow-lg'>
        <header className='mb-4'>
          <p className='text-sm uppercase tracking-wide text-gray-500'>
            Diagnostics
          </p>
          <h1 className='text-3xl font-semibold text-gray-900'>
            Cities API Test
          </h1>
          <p className='mt-2 text-sm text-gray-600'>
            Click the button below to fetch cities from the FastAPI backend&apos;s{' '}
            <code className='rounded bg-gray-100 px-1 py-0.5 text-xs'>
              /api/v1/cities/
            </code>{' '}
            endpoint.
          </p>
        </header>
        <div className='flex flex-col gap-4 sm:flex-row sm:items-center'>
          <button
            onClick={handleTestApi}
            disabled={isLoading}
            className='inline-flex items-center justify-center rounded-full bg-black px-6 py-3 text-sm font-semibold text-white transition enabled:hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-400'
          >
            {isLoading ? 'Loading...' : 'Fetch Cities'}
          </button>
        </div>
      </section>

      <section className='rounded-2xl border border-gray-200 bg-white p-6 shadow-lg'>
        <h2 className='text-xl font-semibold text-gray-900'>Result</h2>

        {!response && !error && (
          <p className='mt-2 text-sm text-gray-500'>
            No data fetched yet. Click the button above to fetch cities from the API.
          </p>
        )}

        {error && (
          <div className='mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700'>
            <p className='font-semibold'>Request failed</p>
            <p>{error}</p>
            <p className='mt-2 text-xs text-red-600'>
              Ensure FastAPI is running and {API_BASE_URL} is reachable from the
              browser.
            </p>
          </div>
        )}

        {response && (
          <div className='mt-4 space-y-4'>
            <div className='rounded-xl border border-green-200 bg-green-50 p-4 text-sm'>
              <p className='font-semibold text-green-700'>
                <i className='fa-solid fa-circle-check text-green-500 mr-2' />
                Successfully fetched cities data
              </p>
              <div className='mt-3 grid grid-cols-2 gap-4 text-xs'>
                <div>
                  <span className='font-semibold text-gray-700'>Total Cities:</span>{' '}
                  <span className='text-gray-800'>{response.total}</span>
                </div>
                <div>
                  <span className='font-semibold text-gray-700'>Page:</span>{' '}
                  <span className='text-gray-800'>{response.page}</span>
                </div>
                <div>
                  <span className='font-semibold text-gray-700'>Page Size:</span>{' '}
                  <span className='text-gray-800'>{response.size}</span>
                </div>
                <div>
                  <span className='font-semibold text-gray-700'>Has More:</span>{' '}
                  <span className='text-gray-800'>
                    {response.has_next ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            </div>

            {response.cities && response.cities.length > 0 && (
              <div>
                <p className='mb-2 font-semibold text-gray-900'>
                  Cities ({response.cities.length} shown):
                </p>
                <div className='max-h-96 space-y-2 overflow-y-auto rounded-lg border border-gray-200 bg-white p-4'>
                  {response.cities.map((city) => (
                    <div
                      key={city._id || city.id}
                      className='rounded-lg border border-gray-100 bg-gray-50 p-3 text-sm'
                    >
                      <div className='flex items-center justify-between'>
                        <div>
                          <p className='font-semibold text-gray-900'>{city.name}</p>
                          <p className='text-xs text-gray-600'>
                            ID: {city._id || city.id}
                          </p>
                          {city.location && city.location.length > 0 && (
                            <p className='mt-1 text-xs text-gray-500'>
                              {city.location[0]?.state?.name ||
                                city.location[0]?.country?.name ||
                                'Location available'}
                            </p>
                          )}
                        </div>
                        <div className='text-right'>
                          <span
                            className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                              city.is_active
                                ? 'bg-green-100 text-green-700'
                                : 'bg-red-100 text-red-700'
                            }`}
                          >
                            {city.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {response.cities && response.cities.length === 0 && (
              <div className='rounded-xl border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-700'>
                <p>No cities found in the response.</p>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
};

export default TestApiPage;





