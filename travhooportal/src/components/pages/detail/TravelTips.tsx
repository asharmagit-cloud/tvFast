'use client';

import { FC, useState } from 'react';
import DpTabs from '@/components/ui/DpTabs';

interface TravelTipsProps {
  tips: string[];
}

interface TipCategory {
  category: string;
  icon: string;
  color: string;
  gradient: string;
}

// Categories with icons and colors
const categories: TipCategory[] = [
  {
    category: 'all',
    icon: 'fa-solid fa-globe',
    color: 'text-blue-600',
    gradient: 'from-blue-500 to-cyan-500',
  },
  {
    category: 'transport',
    icon: 'fa-solid fa-car',
    color: 'text-green-600',
    gradient: 'from-green-500 to-emerald-500',
  },
  {
    category: 'food',
    icon: 'fa-solid fa-utensils',
    color: 'text-orange-600',
    gradient: 'from-orange-500 to-amber-500',
  },
  {
    category: 'culture',
    icon: 'fa-solid fa-landmark',
    color: 'text-purple-600',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    category: 'safety',
    icon: 'fa-solid fa-user-shield',
    color: 'text-red-600',
    gradient: 'from-red-500 to-rose-500',
  },
  {
    category: 'money',
    icon: 'fa-solid fa-coins',
    color: 'text-yellow-600',
    gradient: 'from-yellow-500 to-orange-400',
  },
];

// Auto-categorize tips based on keywords
const categorizeTip = (tip: string): string => {
  const lowerTip = tip.toLowerCase();
  if (
    lowerTip.includes('transport') ||
    lowerTip.includes('taxi') ||
    lowerTip.includes('bus') ||
    lowerTip.includes('metro') ||
    lowerTip.includes('travel') ||
    lowerTip.includes('drive')
  )
    return 'transport';
  if (
    lowerTip.includes('food') ||
    lowerTip.includes('eat') ||
    lowerTip.includes('restaurant') ||
    lowerTip.includes('cuisine') ||
    lowerTip.includes('dish')
  )
    return 'food';
  if (
    lowerTip.includes('culture') ||
    lowerTip.includes('tradition') ||
    lowerTip.includes('festival') ||
    lowerTip.includes('temple') ||
    lowerTip.includes('heritage')
  )
    return 'culture';
  if (
    lowerTip.includes('safe') ||
    lowerTip.includes('security') ||
    lowerTip.includes('emergency') ||
    lowerTip.includes('avoid')
  )
    return 'safety';
  if (
    lowerTip.includes('money') ||
    lowerTip.includes('cash') ||
    lowerTip.includes('currency') ||
    lowerTip.includes('pay') ||
    lowerTip.includes('budget')
  )
    return 'money';
  return 'general';
};

const getCategoryIcon = (category: string): string => {
  const found = categories.find(c => c.category === category);
  return found?.icon || 'fa-solid fa-lightbulb';
};

const getCategoryColor = (category: string): string => {
  const found = categories.find(c => c.category === category);
  return found?.color || 'text-gray-600';
};

const getCategoryGradient = (category: string): string => {
  const found = categories.find(c => c.category === category);
  return found?.gradient || 'from-gray-500 to-gray-600';
};

