'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay, FreeMode } from 'swiper/modules';

import 'swiper/css';
import 'swiper/css/free-mode';

type Img = { src: string; alt?: string };

/* ------------ Masonry blueprints (desktop base sizes) ------------ */
const TOP_LAYOUT = [
  { w: 520, h: 320 },
  { w: 420, h: 260 },
  { w: 280, h: 460 },
  { w: 520, h: 320 },
  { w: 320, h: 460 },
  { w: 360, h: 260 },
  { w: 420, h: 260 },
  { w: 300, h: 440 },
];

const BOTTOM_LAYOUT = [
  { w: 360, h: 500 },
  { w: 520, h: 340 },
  { w: 480, h: 300 },
  { w: 340, h: 240 },
  { w: 280, h: 460 },
  { w: 520, h: 340 },
  { w: 360, h: 260 },
  { w: 300, h: 440 },
];

/* -------------------- Responsive scaling hook -------------------- */
function useScale() {
  const [scale, setScale] = useState(1);
  useEffect(() => {
    const calc = () => {
      const w = window.innerWidth;
      if (w < 480) setScale(0.55);
      else if (w < 640) setScale(0.65);
      else if (w < 768) setScale(0.75);
      else if (w < 1024) setScale(0.85);
      else setScale(1);
    };
    calc();
    window.addEventListener('resize', calc);
    return () => window.removeEventListener('resize', calc);
  }, []);
  return scale;
}

interface RowProps {
  images: Img[];
  layout: { w: number; h: number }[];
  direction?: 'ltr' | 'rtl';
  speed?: number;
  gap?: number;
  stick?: 'top' | 'bottom';
  mirrorY?: boolean;
  imageScale?: number; // 👈 new prop
}

/* ------------------------- Single marquee row ------------------------- */
function MasonryRow({
  images,
  layout,
  direction = 'ltr',
  speed = 8000,
  gap = 24,
  stick = 'bottom',
  mirrorY = false,
  imageScale = 1,
}: RowProps) {
  const baseScale = useScale();
  const scale = baseScale * imageScale;

  const repeated = [...images, ...images, ...images];

  return (
    <div
      className={`w-full overflow-hidden ${direction === 'rtl' ? 'rtl' : ''}`}
      style={{
        transform: mirrorY ? 'scaleY(-1)' : undefined,
        transformOrigin: 'center',
      }}
    >
      <Swiper
        modules={[Autoplay, FreeMode]}
        freeMode
        loop
        dir={direction}
        slidesPerView='auto'
        spaceBetween={gap}
        speed={speed}
        autoplay={{
          delay: 0,
          disableOnInteraction: false,
          pauseOnMouseEnter: false,
        }}
        className='!py-2'
      >
        {repeated.map((img, i) => {
          const { w, h } = layout[i % layout.length];
          const W = Math.round(w * scale);
          const H = Math.round(h * scale);

          return (
            <SwiperSlide
              key={`${img.src}-${i}`}
              className='!w-auto flex'
              style={{
                alignItems: stick === 'bottom' ? 'flex-end' : 'flex-start',
              }}
            >
              <div
                className='relative overflow-hidden rounded-2xl shadow-sm'
                style={{
                  width: `${W}px`,
                  height: `${H}px`,
                  transform: mirrorY ? 'scaleY(-1)' : undefined,
                }}
              >
                <Image
                  src={img.src}
                  alt={img.alt || 'masonry image'}
                  fill
                  priority={i < 6}
                  className='object-cover'
                  sizes={`${W}px`}
                />
              </div>
            </SwiperSlide>
          );
        })}
      </Swiper>
    </div>
  );
}

interface MasonryMarqueeProps {
  topImages?: Img[];
  bottomImages?: Img[];
  className?: string;
  gap?: number;
  imageScale?: number;
}

export default function MasonryMarquee({
  topImages = DEFAULT_TOP,
  bottomImages = DEFAULT_BOTTOM,
  className,
  gap = 24,
  imageScale = 0.75,
}: MasonryMarqueeProps) {
  return (
    <section className={className}>
      <div className='mx-auto w-full max-w-screen'>
        <MasonryRow
          images={topImages}
          layout={TOP_LAYOUT}
          direction='ltr'
          speed={9000}
          gap={gap}
          stick='bottom'
          mirrorY
          imageScale={imageScale}
        />

        <MasonryRow
          images={bottomImages}
          layout={BOTTOM_LAYOUT}
          direction='rtl'
          speed={9000}
          gap={gap}
          stick='top'
          mirrorY={false}
          imageScale={imageScale}
        />
      </div>
    </section>
  );
}

const DEFAULT_TOP: Img[] = [
  { src: '/images/default.jpg', alt: 'Tree on lake' },
  { src: '/images/default.jpg', alt: 'Cable cars' },
  { src: '/images/default.jpg', alt: 'Forest bridge' },
  { src: '/images/default.jpg', alt: 'Sunset mountains' },
  { src: '/images/default.jpg', alt: 'Aurora' },
  { src: '/images/default.jpg', alt: 'Hiking ridge' },
  { src: '/images/default.jpg', alt: 'Blue seaside' },
  { src: '/images/default.jpg', alt: 'Rice terraces' },
];

const DEFAULT_BOTTOM: Img[] = [
  { src: '/images/default.jpg', alt: 'Boat in lagoon' },
  { src: '/images/default.jpg', alt: 'Mirror lake' },
  { src: '/images/default.jpg', alt: 'Coastal village' },
  { src: '/images/default.jpg', alt: 'Open road' },
  { src: '/images/default.jpg', alt: 'White villas by sea' },
  { src: '/images/default.jpg', alt: 'Misty hills' },
  { src: '/images/default.jpg', alt: 'Golden ridge' },
  { src: '/images/default.jpg', alt: 'Pier at sunset' },
];
