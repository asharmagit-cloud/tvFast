'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useImageFallback } from '../../../../hooks/useImageFallback';
import getDetailPageUrl from '../../../../utils/getDetailPageUrl';
import { Location } from '@/types/location';

interface PopularDestinationProps {
  destination: Location;
  index: number;
}

const PopularDestination = ({
  destination,
  index,
}: PopularDestinationProps) => {
  const { src: imageSrc, onError: handleImageError } = useImageFallback(
    destination.images?.banner,
  );

  return (
    <Link
      href={getDetailPageUrl(destination.id, destination.type || '')}
      className='group block w-full h-full'
    >
      <div className='relative w-full h-full cursor-pointer transition-transform duration-300 group-hover:scale-[1.02]'>
        <Image
          src={imageSrc}
          alt={destination.name}
          fill
          className='w-full h-full object-cover transition-transform duration-300 group-hover:scale-105'
          sizes='(max-width: 640px) 100vw, (max-width: 1024px) 80vw, 600px'
          priority={index < 3}
          quality={85}
          onError={handleImageError}
        />
        <div className='absolute inset-0 bg-black/40 group-hover:bg-black/50 transition-colors duration-300' />
        <div className='absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 sm:p-5 md:p-6 lg:p-8 text-white'>
          <h3 className='text-xl sm:text-2xl md:text-3xl lg:text-4xl font-semibold mb-1 sm:mb-2 drop-shadow-lg font-playfair group-hover:text-orange-400 transition-colors duration-300'>
            {destination.name}
          </h3>

          {destination.tagline ? (
            <h2 className='text-xs sm:text-sm md:text-base lg:text-lg opacity-95 drop-shadow-md line-clamp-2'>
              {destination.tagline}
            </h2>
          ) : null}
        </div>
      </div>
    </Link>
  );
};

export default PopularDestination;
