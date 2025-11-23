import SectionNavigation from '@/components/SectionNavigation';
import { HOMEPAGE_SECTIONS } from '@/constants';
import { Moments } from '@/components/pages/home/Moments';
import HeroSlides from '@/components/pages/home/HeroSlides';
import PopularDestinations from '@/components/pages/home/Destinations';
import { TopPicks } from '@/components/pages/home/TopPicks';

const Home = () => {
  return (
    <div className='w-full'>
      <SectionNavigation sections={HOMEPAGE_SECTIONS} />
      <HeroSlides />
      <PopularDestinations />
      <TopPicks />
      <Moments />
    </div>
  );
};

export default Home;
