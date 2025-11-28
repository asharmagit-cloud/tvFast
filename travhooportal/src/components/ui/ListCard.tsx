'use client';

import { FC, useState } from 'react';
import Link from 'next/link';
import { useImageFallback } from '../../hooks/useImageFallback';
import Image from 'next/image';
import getDetailPageUrl from '../../utils/getDetailPageUrl';
import { Location } from '@/types/location';

const ListCard: FC<{
  item: Location;
  index: number;
  className?: string;
  type?: string;
}> = ({
  item: { id, name, tagline, images, labels },
  index,
  className,
  type,
}) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const { src: imageSrc, onError: handleImageError } = useImageFallback(
    images?.banner,
  );

  return (
    <Link
      href={getDetailPageUrl(id, type || '')}
      className={`block h-full rounded-2xl ${className}`}
    >
      <div className='relative h-full rounded-2xl overflow-hidden group cursor-pointer shadow-md hover:shadow-xl transition-all duration-500 transform hover:scale-103 border-2 border-gray-200'>
        {/* Image */}
        <Image
          src={imageSrc}
          alt={name}
          fill
          className={`object-cover transition-all duration-700 group-hover:scale-110 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
          sizes='(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw'
          priority={index < 6}
          quality={85}
          onLoad={() => setImageLoaded(true)}
          onError={handleImageError}
        />

        {!imageLoaded && (
          <div className='absolute inset-0 bg-gray-200 animate-pulse' />
        )}

        {/* Gradient Overlays */}
        <div className='absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent' />
        <div className='absolute inset-0 bg-gradient-to-r from-orange-500/20 to-purple-600/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500' />

        {/* Content */}
        <div className='relative z-10 h-full flex flex-col justify-end p-6'>
          {/* Labels */}
          {labels && labels.length > 0 && (
            <div className='flex flex-wrap gap-2 mb-4'>
              {labels.slice(0, 3).map((label, labelIndex) => {
                // Handle both string[] (legacy) and Array<{name, id}> (new format)
                const labelText = typeof label === 'string' 
                  ? label 
                  : (label.name || label.id || '');
                const labelKey = typeof label === 'string' 
                  ? label 
                  : (label.id || `label-${labelIndex}`);
                
                return (
                  <span
                    key={labelKey}
                    className='px-3 py-1 bg-white/95 backdrop-blur-sm text-gray-800 text-xs font-semibold rounded-full shadow-md transform group-hover:scale-103 transition-transform duration-300'
                    style={{
                      transitionDelay: `${labelIndex * 50}ms`,
                    }}
                  >
                    {labelText}
                  </span>
                );
              })}
            </div>
          )}

          {/* Title */}
          <h3 className='text-2xl md:text-3xl font-bold text-white mb-2 font-playfair drop-shadow-lg'>
            {name}
          </h3>

          {/* Tagline */}
          {tagline && (
            <p className='text-white/95 text-sm md:text-base leading-relaxed mb-4 drop-shadow-md'>
              {tagline}
            </p>
          )}

          {/* CTA Button */}
          <div className='mt-auto'>
            <div className='inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-full text-white font-semibold text-sm shadow-lg group-hover:shadow-xl transition-all duration-300 transform group-hover:scale-103'>
              <span>Explore Now</span>
              <i className='fa-solid fa-arrow-right text-xs' />
            </div>
          </div>
        </div>

        {/* Decorative Corner */}
        <div className='absolute top-0 right-0 w-24 h-24 opacity-20 pointer-events-none'>
          <div className='w-full h-full rounded-bl-full bg-gradient-to-br from-white to-transparent' />
        </div>
      </div>
    </Link>
  );
};

export default ListCard;
