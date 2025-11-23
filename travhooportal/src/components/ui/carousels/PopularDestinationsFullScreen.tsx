'use client';

import { useState, useEffect, useRef } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { EffectFade, Navigation } from 'swiper/modules';
import type { Swiper as SwiperType } from 'swiper';
import PopularDestination from './cards/PopularDestination';
import { getImageSrc } from '../../../hooks/useImageFallback';
import CarouselNavigation from './CarouselNavigation';
import { Location } from '@/types/location';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/effect-fade';
import 'swiper/css/navigation';

interface PopularDestinationsFullScreenProps {
  destinations: Location[];
  title: string;
  id: string;
}

const PopularDestinationsFullScreen = ({
  destinations,
  title,
  id,
}: PopularDestinationsFullScreenProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [nextIndex, setNextIndex] = useState(1);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const swiperRef = useRef<SwiperType | null>(null);

  // Optimized image preloading - only preload current and next few images
  useEffect(() => {
    const preloadImages = (startIndex: number, count: number = 3) => {
      for (let i = 0; i < count; i++) {
        const index = (startIndex + i) % destinations.length;
        const img = new window.Image();
        img.src = getImageSrc(destinations[index]?.images?.banner);
      }
    };

    preloadImages(currentIndex);
  }, [currentIndex, destinations]);

  const currentDestination = destinations[currentIndex];

  const handleSlideChange = (swiper: SwiperType) => {
    const newIndex = swiper.realIndex;
    if (newIndex !== currentIndex) {
      setIsTransitioning(true);
      setNextIndex(newIndex);

      // Delay the index update slightly for smoother transition
      setTimeout(() => {
        setCurrentIndex(newIndex);
        setIsTransitioning(false);
      }, 100);
    }
  };

  const nextSlide = () => {
    swiperRef.current?.slideNext();
  };

  const prevSlide = () => {
    swiperRef.current?.slidePrev();
  };

  return (
    <section
      className='relative w-full min-h-[80vh] sm:min-h-screen overflow-hidden flex items-center'
      id={id}
    >
      {/* Optimized Background Images - Fade transition */}
      <div className='absolute inset-0'>
        {/* Current Background */}
        <div
          className='absolute inset-0 bg-cover bg-center bg-no-repeat transition-opacity duration-500 ease-out will-change-auto'
          style={{
            backgroundImage: `url(${getImageSrc(currentDestination?.images?.banner)})`,
            opacity: isTransitioning ? 0 : 1,
          }}
        />

        {/* Next Background - only render during transition */}
        {isTransitioning && (
          <div
            className='absolute inset-0 bg-cover bg-center bg-no-repeat transition-opacity duration-500 ease-out will-change-auto'
            style={{
              backgroundImage: `url(${getImageSrc(
                destinations[nextIndex]?.images?.banner,
              )})`,
              opacity: 1,
            }}
          />
        )}
      </div>

      <div className='absolute inset-0 bg-gradient-to-r from-black/60 via-black/40 to-black/60' />

      <div className='relative z-10 w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20 md:py-24'>
        <h2 className='text-white text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold drop-shadow-2xl mb-8 sm:mb-12 md:mb-16 text-center font-playfair'>
          {title}
        </h2>
        <div className='relative px-4 w-full'>
          <div className='relative max-w-4xl mx-auto rounded-xl overflow-hidden'>
            <Swiper
              modules={[EffectFade, Navigation]}
              effect='fade'
              loop={true}
              autoplay={false}
              speed={500}
              onSwiper={swiper => {
                swiperRef.current = swiper;
              }}
              onSlideChange={handleSlideChange}
              className='w-full h-[300px] sm:h-[350px] md:h-[400px] lg:h-[450px]'
            >
              {destinations.map((destination, index) => (
                <SwiperSlide key={destination.id}>
                  <PopularDestination destination={destination} index={index} />
                </SwiperSlide>
              ))}
            </Swiper>
          </div>
          <CarouselNavigation
            onPrevSlide={prevSlide}
            onNextSlide={nextSlide}
            changePositionInMobile={true}
            leftClassName='hidden sm:flex absolute -left-1 sm:-left-2 md:-left-4 top-1/2 transform -translate-y-1/2 z-20 -ml-4'
            rightClassName='hidden sm:flex absolute -right-1 sm:-right-2 md:-right-4 top-1/2 transform -translate-y-1/2 z-20 -mr-4'
          />
        </div>
      </div>
    </section>
  );
};

export default PopularDestinationsFullScreen;
