'use client';

import { useEffect, useRef, useState } from 'react';

interface LazyLoadProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  rootMargin?: string;
  threshold?: number;
}

/**
 * LazyLoad component that only renders children when they enter the viewport
 * This helps reduce initial load time by deferring non-critical content
 */
export default function LazyLoad({
  children,
  fallback = null,
  rootMargin = '100px',
  threshold = 0.1,
}: LazyLoadProps) {
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          // Disconnect observer once visible to save resources
          observer.disconnect();
        }
      },
      {
        rootMargin,
        threshold,
      }
    );

    const currentRef = containerRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
      observer.disconnect();
    };
  }, [rootMargin, threshold]);

  return (
    <div ref={containerRef}>
      {isVisible ? children : fallback}
    </div>
  );
}
