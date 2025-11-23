'use client';

import { FC, useState } from 'react';
import Image from 'next/image';
import { Experience } from '@/types/location';
import { useImageFallback } from '@/hooks/useImageFallback';
import DpTabs from '@/components/ui/DpTabs';

interface ExperiencesProps {
  experiences: {
    Food?: Experience[];
    Activities?: Experience[];
    LocalMarkets?: Experience[];
    Spiritual?: Experience[];
    Historical?: Experience[];
    Nature?: Experience[];
    Cultural?: Experience[];
    Adventure?: Experience[];
    Others?: Experience[];
  };
}

interface ExperienceCategory {
  key: keyof ExperiencesProps['experiences'];
  label: string;
  icon: string;
  gradient: string;
  color: string;
}

const categories: ExperienceCategory[] = [
  {
    key: 'Food',
    label: 'Food',
    icon: 'fa-solid fa-utensils',
    gradient: 'from-orange-500 to-red-500',
    color: 'text-orange-600',
  },
  {
    key: 'Activities',
    label: 'Activities',
    icon: 'fa-solid fa-person-hiking',
    gradient: 'from-blue-500 to-cyan-500',
    color: 'text-blue-600',
  },
  {
    key: 'LocalMarkets',
    label: 'Local Markets',
    icon: 'fa-solid fa-shop',
    gradient: 'from-purple-500 to-pink-500',
    color: 'text-purple-600',
  },
  {
    key: 'Spiritual',
    label: 'Spiritual',
    icon: 'fa-solid fa-hands-praying',
    gradient: 'from-yellow-500 to-amber-500',
    color: 'text-yellow-600',
  },
  {
    key: 'Historical',
    label: 'Historical',
    icon: 'fa-solid fa-landmark',
    gradient: 'from-amber-600 to-orange-700',
    color: 'text-amber-700',
  },
  {
    key: 'Nature',
    label: 'Nature',
    icon: 'fa-solid fa-tree',
    gradient: 'from-emerald-500 to-green-600',
    color: 'text-emerald-600',
  },
  {
    key: 'Cultural',
    label: 'Cultural',
    icon: 'fa-solid fa-masks-theater',
    gradient: 'from-indigo-500 to-purple-600',
    color: 'text-indigo-600',
  },
  {
    key: 'Adventure',
    label: 'Adventure',
    icon: 'fa-solid fa-mountain',
    gradient: 'from-red-600 to-rose-600',
    color: 'text-red-600',
  },
  {
    key: 'Others',
    label: 'Others',
    icon: 'fa-solid fa-star',
    gradient: 'from-slate-500 to-gray-600',
    color: 'text-slate-600',
  },
];

interface ExperienceCardProps {
  experience: Experience;
  gradient: string;
  color: string;
  icon: string;
}

