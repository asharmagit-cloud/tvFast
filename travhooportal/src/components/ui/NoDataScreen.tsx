import { FC, useRef } from 'react';
import AnimatedBackground from './AnimatedBackground';

const NoDataScreen: FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  return (
    <div
      className='relative flex items-center justify-center bg-[#f2f2f2] min-h-screen pointer-events-auto'
      ref={containerRef}
    >
      <div className='w-full flex flex-col items-center'>
        <div className='text-3xl md:text-5xl font-bold text-(--primary) text-center select-none'>
          <i className='fa-solid fa-bomb' />
          <div className='mt-4'>No Data Found</div>
        </div>
      </div>
      <AnimatedBackground
        containerRef={containerRef as React.RefObject<HTMLElement>}
        particleCount={40}
        colors={[
          '#f85d01',
          '#ffffff',
          '#3b82f6',
          '#8b5cf6',
          '#06b6d4',
          '#10b981',
        ]}
        className='opacity-50'
      />
    </div>
  );
};

export default NoDataScreen;
