import { FC } from 'react';

const FlagBounce: FC = () => {
  return (
    <div className='flex justify-center items-center gap-4 mt-8'>
      <div
        className='w-3 h-3 rounded-full bg-[#FF9933] animate-bounce'
        style={{ animationDuration: '2s' }}
      ></div>
      <div
        className='w-3 h-3 rounded-full bg-white animate-bounce delay-200'
        style={{ animationDuration: '2s' }}
      ></div>
      <div
        className='w-3 h-3 rounded-full bg-[#138808] animate-bounce delay-400'
        style={{ animationDuration: '2s' }}
      ></div>
    </div>
  );
};

export default FlagBounce;
