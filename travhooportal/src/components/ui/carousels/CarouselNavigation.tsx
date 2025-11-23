'use client';

interface CarouselNavigationProps {
  onPrevSlide: () => void;
  onNextSlide: () => void;
  leftClassName?: string;
  rightClassName?: string;
  changePositionInMobile?: boolean;
  wrapperClassName?: string;
}

const buttonClasses =
  'w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gray-800/80 border-2 border-gray-700/60 flex items-center justify-center cursor-pointer transition-all duration-300 backdrop-blur-md hover:bg-(--primary) hover:border-(--primary) hover:scale-110 shadow-lg';

const CarouselNavigation = ({
  onPrevSlide,
  onNextSlide,
  leftClassName,
  rightClassName,
  changePositionInMobile = false,
  wrapperClassName,
}: CarouselNavigationProps) => {
  return (
    <>
      <div className={`flex gap-2 sm:gap-4 ${wrapperClassName}`}>
        <button
          className={`${leftClassName} ${buttonClasses}`}
          onClick={onPrevSlide}
        >
          <i className='fa-solid fa-chevron-left text-white text-sm sm:text-lg transition-transform duration-300' />
        </button>
        <button
          className={`${rightClassName} ${buttonClasses}`}
          onClick={onNextSlide}
        >
          <i className='fa-solid fa-chevron-right text-white text-sm sm:text-lg transition-transform duration-300' />
        </button>
      </div>

      {/* Mobile Bottom Center Arrow Buttons - Visible only on mobile */}
      {changePositionInMobile && (
        <div
          className={`flex sm:hidden justify-center gap-4 mt-6 ${wrapperClassName}`}
        >
          <button onClick={onPrevSlide} className={buttonClasses}>
            <i className='fa-solid fa-chevron-left text-white text-sm sm:text-lg transition-transform duration-300' />
          </button>

          <button onClick={onNextSlide} className={buttonClasses}>
            <i className='fa-solid fa-chevron-right text-white text-sm sm:text-lg transition-transform duration-300' />
          </button>
        </div>
      )}
    </>
  );
};

export default CarouselNavigation;
