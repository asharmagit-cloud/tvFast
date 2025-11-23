'use client';

import { useState, useEffect } from 'react';

interface Section {
  id: string;
  name: string;
}

interface SectionNavigationProps {
  sections: Section[];
}

const SectionNavigation: React.FC<SectionNavigationProps> = ({ sections }) => {
  const [activeSection, setActiveSection] = useState('intro');

  const scrollToSection = (sectionId: string) => {
    const section = document.getElementById(sectionId);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
      // Update URL hash
      window.location.hash = sectionId;
    }
  };

  useEffect(() => {
    // Set initial active section based on hash
    const hash = window.location.hash.slice(1);
    if (hash && sections.find(s => s.id === hash)) {
      setActiveSection(hash);
    }

    const handleScroll = () => {
      const scrollPosition = window.scrollY + window.innerHeight / 2;

      for (const section of sections) {
        const element = document.getElementById(section.id);
        if (element) {
          const { offsetTop, offsetHeight } = element;
          if (
            scrollPosition >= offsetTop &&
            scrollPosition < offsetTop + offsetHeight
          ) {
            setActiveSection(section.id);
            // Update URL hash without triggering scroll
            if (window.location.hash !== `#${section.id}`) {
              window.history.replaceState(null, '', `#${section.id}`);
            }
            break;
          }
        }
      }
    };

    // Handle hash changes
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash && sections.find(s => s.id === hash)) {
        setActiveSection(hash);
        const section = document.getElementById(hash);
        if (section) {
          section.scrollIntoView({ behavior: 'smooth' });
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('hashchange', handleHashChange);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, [sections]);

  return (
    <div className='fixed right-2 sm:right-4 bottom-4 sm:bottom-8 z-50'>
      <div className='flex flex-col space-y-1.5 sm:space-y-2 bg-black/20 backdrop-blur-sm rounded-full p-2 border border-white/10'>
        {sections.map(section => (
          <button
            key={section.id}
            onClick={() => scrollToSection(section.id)}
            className={`
              transition-all duration-300 rounded-full cursor-pointer
              ${
                activeSection === section.id
                  ? 'w-1.5 h-5 sm:w-2 sm:h-6 bg-(--primary)'
                  : 'w-1.5 h-1.5 sm:w-2 sm:h-2 bg-white/60 hover:bg-(--primary)/80'
              }
            `}
            aria-label={`Go to ${section.name} section`}
            title={section.name}
          />
        ))}
      </div>
    </div>
  );
};

export default SectionNavigation;
