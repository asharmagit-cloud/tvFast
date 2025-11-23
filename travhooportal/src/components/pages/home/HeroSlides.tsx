'use client';

import { FC, useEffect, useRef } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay, EffectFade, Navigation } from 'swiper/modules';
import type { Swiper as SwiperType } from 'swiper';
import { LANDING_PAGE_CAROUSEL_ITEMS } from '@/constants';
import CarouselNavigation from '@/components/ui/carousels/CarouselNavigation';
import HomeHeroSlide from '@/components/ui/carousels/cards/HomeHeroSlide';
import ButtonWithIcon from '@/components/ui/buttons/ButtonWithIcon';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/effect-fade';
import 'swiper/css/navigation';
import Image from 'next/image';

const HeroSlides: FC = () => {
  const swiperRef = useRef<SwiperType | null>(null);

  useEffect(() => {
    const preloadImages = () => {
      LANDING_PAGE_CAROUSEL_ITEMS.slice(0, 3).forEach(item => {
        const img = new window.Image();
        img.src = item.imageUrl;
      });
    };

    preloadImages();
  }, []);

  const nextSlide = () => {
    swiperRef.current?.slideNext();
  };

  const prevSlide = () => {
    swiperRef.current?.slidePrev();
  };

  return (
    <section id='intro' className='w-full h-screen relative overflow-hidden'>
      {/* Swiper Carousel */}
      <Swiper
        modules={[Autoplay, EffectFade, Navigation]}
        effect='fade'
        loop={true}
        autoplay={{ delay: 3000, disableOnInteraction: false }}
        speed={500}
        allowTouchMove={true}
        preventInteractionOnTransition={false}
        onSwiper={swiper => {
          swiperRef.current = swiper;
        }}
        className='w-full h-full'
      >
        {LANDING_PAGE_CAROUSEL_ITEMS.map((item, index) => (
          <SwiperSlide key={index}>
            <HomeHeroSlide item={item} index={index} />
            {/* Arrow Navigation - Positioned above the content area */}
            <div className='absolute bottom-4 sm:bottom-6 md:bottom-8 left-1/2 transform -translate-x-1/2 z-20'>
              <CarouselNavigation
                onPrevSlide={prevSlide}
                onNextSlide={nextSlide}
              />
            </div>
          </SwiperSlide>
        ))}
      </Swiper>

      {/* Main Title and CTA - Center */}
      <div className='absolute inset-0 z-30 flex flex-col items-center justify-center text-center px-4 sm:px-6 pointer-events-none'>
        <div className='mb-8 sm:mb-12 md:mb-16 pointer-events-auto flex flex-col items-center justify-center'>
          <div className='mb-4 sm:mb-6 w-full flex justify-center'>
            <Image
              src='/travhoo-text.svg'
              alt='Travhoo'
              width={600}
              height={100}
              className='w-[280px] sm:w-[400px] md:w-[500px] lg:w-[600px] h-auto'
            />
          </div>
          <div className='transform scale-75 sm:scale-85 md:scale-95 lg:scale-100'>
            <ButtonWithIcon
              text='Explore'
              iconClassName='fa-solid fa-arrow-right-long'
              onClick={() => {
                const nextSection = document.getElementById('destinations');
                if (nextSection) {
                  nextSection.scrollIntoView({ behavior: 'smooth' });
                  window.location.hash = 'destinations';
                }
              }}
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSlides;
