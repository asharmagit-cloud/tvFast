import { Suspense } from 'react';
import MasonryMarquee from '@/components/ui/MasonryMarquee';

export const Moments: React.FC = () => {
  return (
    <Suspense fallback={null}>
      <section
        id='moments'
        className='flex flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-white to-gray-50 py-16 md:py-20'
      >
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='text-center mb-12 md:mb-16'>
            <h2 className='text-4xl md:text-5xl lg:text-6xl font-bold text-gray-800 mb-4 font-playfair'>
              Discover the Moments
            </h2>
            <p className='text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed'>
              Explore our gallery for stunning travel photos and the best vibes
              from Travhoo!
            </p>
          </div>
        </div>
        <MasonryMarquee className='w-full' />
      </section>
    </Suspense>
  );
};