const ExperienceCard: FC<ExperienceCardProps> = ({
  experience,
  gradient,
  color,
  icon,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const { src: imageSrc, onError: handleError } = useImageFallback(
    experience.images?.card ||
      experience.images?.banner ||
      '/images/default.jpg',
  );

  const hasLongDescription =
    experience.description?.long &&
    experience.description.long.length > experience.description.short!.length;

  return (
    <div className='h-full group'>
      <div className='relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 overflow-hidden border border-gray-100 h-full flex flex-col'>
        {/* Image Section */}
        <div className='relative h-64 overflow-hidden'>
          <Image
            src={imageSrc}
            alt={experience.name || 'Experience image'}
            fill
            className={`object-cover transition-all duration-700 group-hover:scale-110 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
            onLoad={() => setImageLoaded(true)}
            onError={handleError}
            sizes='(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw'
          />
          {!imageLoaded && (
            <div className='absolute inset-0 bg-gray-200 animate-pulse' />
          )}

          {/* Gradient Overlay */}
          <div
            className={`absolute inset-0 bg-gradient-to-t ${gradient} opacity-0 group-hover:opacity-20 transition-opacity duration-500`}
          />

          {/* Type Badge */}
          <div className='absolute top-4 right-4'>
            <div
              className={`px-3 py-1 rounded-full bg-white/95 backdrop-blur-sm ${color} font-semibold text-sm shadow-lg flex items-center gap-2`}
            >
              <i className={`${icon} text-xs`} />
              <span>{experience.type}</span>
            </div>
          </div>

          {/* Location Badge */}
          {experience.locations && experience.locations.length > 0 && (
            <div className='absolute bottom-4 left-4'>
              <div className='px-3 py-1 rounded-full bg-black/70 backdrop-blur-sm text-white text-sm flex items-center gap-2'>
                <i className='fa-solid fa-location-dot text-xs' />
                <span>
                  {experience.locations[0].city?.name ||
                    experience.locations[0].state?.name}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Content Section */}
        <div className='p-6 flex-1 flex flex-col'>
          {/* Title */}
          <h3
            className={`text-xl font-bold ${color} mb-3 line-clamp-2 group-hover:line-clamp-none transition-all duration-300`}
          >
            {experience.name || experience.type || 'Experience'}
          </h3>

          {/* Description */}
          <p className='text-gray-700 leading-relaxed text-base mb-4'>
            {isExpanded && hasLongDescription
              ? experience.description?.long
              : experience.description?.short}
          </p>

          {/* Actions */}
          <div className='flex items-center justify-between gap-3'>
            {hasLongDescription && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className={`text-sm font-medium ${color} flex items-center gap-2 cursor-pointer`}
              >
                {isExpanded ? (
                  <>
                    <span>Show Less</span>
                    <i className='fa-solid fa-chevron-up text-xs' />
                  </>
                ) : (
                  <>
                    <span>Learn More</span>
                    <i className='fa-solid fa-chevron-down text-xs' />
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Decorative Corner */}
        <div className='absolute top-0 left-0 w-20 h-20 opacity-10 pointer-events-none'>
          <div
            className={`w-full h-full rounded-br-full bg-gradient-to-br ${gradient}`}
          />
        </div>
      </div>
    </div>
  );
};

// Component to render experiences for a category
const ExperiencesCategory: FC<{
  experiences: Experience[];
  categoryKey: string;
}> = ({ experiences, categoryKey }) => {
  const currentCategory = categories.find(cat => cat.key === categoryKey);

  if (experiences.length === 0) {
    return (
      <div className='text-center py-12'>
        <div className='inline-block p-8 bg-gray-100 rounded-full mb-4'>
          <i className={`${currentCategory?.icon} text-5xl text-gray-400`} />
        </div>
        <p className='text-xl text-gray-600 font-medium'>
          No experiences available in this category
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Experience Count */}
      <div className='text-center mb-8'>
        <div
          className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${currentCategory?.color} bg-opacity-10 border border-current`}
        >
          <i className={`${currentCategory?.icon}`} />
          <span className='font-semibold'>
            {experiences.length}{' '}
            {experiences.length === 1 ? 'Experience' : 'Experiences'} Available
          </span>
        </div>
      </div>

      {/* Responsive Grid */}
      <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-6 auto-rows-fr'>
        {experiences.map((experience, index) => (
          <ExperienceCard
            key={`${experience.name || experience.type || index}-${index}`}
            experience={experience}
            gradient={currentCategory?.gradient || 'from-gray-500 to-gray-600'}
            color={currentCategory?.color || 'text-gray-600'}
            icon={currentCategory?.icon || 'fa-solid fa-star'}
          />
        ))}
      </div>
    </div>
  );
};

const Experiences: FC<ExperiencesProps> = ({ experiences }) => {
  // Debug logging
  console.log('Experiences component received:', experiences);
  console.log('Experiences keys:', Object.keys(experiences || {}));
  
  // Filter categories that have experiences
  // Also check if experiences are objects with name property or just IDs
  const availableCategories = categories.filter(cat => {
    const catExperiences = experiences[cat.key];
    if (!catExperiences || !Array.isArray(catExperiences)) {
      return false;
    }
    // Check if we have actual experience objects (with name) or just IDs
    const hasValidExperiences = catExperiences.some(exp => 
      typeof exp === 'object' && exp !== null && 'name' in exp
    );
    console.log(`Category ${cat.key}: ${catExperiences.length} items, hasValid: ${hasValidExperiences}`);
    return catExperiences.length > 0 && hasValidExperiences;
  });

  if (availableCategories.length === 0) {
    return null;
  }

  const tabConfigs = availableCategories.map(category => ({
    key: category.key,
    name: category.label,
    component: () => (
      <ExperiencesCategory
        experiences={experiences[category.key] || []}
        categoryKey={category.key}
      />
    ),
  }));

  return (
    <div className='w-full py-12 sm:py-16 px-4 bg-gradient-to-br from-orange-50 via-white to-purple-50'>
      <div className='max-w-7xl mx-auto'>
        {/* Header Section */}
        <div className='text-center mb-8 sm:mb-12'>
          <h2 className='text-3xl sm:text-4xl md:text-5xl font-bold text-gray-800 mb-3 sm:mb-4 font-playfair'>
            Experiences
          </h2>
          <p className='text-base sm:text-lg text-gray-600 max-w-2xl mx-auto mb-6 sm:mb-8 px-4'>
            From culinary delights to cultural adventures, explore the best this
            destination has to offer
          </p>
        </div>

        {/* Tabs */}
        <DpTabs
          tabs={tabConfigs}
          defaultTab={availableCategories[0]?.key || 'Food'}
          tabsClassNames={{
            container: 'flex flex-row justify-center mb-8',
            tabs: 'w-auto p-2 rounded-full flex gap-3',
            defaultChildren:
              'hover:scale-105 hover:shadow-sm px-6 py-3 border-2 border-gray-200 text-md text-gray-700 hover:bg-gray-50 rounded-full transition-all duration-300 font-medium',
            activeChildren:
              'text-white font-semibold shadow-md bg-gradient-to-r from-orange-500 to-purple-600',
          }}
        />
      </div>
    </div>
  );
};

export default Experiences;
