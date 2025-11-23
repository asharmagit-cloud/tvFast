'use client';

import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { NAV_LINKS } from '../constants';
import Link from 'next/link';

const MobileMenu: React.FC<{ open: boolean; onClose: () => void }> = ({
  open,
  onClose,
}) => {
  if (!open) return null;

  return (
    <div className='fixed inset-0 z-[99] bg-black/40 backdrop-blur-sm flex flex-col items-end lg:hidden'>
      <div className='relative rounded-l-2xl z-[100] w-80 max-w-[85vw] bg-white dark:bg-gray-900 shadow-2xl h-full animate-slide-in-right p-8'>
        <div className='flex flex-col'>
          <button
            onClick={onClose}
            className='self-end text-2xl text-gray-300 hover:text-(--primary) mb-8 transition-all duration-300 hover:scale-110 hover:rotate-90'
          >
            <i className='fa-solid fa-xmark' />
          </button>
          <div className='flex flex-col space-y-6 text-gray-300 text-sm sm:text-base'>
            {NAV_LINKS.map(({ name, link }, index) => {
              return (
                <Link
                  className='transition-all duration-300 hover:scale-105 hover:text-(--primary)'
                  key={`${name}-${index}`}
                  href={link}
                  onClick={onClose}
                >
                  {name}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

const Navbar: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 200);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <nav className='rounded-b-3xl fixed top-0 left-0 w-full z-50 flex justify-center py-4 px-4 transition-all duration-500 ease-out bg-transparent backdrop-blur-xs'>
        <div
          className={`
          w-full max-w-7xl flex items-center justify-between 
          rounded-full shadow-xl py-3 px-4 
          transition-all duration-300 ease-out
          ${
            scrolled
              ? 'bg-white/95 backdrop-blur-sm'
              : 'bg-white/10 backdrop-blur-md hover:bg-white/20'
          }
        `}
        >
          <div className='flex items-center flex-shrink-0'>
            <span
              onClick={() => router.push('/')}
              className='flex items-center gap-2 drop-shadow-lg text-xl sm:text-2xl md:text-3xl font-extrabold select-none cursor-pointer transition-all duration-300 hover:scale-105'
            >
              <Image src='/logo.svg' alt='Travhoo' width={45} height={34} />
              <Image
                src='/travhoo-text.svg'
                alt='Travhoo'
                width={100}
                height={34}
              />
            </span>
          </div>

          <div className='flex-1 flex justify-end ml-6 items-center'>
            <div
              className={`hidden lg:flex items-center space-x-6 text-md font-medium ${
                scrolled ? 'text-gray-800' : 'text-white'
              }`}
            >
              {NAV_LINKS.map(({ name, link }, index) => {
                return (
                  <Link
                    className='transition-all duration-300 hover:scale-105 hover:text-(--primary)'
                    key={`${name}-${index}`}
                    href={link}
                  >
                    {name}
                  </Link>
                );
              })}
            </div>

            {/* Hamburger for mobile */}
            <button
              className={`
                flex lg:hidden items-center p-2 rounded-full focus:outline-none transition-all duration-300 ease-out hover:scale-105
                ${
                  scrolled
                    ? 'hover:bg-(--primary)/10 text-gray-700 hover:text-(--primary)'
                    : 'hover:bg-(--primary)/20 text-white'
                }
              `}
              aria-label='Open Menu'
              onClick={() => {
                setMobileMenuOpen(!mobileMenuOpen);
              }}
            >
              <i className='fa-solid fa-bars text-xl' />
            </button>
          </div>
        </div>
      </nav>

      {mobileMenuOpen && (
        <MobileMenu
          open={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(!mobileMenuOpen)}
        />
      )}
    </>
  );
};

export default Navbar;
