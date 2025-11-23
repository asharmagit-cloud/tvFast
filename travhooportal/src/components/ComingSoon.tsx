import Image from 'next/image';
import { FC } from 'react';

const ComingSoon: FC = () => {
  return (
    <div className='min-h-screen flex flex-col items-center justify-center bg-[#f2f2f2] text-[#161618]'>
      <div className='mb-6'>
        <Image src='/logo.svg' alt='Travhoo' width={100} height={75} />
      </div>
      <div className='text-3xl md:text-4xl font-bold mb-4 text-(--primary)'>
        Launching Shortly
      </div>
      <div className='text-base md:text-lg text-center mb-8'>
        We&apos;re putting on the final touches.
      </div>
    </div>
  );
};

export default ComingSoon;
