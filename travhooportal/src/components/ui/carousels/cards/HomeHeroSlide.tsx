'use client';

import Image from 'next/image';
import { useImageFallback } from '@/hooks/useImageFallback';

interface HomeHeroSlideItem {
  imageUrl: string;
  alt: string;
  title: string;
  description: string;
}

interface HomeHeroSlideProps {
  item: HomeHeroSlideItem;
  index: number;
}

const HomeHeroSlide = ({ item, index }: HomeHeroSlideProps) => {
  const { src: imageSrc, onError: handleImageError } = useImageFallback(
    item.imageUrl,
  );

  return (
    <div className='relative w-full h-full'>
      <Image
        src={imageSrc}
        alt={item.alt}
        fill
        className='w-full h-full object-cover'
        sizes='100vw'
        priority={index < 2}
        quality={90}
        onError={handleImageError}
      />

      {/* Slide Content with Backdrop - Full Width */}
      <div className='absolute bottom-0 left-0 right-0 bg-white/20 backdrop-blur-sm p-4 sm:p-6 md:p-8 lg:p-12 flex flex-col items-center justify-center text-center rounded-t-3xl'>
        <h2
          className='mb-2 sm:mb-3 md:mb-4 font-bold drop-shadow-lg max-w-4xl px-2 text-xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl'
          style={{
            color: 'rgb(5, 64, 72)',
            lineHeight: '1.1',
          }}
        >
          {item.title}
        </h2>
        <p
          className='drop-shadow-sm max-w-3xl px-4 mb-10 sm:mb-14 md:mb-16 lg:mb-20 text-xs sm:text-sm md:text-base lg:text-lg'
          style={{
            color: 'rgb(5, 64, 72)',
            lineHeight: '1.3',
          }}
        >
          {item.description}
        </p>
      </div>
    </div>
  );
};

export default HomeHeroSlide;
