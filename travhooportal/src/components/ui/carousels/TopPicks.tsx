'use client';

import { useRef, useState, useEffect } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, EffectCoverflow } from 'swiper/modules';
import type { Swiper as SwiperType } from 'swiper';
import Link from 'next/link';
import TopPicksCard from './cards/TopPicks';
import CarouselNavigation from './CarouselNavigation';
import { City, State } from '@/types/location';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import 'swiper/css/effect-coverflow';

const LIST_TYPE_TO_PAGE_MAP = {
  state: 'states',
  city: 'cities',
};

const fetchCities = async () => {
  const response = await fetch('/api/v1/cities/');
  const data = await response.json();
  return data.cities;
};

const fetchStates = async () => {
  const response = await fetch('/api/v1/states/');
  const data = await response.json();
  return data.states;
};

// map the fetchCities and fetchStates to the data

interface TopPicksCarouselProps {
  id: string;
  title: string;
  backgroundImage: string;
  data: State[] | City[];
  type: 'state' | 'city';
}

const TopPicksCarousel = ({
  id,
  title,
  backgroundImage,
  data,
  type,
}: TopPicksCarouselProps) => {
  const swiperRef = useRef<SwiperType | null>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const preloadImages = () => {
      data.slice(0, 5).forEach(item => {
        const img = new window.Image();
        img.src = item.images?.banner || '';
      });
    };

    preloadImages();
  }, [data]);

  const goToPrevSlide = () => {
    swiperRef.current?.slidePrev();
  };

  const goToNextSlide = () => {
    swiperRef.current?.slideNext();
  };

  return (
    <section
      id={id}
      className='relative min-h-screen w-full overflow-hidden bg-cover bg-center bg-no-repeat'
      style={{
        backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('${backgroundImage}')`,
      }}
    >
      <div className='absolute inset-0 bg-gradient-to-r from-black/50 via-transparent to-black/50' />

      <div className='relative z-10 flex flex-col items-center justify-center min-h-screen px-4 sm:px-6 md:px-8 py-16 sm:py-20 md:py-24'>
        <div className='mb-12 sm:mb-16 md:mb-20 w-full max-w-7xl'>
          <div className='flex flex-col sm:flex-row items-center justify-between gap-6 sm:gap-8'>
            <h2 className='text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white text-center sm:text-left font-playfair drop-shadow-2xl'>
              {title}
            </h2>
            <Link
              href={`/search/${LIST_TYPE_TO_PAGE_MAP[type]}`}
              className='inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full font-semibold text-sm shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 whitespace-nowrap'
            >
              <span>View All</span>
              <i className='fa-solid fa-arrow-right text-xs' />
            </Link>
          </div>
        </div>

        <div className='relative w-full max-w-6xl mx-auto px-8 sm:px-12 md:px-16 lg:px-20'>
          <Swiper
            onSwiper={swiper => {
              swiperRef.current = swiper;
            }}
            modules={[Navigation, Pagination, EffectCoverflow]}
            effect='coverflow'
            grabCursor={true}
            centeredSlides={true}
            loop={true}
            slidesPerView={3}
            spaceBetween={0}
            speed={400}
            watchSlidesProgress={true}
            coverflowEffect={{
              rotate: 15,
              stretch: 0,
              depth: 200,
              modifier: 1,
              slideShadows: false,
            }}
            onSlideChange={swiper => setActiveIndex(swiper.realIndex)}
            className='w-full h-[300px] sm:h-[350px] md:h-[400px] lg:h-[450px]'
            breakpoints={{
              320: {
                slidesPerView: 1,
                coverflowEffect: {
                  rotate: 0,
                  stretch: 0,
                  depth: 100,
                  modifier: 1,
                  slideShadows: false,
                },
              },
              768: {
                slidesPerView: 2,
                coverflowEffect: {
                  rotate: 10,
                  stretch: 0,
                  depth: 150,
                  modifier: 1,
                  slideShadows: false,
                },
              },
              1024: {
                slidesPerView: 3,
                coverflowEffect: {
                  rotate: 15,
                  stretch: 0,
                  depth: 200,
                  modifier: 1,
                  slideShadows: false,
                },
              },
            }}
          >
            {data.map((item, index) => (
              <SwiperSlide
                key={`${item.id}-${index}`}
                className='w-full max-w-sm py-2'
              >
                <TopPicksCard
                  type={type}
                  key={item.id}
                  destination={item}
                  isActive={activeIndex === index}
                  index={index}
                />
              </SwiperSlide>
            ))}
          </Swiper>
          <CarouselNavigation
            onPrevSlide={goToPrevSlide}
            onNextSlide={goToNextSlide}
            changePositionInMobile={true}
            leftClassName='hidden sm:flex absolute -left-1 sm:-left-2 md:-left-4 top-1/2 transform -translate-y-1/2 z-20'
            rightClassName='hidden sm:flex absolute -right-1 sm:-right-2 md:-right-4 top-1/2 transform -translate-y-1/2 z-20'
          />
        </div>
      </div>
    </section>
  );
};

export default TopPicksCarousel;
