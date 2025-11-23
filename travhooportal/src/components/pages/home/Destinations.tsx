'use client';

import PopularDestinationsFullScreen from '@/components/ui/carousels/PopularDestinationsFullScreen';
import trendingData from '@/data/trending.json';
import { useEffect, useState } from 'react';
import { Location } from '@/types/location';

export default function PopularDestinations() {
  const [destinations, setDestinations] = useState<Location[]>([]);

  useEffect(() => {
    setDestinations(trendingData.trending);
  }, []);

  return (
    <PopularDestinationsFullScreen
      destinations={destinations}
      title='Explore Top Destinations'
      id='destinations'
    />
  );
}
