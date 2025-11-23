'use client';

import { FC, useRef } from 'react';
import ComingSoon from '@/components/ComingSoon';
import AnimatedBackground from '@/components/ui/AnimatedBackground';

const AboutUs: FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  return (
    <div ref={containerRef}>
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
      <ComingSoon />
    </div>
  );
};

export default AboutUs;
