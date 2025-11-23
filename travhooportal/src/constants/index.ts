export const TYPE_TO_PAGE_MAP = {
  list: {
    state: 'states',
    city: 'cities',
  },
  detail: {
    state: 'state',
    city: 'city',
  },
};

export const HOMEPAGE_SECTIONS = [
  { id: 'intro', name: 'Intro' },
  { id: 'destinations', name: 'Destinations' },
  { id: 'popular-states', name: 'Popular States' },
  { id: 'popular-cities', name: 'Popular Cities' },
  { id: 'moments', name: 'Moments' },
];

export const SOCIAL_MEDIA = [
  {
    name: 'Instagram',
    link: 'https://www.instagram.com/travhoo.official',
    icon: 'fab fa-instagram',
  },
];

export const NAV_LINKS = [
  {
    name: 'Home',
    link: '/',
    icon: 'fa-solid fa-home',
  },
  {
    name: 'About Us',
    link: '/about-us',
    icon: 'fa-solid fa-info-circle',
  },
];

export const FOOTER_SECTIONS = [
  {
    name: 'Quick Links',
    items: [
      {
        name: 'Home',
        link: '#',
        icon: 'fa-solid fa-home',
      },
      {
        name: 'About Us',
        link: '/about-us',
        icon: 'fa-solid fa-info-circle',
      },
    ],
  },
  {
    name: 'Support',
    items: [
      {
        name: 'official@travhoo.com',
        link: 'mailto:official@travhoo.com',
        icon: 'fa-solid fa-envelope',
      },
    ],
  },
];

export const LANDING_PAGE_CAROUSEL_ITEMS = [
  {
    imageUrl: '/images/homepage/carousel-image-1.jpg',
    alt: 'Jungle View',
    title: 'Wanderlust Paradise',
    description:
      "Unveil the allure of serene beaches in breathtaking locations. Immerse yourself in nature's wonders as you explore these hidden gems. Embrace the tranquility of crystal-clear waters and golden sands. Your dream escape awaits.",
  },
  {
    imageUrl: '/images/homepage/carousel-image-2.jpg',
    alt: 'Beach View',
    title: 'Adventure Awaits',
    description:
      "Discover thrilling mountain trails and pristine wilderness. Challenge yourself with exhilarating outdoor activities while surrounded by nature's most spectacular landscapes. Every step leads to unforgettable memories.",
  },
  {
    imageUrl: '/images/homepage/carousel-image-3.jpg',
    alt: 'Mountain View',
    title: 'Cultural Heritage',
    description:
      'Journey through ancient cities and sacred temples that tell stories of centuries past. Experience the rich tapestry of traditions, festivals, and local customs that make each destination uniquely captivating.',
  },
  {
    imageUrl: '/images/homepage/carousel-image-4.jpg',
    alt: 'Road View',
    title: 'Road Less Traveled',
    description:
      'Venture off the beaten path to discover hidden treasures and authentic experiences. Connect with local communities and create meaningful memories that will last a lifetime.',
  },
  {
    imageUrl: '/images/homepage/carousel-image-5.jpg',
    alt: 'Lake View',
    title: "Nature's Symphony",
    description:
      'Find peace in the gentle rhythm of flowing waters and rustling leaves. Let the natural world rejuvenate your spirit and inspire your next great adventure.',
  },
];
