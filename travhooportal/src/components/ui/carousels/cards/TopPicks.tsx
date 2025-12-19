'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useImageFallback } from '../../../../hooks/useImageFallback';
import getDetailPageUrl from '../../../../utils/getDetailPageUrl';
import { Location } from '@/types/location';

interface TopPicksCardProps {
  type: 'state' | 'city';
  destination: Location;
  index: number;
  isActive?: boolean;
}

const TopPicksCard = ({
  type,
  destination: { id, name, labels, tagline, images },
  index,
  isActive,
}: TopPicksCardProps) => {
  const { src: imageSrc, onError: handleImageError } = useImageFallback(
    images?.banner,
  );

  // Don't render link if ID is missing
  if (!id || id.trim() === '') {
    return (
      <div className='relative h-full rounded-2xl overflow-hidden group cursor-not-allowed opacity-75'>
        <Image
          src={imageSrc}
          alt={name}
          fill
          className='object-cover rounded-2xl'
          sizes='(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw'
          priority={index < 1}
          loading={index < 1 ? 'eager' : 'lazy'}
          quality={75}
          onError={handleImageError}
        />
        <div className='absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent rounded-2xl' />
        <div className='relative z-10 h-full flex flex-col justify-end p-6'>
          <div className='flex flex-wrap gap-2 mb-4'>
            {labels?.slice(0, 2).map((label, labelIndex) => {
              const labelText = typeof label === 'string' 
                ? label 
                : (label.name || label.id || '');
              const labelKey = typeof label === 'string' 
                ? label 
                : (label.id || `label-${labelIndex}`);
              
              return (
                <span
                  key={labelKey}
                  className='px-3 py-1 bg-white/20 backdrop-blur-sm text-white text-sm rounded-full'
                >
                  {labelText}
                </span>
              );
            })}
          </div>
          <h3 className='text-2xl font-bold text-white mb-2'>{name}</h3>
          <p className='text-white/90 text-sm'>{tagline}</p>
        </div>
      </div>
    );
  }

  return (
    <Link
      href={getDetailPageUrl(id, type || '')}
      className='block h-full rounded-2xl'
    >
      <div className='relative h-full rounded-2xl overflow-hidden group cursor-pointer transition-transform duration-300 hover:scale-[1.02]'>
        <Image
          src={imageSrc}
          alt={name}
          fill
          className='object-cover rounded-2xl'
          sizes='(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw'
          priority={index < 1}
          loading={index < 1 ? 'eager' : 'lazy'}
          quality={75}
          onError={handleImageError}
        />

        <div className='absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent rounded-2xl' />

        <div className='relative z-10 h-full flex flex-col justify-end p-6'>
          <div className='flex flex-wrap gap-2 mb-4'>
            {labels?.slice(0, 2).map((label, labelIndex) => {
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
                  className='px-3 py-1 bg-white/20 backdrop-blur-sm text-white text-sm rounded-full'
                >
                  {labelText}
                </span>
              );
            })}
          </div>

          <h3 className='text-2xl font-bold text-white mb-2'>{name}</h3>

          <p className='text-white/90 text-sm'>{tagline}</p>

          {isActive && (
            <div className='mt-4 text-center'>
              <div className='inline-flex items-center justify-center w-16 h-16 bg-(--primary) rounded-full text-white hover:animate-pulse'>
                <span className='text-xs font-bold'>EXPLORE</span>
              </div>
            </div>
          )}
        </div>

        {isActive && (
          <div className='absolute inset-0 border-4 border-white/50 rounded-2xl pointer-events-none' />
        )}
      </div>
    </Link>
  );
};

export default TopPicksCard;
