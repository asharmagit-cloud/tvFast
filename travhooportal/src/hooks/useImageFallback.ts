import { useState } from 'react';

/**
 * Custom hook to handle image fallback to default image when original fails to load
 * @param originalSrc - The original image source
 * @param fallbackSrc - The fallback image source (defaults to /images/default.jpg)
 * @returns Object containing current src and error handler
 */
export const useImageFallback = (
  originalSrc: string | undefined | null,
  fallbackSrc: string = '/images/default.jpg',
) => {
  const [imgSrc, setImgSrc] = useState(originalSrc || fallbackSrc);
  const [hasError, setHasError] = useState(false);

  const handleError = () => {
    if (!hasError && imgSrc !== fallbackSrc) {
      setHasError(true);
      setImgSrc(fallbackSrc);
    }
  };

  return {
    src: imgSrc || fallbackSrc,
    onError: handleError,
  };
};

/**
 * Simple utility function to get image source with fallback
 * @param originalSrc - The original image source
 * @param fallbackSrc - The fallback image source (defaults to /images/default.jpg)
 * @returns The image source to use
 */
export const getImageSrc = (
  originalSrc: string | undefined | null,
  fallbackSrc: string = '/images/default.jpg',
): string => {
  return originalSrc || fallbackSrc;
};