// Component to render tips for a category
const TipsCategory: FC<{ tips: string[]; categoryKey: string }> = ({
  tips,
  categoryKey,
}) => {
  const [expandedTips, setExpandedTips] = useState<number[]>([]);

  const toggleTip = (index: number) => {
    setExpandedTips(prev =>
      prev.includes(index) ? prev.filter(i => i !== index) : [...prev, index],
    );
  };

  const filteredTips = tips.filter(tip => {
    if (categoryKey === 'all') return true;
    return categorizeTip(tip) === categoryKey;
  });

  if (filteredTips.length === 0) {
    return (
      <div className='text-center py-12'>
        <div className='inline-block p-8 bg-gray-100 rounded-full mb-4'>
          <i className='fa-solid fa-search text-5xl text-gray-400' />
        </div>
        <p className='text-xl text-gray-600 font-medium'>
          No tips found in this category
        </p>
        <p className='text-gray-500 mt-2'>Try selecting a different category</p>
      </div>
    );
  }

  return (
    <div>
      {/* Tips Count Badge */}
      <div className='text-center mb-8'>
        <span className='inline-block bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-medium'>
          <i className='fa-solid fa-check-circle mr-2' />
          {filteredTips.length} {filteredTips.length === 1 ? 'Tip' : 'Tips'}{' '}
          Available
        </span>
      </div>

      {/* Tips Grid */}
      <div className='columns-1 md:columns-2 gap-6 space-y-6'>
        {filteredTips.map((tip, index) => {
          const category = categorizeTip(tip);
          const isExpanded = expandedTips.includes(index);
          const shortTip = tip.length > 100 ? tip.substring(0, 100) : tip;
          const needsExpansion = tip.length > 100;

          return (
            <div
              key={index}
              className='break-inside-avoid mb-6 group relative bg-white rounded-2xl shadow-md hover:shadow-2xl transition-all duration-500 border-2 border-transparent transform hover:-translate-y-2 overflow-hidden'
              style={{ pageBreakInside: 'avoid' }}
            >
              {/* Gradient Background Effect */}
              <div
                className={`absolute inset-0 bg-gradient-to-br ${getCategoryGradient(category)} opacity-0 group-hover:opacity-5 transition-opacity duration-500`}
              />

              {/* Content */}
              <div className='relative p-6'>
                {/* Icon Badge */}
                <div className='flex items-start gap-4'>
                  <div
                    className={`flex-shrink-0 w-14 h-14 rounded-xl bg-gradient-to-br ${getCategoryGradient(category)} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}
                  >
                    <i
                      className={`${getCategoryIcon(category)} text-white text-xl`}
                    />
                  </div>

                  <div className='flex-1'>
                    {/* Category Label */}
                    <div className='mb-3'>
                      <span
                        className={`inline-block text-xs font-semibold uppercase tracking-wider ${getCategoryColor(category)} bg-${getCategoryColor(category).split('-')[1]}-50 px-3 py-1 rounded-full`}
                      >
                        {category}
                      </span>
                    </div>

                    {/* Tip Text */}
                    <p className='text-gray-700 leading-relaxed text-base'>
                      {isExpanded || !needsExpansion ? tip : `${shortTip}...`}
                    </p>

                    {/* Expand/Collapse Button */}
                    {needsExpansion && (
                      <button
                        onClick={() => toggleTip(index)}
                        className={`mt-3 text-sm font-medium ${getCategoryColor(category)} cursor-pointer flex items-center gap-2 transition-all duration-300`}
                      >
                        {isExpanded ? (
                          <>
                            <span>Show Less</span>
                            <i className='fa-solid fa-chevron-up' />
                          </>
                        ) : (
                          <>
                            <span>Read More</span>
                            <i className='fa-solid fa-chevron-down' />
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>

                {/* Decorative Corner Element */}
                <div className='absolute top-0 right-0 w-20 h-20 opacity-10'>
                  <div
                    className={`w-full h-full rounded-bl-full bg-gradient-to-br ${getCategoryGradient(category)}`}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const TravelTips: FC<TravelTipsProps> = ({ tips }) => {
  if (!tips || tips.length === 0) {
    return null;
  }

  const tabConfigs = categories.map(({ category }) => ({
    key: category,
    name: category.charAt(0).toUpperCase() + category.slice(1),
    component: () => <TipsCategory tips={tips} categoryKey={category} />,
  }));

  return (
    <div className='w-full py-12 sm:py-16 px-4 bg-gradient-to-br from-gray-50 via-white to-gray-100'>
      <div className='max-w-7xl mx-auto'>
        {/* Header Section */}
        <div className='text-center mb-8 sm:mb-12'>
          <h2 className='text-3xl sm:text-4xl md:text-5xl font-bold text-gray-800 mb-3 sm:mb-4 font-playfair'>
            Travel Tips
          </h2>
          <p className='text-base sm:text-lg text-gray-600 max-w-2xl mx-auto mb-6 sm:mb-8 px-4'>
            Essential tips and insights to help you make the most of your visit
          </p>
        </div>

        {/* Tabs */}
        <DpTabs
          tabs={tabConfigs}
          defaultTab='all'
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

export default TravelTips;
