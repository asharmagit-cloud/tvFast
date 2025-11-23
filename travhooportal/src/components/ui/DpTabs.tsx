import { FC, useCallback, useEffect, useRef, useState } from 'react';

interface TabConfig {
  key: string;
  name: string;
  component: React.ComponentType<Record<string, unknown>>;
}

interface Tabs {
  tabs: TabConfig[];
  defaultTab?: string;
  onTabChange?: (tabKey: string) => void;
  className?: string;
  tabsClassNames?: {
    container?: string;
    tabs?: string;
    defaultChildren?: string;
    activeChildren?: string;
    inactiveChildren?: string;
  };
  componentClassName?: string;
  componentProps?: object;
}

const Tabs: FC<Tabs> = ({
  tabs,
  defaultTab,
  onTabChange,
  className = '',
  componentClassName = '',
  tabsClassNames: {
    container: tabsContainerClassName = 'w-full shadow-sm',
    tabs: tabsClassName = 'w-full',
    defaultChildren:
      tabChildrenClassName = 'px-6 py-4 text-md text-gray hover:bg-(--primary)/10',
    activeChildren:
      tabActiveChildrenClassName = 'text-white font-medium bg-gradient-to-r from-(--primary) to-orange-500',
    inactiveChildren: tabInactiveChildrenClassName = '',
  } = {},
  componentProps = {},
}) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.key);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const tabsContainerRef = useRef<HTMLDivElement>(null);
  const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map());

  // Check scroll position
  const checkScroll = useCallback(() => {
    if (tabsContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = tabsContainerRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
    }
  }, []);

  useEffect(() => {
    checkScroll();

    const container = tabsContainerRef.current;
    if (container) {
      container.addEventListener('scroll', checkScroll);
      const handleResize = () => {
        checkScroll();
      };
      window.addEventListener('resize', handleResize);

      return () => {
        container.removeEventListener('scroll', checkScroll);
        window.removeEventListener('resize', handleResize);
      };
    }
  }, [activeTab, checkScroll]);

  const handleTabClick = (tabKey: string) => {
    setActiveTab(tabKey);
    if (onTabChange) {
      onTabChange(tabKey);
    }

    // Scroll tab into view
    const tabElement = tabRefs.current.get(tabKey);
    if (tabElement && tabsContainerRef.current) {
      const containerRect = tabsContainerRef.current.getBoundingClientRect();
      const tabRect = tabElement.getBoundingClientRect();
      const scrollLeft = tabsContainerRef.current.scrollLeft;

      // Check if tab is out of view
      if (tabRect.left < containerRect.left) {
        tabsContainerRef.current.scrollTo({
          left: scrollLeft - (containerRect.left - tabRect.left) - 20,
          behavior: 'smooth',
        });
      } else if (tabRect.right > containerRect.right) {
        tabsContainerRef.current.scrollTo({
          left: scrollLeft + (tabRect.right - containerRect.right) + 20,
          behavior: 'smooth',
        });
      }
    }
  };

  const scroll = (direction: 'left' | 'right') => {
    if (tabsContainerRef.current) {
      const scrollAmount = 200;
      tabsContainerRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      });
    }
  };

  const ActiveComponent = tabs.find(tab => tab.key === activeTab)?.component;

  return (
    <div className={`w-full ${className}`}>
      {tabs.length > 1 && (
        <div className={`relative group ${tabsContainerClassName}`}>
          <div
            ref={tabsContainerRef}
            className={`overflow-x-auto scrollbar-hide relative ${tabsClassName}`}
            style={{
              scrollbarWidth: 'none',
              msOverflowStyle: 'none',
            }}
          >
            {canScrollLeft && (
              <div className='absolute rounded-full left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-white/80 via-white/40 to-transparent z-10 pointer-events-none' />
            )}
            {canScrollRight && (
              <div className='absolute rounded-full right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-white/80 via-white/40 to-transparent z-10 pointer-events-none' />
            )}

            {canScrollLeft && (
              <button
                onClick={() => scroll('left')}
                className='absolute cursor-pointer left-2 top-1/2 -translate-y-1/2 z-20 w-8 h-8 rounded-full bg-white/90 backdrop-blur-sm shadow-lg border border-gray-200/50 flex items-center justify-center text-gray-600 hover:text-(--primary) hover:border-(--primary)/30 hover:scale-110 transition-all duration-300 opacity-0 group-hover:opacity-100'
                aria-label='Scroll left'
              >
                <i className='fa-solid fa-chevron-left text-xs' />
              </button>
            )}
            {canScrollRight && (
              <button
                onClick={() => scroll('right')}
                className='absolute cursor-pointer right-2 top-1/2 -translate-y-1/2 z-20 w-8 h-8 rounded-full bg-white/90 backdrop-blur-sm shadow-lg border border-gray-200/50 flex items-center justify-center text-gray-600 hover:text-(--primary) hover:border-(--primary)/30 hover:scale-110 transition-all duration-300 opacity-0 group-hover:opacity-100'
                aria-label='Scroll right'
              >
                <i className='fa-solid fa-chevron-right text-xs' />
              </button>
            )}

            {tabs.map(tab => {
              const isActive = activeTab === tab.key;
              return (
                <button
                  key={tab.key}
                  ref={el => {
                    if (el) {
                      tabRefs.current.set(tab.key, el);
                    }
                  }}
                  onClick={() => handleTabClick(tab.key)}
                  className={`cursor-pointer whitespace-nowrap ${
                    isActive
                      ? tabActiveChildrenClassName
                      : tabInactiveChildrenClassName
                  }
              ${tabChildrenClassName}
            `}
                >
                  {tab.name}
                </button>
              );
            })}
          </div>
        </div>
      )}
      <div
        key={activeTab}
        className={`animate-fadeIn w-full ${componentClassName}`}
      >
        {ActiveComponent && <ActiveComponent {...componentProps} />}
      </div>

      <style jsx>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
};

export default Tabs;
