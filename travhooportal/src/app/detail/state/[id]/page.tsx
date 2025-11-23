'use client';

import { FC, useEffect, useState } from 'react';
import GreetingScreen from '@/components/ui/GreetingScreen';
import { useParams } from 'next/navigation';
import LoadingScreen from '@/components/ui/LoadingScreen';
import { State } from '@/types/location';
import Image from 'next/image';
import DpTabs from '@/components/ui/DpTabs';
import Overview from '@/components/pages/detail/Overview';
import History from '@/components/pages/detail/History';
import TravelTips from '@/components/pages/detail/TravelTips';
import SafetyEmergency from '@/components/pages/detail/SafetyEmergency';
import Experiences from '@/components/pages/detail/Experiences';
import {
  fetchStateById,
  transformApiStateToState,
} from '@/utils/api';

const StateDetailPage: FC = () => {
  const { id: stateId } = useParams();
  const [stateDetails, setStateDetails] = useState<State | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadState = async () => {
      if (!stateId || typeof stateId !== 'string') {
        setError('Invalid state ID');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const apiState = await fetchStateById(stateId);
        console.log('API State experiences:', apiState.experiences);
        const transformedState = transformApiStateToState(apiState);
        console.log('Transformed State experiences:', transformedState.experiences);
        setStateDetails(transformedState);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to load state details';
        // Provide user-friendly error messages
        let userMessage = message;
        if (message.includes('Invalid state ID') || message.includes('Invalid state ID format')) {
          userMessage = 'Invalid state ID. The state you are looking for does not exist.';
        } else if (message.includes('not found')) {
          userMessage = 'State not found. The state you are looking for does not exist.';
        }
        setError(userMessage);
        console.error('Error fetching state:', err);
      } finally {
        setLoading(false);
      }
    };

    loadState();
  }, [stateId]);

  if (loading) {
    return <LoadingScreen />;
  }

  if (error || !stateDetails) {
    return (
      <div className='min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 via-white to-red-50'>
        <div className='text-center px-4 max-w-md'>
          <div className='mb-6'>
            <i className='fa-solid fa-exclamation-triangle text-6xl text-orange-500 mb-4' />
          </div>
          <h1 className='text-3xl font-bold text-gray-900 mb-4'>
            {error ? 'Error Loading State' : 'State Not Found'}
          </h1>
          <p className='text-gray-600 mb-6'>
            {error || 'The state you are looking for does not exist.'}
          </p>
          <div className='flex flex-col sm:flex-row gap-3 justify-center'>
            <button
              onClick={() => window.history.back()}
              className='px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors'
            >
              Go Back
            </button>
            <button
              onClick={() => window.location.href = '/search/states'}
              className='px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors'
            >
              Browse States
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { greetingText = '' } = stateDetails ?? {};

  return (
    <>
      <GreetingScreen greetingText={greetingText} animationType='fadeInUp' />
      <div className='min-h-screen relative'>
        <Image
          src={stateDetails?.images?.banner || '/images/default.jpg'}
          alt={stateDetails?.name || 'State banner image'}
          fill
          className='object-cover'
        />
        <div className='absolute inset-0 flex items-center justify-center'>
          <div className='flex flex-col items-center justify-center gap-3 sm:gap-4 text-center px-4 sm:px-6 max-w-5xl'>
            <h1 className='text-4xl sm:text-6xl md:text-7xl lg:text-8xl xl:text-9xl line-height-normal font-bold text-white drop-shadow-2xl font-playfair tracking-wide'>
              {stateDetails.name}
            </h1>

            {stateDetails.tagline && (
              <p className='text-base sm:text-xl md:text-2xl lg:text-3xl text-white/95 drop-shadow-lg font-inter font-semibold tracking-wide max-w-3xl px-2'>
                {stateDetails.tagline}
              </p>
            )}

            {stateDetails.locations?.length &&
              stateDetails.locations?.length > 0 && (
                <div className='flex flex-wrap justify-center items-center gap-2 text-sm sm:text-base md:text-lg text-white/90 drop-shadow-md'>
                  {stateDetails.locations?.map(({ region }) => {
                    return (
                      <div key={region?.id} className='flex items-center gap-1'>
                        {region?.name && <span>{region?.name}</span>}
                      </div>
                    );
                  })}
                </div>
              )}
          </div>
        </div>

        <div className='absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-black/20' />

        <div className='absolute bottom-20 left-1/2 transform -translate-x-1/2 animate-bounce'>
          <i className='fa-solid fa-angles-down text-white/50 text-xl' />
        </div>
      </div>

      {/* Overview and History Section */}
      <div className='w-full bg-gradient-to-br from-orange-50 via-white to-red-50 py-16 px-4'>
        <div className='max-w-7xl mx-auto'>
          <DpTabs
            tabs={[
              {
                key: 'overview',
                name: 'Overview',
                component: () => (
                  <Overview
                    description={stateDetails.description || {}}
                    labels={stateDetails.labels || []}
                  />
                ),
              },
              ...(stateDetails.description?.history
                ? [
                    {
                      key: 'history',
                      name: 'History',
                      component: () => (
                        <History
                          history={stateDetails.description?.history || ''}
                        />
                      ),
                    },
                  ]
                : []),
            ]}
            defaultTab='overview'
            tabsClassNames={{
              container: 'flex flex-row justify-center mb-8',
              tabs: 'w-auto p-2 shadow-md rounded-full flex gap-2 bg-white',
              defaultChildren:
                'px-6 py-3 text-md text-gray-700 hover:bg-gray-50 rounded-full transition-all duration-300 font-medium',
              activeChildren:
                'text-white font-semibold bg-gradient-to-r from-orange-500 to-red-500 shadow-md',
            }}
          />
        </div>
      </div>

      {/* Experiences Section */}
      {stateDetails.experiences && (
        <Experiences experiences={stateDetails.experiences} />
      )}

      {/* Travel Tips Section */}
      {stateDetails.travelTips && stateDetails.travelTips.length > 0 && (
        <TravelTips tips={stateDetails.travelTips} />
      )}

      {/* Safety & Emergency Section */}
      <SafetyEmergency
        emergencyContacts={stateDetails.emergencyContacts}
        safetyInformation={stateDetails.safetyInformation}
      />
    </>
  );
};

export default StateDetailPage;
