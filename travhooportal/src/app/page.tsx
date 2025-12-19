'use client';

import dynamic from 'next/dynamic';
import SectionNavigation from '@/components/SectionNavigation';
import { HOMEPAGE_SECTIONS } from '@/constants';
import LazyLoad from '@/components/LazyLoad';

// Dynamically import components that use Swiper (which accesses localStorage)
// with ssr: false to prevent server-side rendering
const HeroSlides = dynamic(
  () => import('@/components/pages/home/HeroSlides'),
  { ssr: false }
);

const PopularDestinations = dynamic(
  () => import('@/components/pages/home/Destinations'),
  { ssr: false }
);

const TopPicks = dynamic(
  () => import('@/components/pages/home/TopPicks').then(mod => {
    console.log('TopPicks: Dynamic import loaded', mod);
    return { default: mod.TopPicks };
  }),
  { 
    ssr: false,
    loading: () => <div className='min-h-screen flex items-center justify-center'>Loading TopPicks...</div>
  }
);

const Moments = dynamic(
  () => import('@/components/pages/home/Moments').then(mod => ({ default: mod.Moments })),
  { ssr: false }
);

const Home = () => {
  return (
    <div className='w-full'>
      <SectionNavigation sections={HOMEPAGE_SECTIONS} />
      {/* Hero slides - load immediately (above the fold) */}
      <HeroSlides />
      {/* Popular Destinations - lazy load when approaching viewport */}
      <LazyLoad rootMargin='200px'>
        <PopularDestinations />
      </LazyLoad>
      {/* TopPicks - Load immediately as it's important content */}
      <TopPicks />
      {/* Moments - lazy load when approaching viewport */}
      <LazyLoad rootMargin='200px'>
        <Moments />
      </LazyLoad>
    </div>
  );
};

export default Home;
