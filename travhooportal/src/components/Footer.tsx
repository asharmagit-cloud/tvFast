import Link from 'next/link';
import { FOOTER_SECTIONS, SOCIAL_MEDIA } from '@/constants';
import Image from 'next/image';

const Footer: React.FC = () => {
  return (
    <footer className='w-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 relative overflow-hidden'>
      <div className='absolute inset-0 bg-black/20 backdrop-blur-sm' />
      <div className='absolute inset-0 bg-gradient-to-r from-orange-900/20 via-transparent to-orange-900/20' />

      <div className='relative z-10 w-full px-6 sm:px-8 md:px-16 py-12 md:py-16 flex flex-col md:flex-row md:justify-between md:items-start flex-wrap'>
        <div className='flex-1 min-w-[300px] mb-12 md:mb-0 flex flex-col items-start'>
          <div className='flex items-center gap-2 select-none bg-gradient-to-r from-(--primary) via-orange-400 to-(--primary) bg-clip-text text-transparent mb-4 hover:scale-105 transition-transform duration-300 cursor-pointer'>
            <Image src='/logo.svg' alt='Travhoo' width={80} height={34} />
            <Image
              src='/travhoo-text.svg'
              alt='Travhoo'
              width={200}
              height={34}
            />
          </div>
          <p className='text-gray-300 mb-6 max-w-sm text-sm sm:text-base leading-relaxed'>
            Discover the world&apos;s most beautiful destinations with us.
            Follow our journey for amazing travel experiences, insider tips, and
            breathtaking adventures.
          </p>
          <div className='flex space-x-5'>
            {SOCIAL_MEDIA.map(({ name, link, icon }) => {
              return (
                <Link
                  className='w-12 h-12 bg-white/10 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-gradient-to-r hover:from-(--primary) hover:to-orange-500 transition-all duration-300 hover:scale-110 border border-white/20 hover:border-(--primary)/50 hover:shadow-lg hover:shadow-(--primary)/25'
                  key={name}
                  href={link}
                >
                  <i className={`${icon} text-lg`} />
                </Link>
              );
            })}
          </div>
        </div>
        <div className='flex-[2] flex flex-col gap-12 sm:flex-row justify-end w-full md:w-auto md:mb-0 md:ml-12'>
          {FOOTER_SECTIONS.map(({ name, items = [] }) => {
            return (
              <div key={name} className='min-w-[140px]'>
                <div className='font-bold text-xl text-white mb-4 pb-2 border-b border-(--primary)/50'>
                  <span className='bg-gradient-to-r from-(--primary) to-orange-400 bg-clip-text text-transparent'>
                    {name}
                  </span>
                </div>
                <ul className='space-y-3 text-gray-300 text-sm sm:text-base'>
                  {items.map(({ name, link, icon }) => {
                    return (
                      <li key={name}>
                        {link ? (
                          <Link
                            href={link}
                            className='hover:text-(--primary) transition-all duration-300 hover:translate-x-2 inline-block flex items-center group'
                          >
                            <i
                              className={`${icon} text-xs mr-2 opacity-60 group-hover:opacity-100`}
                            />
                            {name}
                          </Link>
                        ) : (
                          <span className='hover:text-(--primary) transition-all duration-300 hover:translate-x-2 inline-block flex items-center group'>
                            <i
                              className={`${icon} text-xs mr-2 opacity-60 group-hover:opacity-100`}
                            />
                            {name}
                          </span>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom row */}
      <div className='relative z-10 border-t border-white/10 bg-black/20 backdrop-blur-sm'>
        <div className='w-full flex flex-col md:flex-row justify-between items-center px-6 sm:px-8 md:px-16 py-6 text-gray-400 text-sm'>
          <div className='text-center md:text-right text-gray-500'>
            <span className='flex items-center justify-center md:justify-end'>
              <i className='fa-solid fa-copyright text-xs mr-2' />
              Copyright 2025, Travhoo. All Rights Reserved
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
