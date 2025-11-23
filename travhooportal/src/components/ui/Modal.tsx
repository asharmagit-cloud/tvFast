'use client';

import { ReactNode, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';

interface ModalProps {
  show: boolean;
  body: ReactNode;
  title?: ReactNode;
  footer?: ReactNode;
  closeButton?: boolean;
  isStatic?: boolean;
  onHide: () => void;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'sm:max-w-sm sm:w-full',
  md: 'sm:max-w-md md:max-w-lg sm:w-full',
  lg: 'sm:max-w-2xl md:max-w-3xl lg:max-w-4xl sm:w-full',
};

const Modal = ({
  show,
  body,
  title,
  footer,
  closeButton = true,
  isStatic = false,
  onHide,
  size = 'md',
}: ModalProps) => {
  const handleEscape = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !isStatic && show) {
        onHide();
      }
    },
    [isStatic, show, onHide],
  );

  useEffect(() => {
    if (show) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [show, handleEscape]);

  if (!show) return null;

  return typeof document !== 'undefined'
    ? createPortal(
        <div
          className='fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200'
          aria-hidden='true'
        >
          <div
            className='flex items-center justify-center min-h-screen p-0 sm:p-4'
            onClick={() => {
              if (!isStatic) {
                onHide();
              }
            }}
          >
            <div
              className={`
              relative bg-white rounded-none sm:rounded-lg shadow-2xl
              w-full h-full sm:h-auto
              ${sizeClasses[size]}
              animate-in zoom-in-95 slide-in-from-bottom-4 duration-200
              flex flex-col max-h-screen sm:max-h-[90vh]
            `}
              role='dialog'
              aria-modal='true'
              aria-labelledby={title ? 'modal-title' : undefined}
              onClick={e => e.stopPropagation()}
            >
              {title && (
                <div className='flex items-center justify-between px-4 sm:px-6 py-4 border-b border-gray-200 flex-shrink-0'>
                  <div
                    id='modal-title'
                    className='text-lg sm:text-xl font-semibold text-gray-900'
                  >
                    {title}
                  </div>
                  {closeButton && (
                    <button
                      type='button'
                      onClick={onHide}
                      className='inline-flex w-6 h-6 cursor-pointer items-center justify-center rounded-full p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none'
                      aria-label='Close modal'
                    >
                      <i className='fa-solid fa-xmark' />
                    </button>
                  )}
                </div>
              )}

              {!title && closeButton && (
                <button
                  type='button'
                  onClick={onHide}
                  className='absolute w-6 h-6 cursor-pointer top-3 right-3 sm:top-4 sm:right-4 z-10 inline-flex items-center justify-center rounded-full p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none'
                  aria-label='Close modal'
                >
                  <i className='fa-solid fa-xmark' />
                </button>
              )}

              <div className='flex-1 overflow-y-auto px-4 sm:px-6 py-4'>
                {body}
              </div>

              {footer && (
                <div className='flex-shrink-0 px-4 sm:px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-none sm:rounded-b-lg'>
                  {footer}
                </div>
              )}
            </div>
          </div>
        </div>,
        document.body,
      )
    : null;
};

export default Modal;
