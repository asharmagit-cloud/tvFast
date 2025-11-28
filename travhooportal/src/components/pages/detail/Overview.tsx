'use client';

import { useState } from 'react';

const Overview = ({
  description = {},
  labels,
}: {
  description: {
    short?: string;
    long?: string;
  };
  labels?: Array<{ name: string; id: string }> | string[];
}) => {
  const [showFullDescription, setShowFullDescription] = useState(
    !description?.short || false,
  );

  if (!description?.short && !description?.long && labels) {
    return (
      <div className='text-center italic text-gray-500'>No data found</div>
    );
  }

  return (
    <div className='flex flex-col gap-6'>
      {description?.short && (
        <div className='text-center'>
          <p className='text-xl leading-relaxed text-gray-700 font-inter'>
            {description.short}
          </p>
        </div>
      )}

      {labels && labels.length > 0 && (
        <div className='flex flex-wrap gap-3 justify-center'>
          {labels.map((label, index) => {
            // Handle both string[] (legacy) and Array<{name, id}> (new format)
            const labelText = typeof label === 'string' 
              ? label 
              : (label.name || label.id || '');
            const labelKey = typeof label === 'string' 
              ? label 
              : (label.id || `label-${index}`);
            
            return (
              <span
                key={labelKey}
                className='group px-5 py-2.5 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full text-sm font-semibold shadow-md hover:shadow-lg transition-all duration-300 transform cursor-default'
                style={{
                  animationDelay: `${index * 100}ms`,
                }}
              >
                {labelText}
              </span>
            );
          })}
        </div>
      )}

      {description?.long && showFullDescription && (
        <div className='animate-fadeIn'>
          <div className='bg-white rounded-2xl p-8 shadow-md border border-gray-100'>
            <p className='text-lg leading-relaxed text-gray-700 font-inter whitespace-pre-line'>
              {description.long}
            </p>
          </div>
        </div>
      )}

      {description?.long && description?.short && (
        <div className='flex justify-center'>
          <button
            onClick={() => setShowFullDescription(!showFullDescription)}
            className='px-6 py-3 cursor-pointer text-sm font-semibold bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full shadow-md hover:shadow-lg transition-all duration-300 transform hover:scale-105'
          >
            <div className='flex items-center gap-2'>
              {showFullDescription ? 'Show Less' : 'Read More'}
              <i
                className={`fa-solid text-xs ${
                  showFullDescription ? 'fa-chevron-up' : 'fa-chevron-down'
                }`}
              />
            </div>
          </button>
        </div>
      )}
    </div>
  );
};

export default Overview;
