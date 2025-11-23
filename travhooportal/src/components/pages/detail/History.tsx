'use client';

const History = ({ history }: { history: string }) => {
  return (
    <div className='animate-fadeIn'>
      <div className='bg-white rounded-2xl p-8 shadow-md border border-gray-100'>
        <p className='text-lg leading-relaxed text-gray-700 font-inter whitespace-pre-line'>
          {history}
        </p>
      </div>
    </div>
  );
};

export default History;
