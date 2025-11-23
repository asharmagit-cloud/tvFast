'use client';

import { FC, useEffect, useRef, useState } from 'react';
import AnimatedBackground from './AnimatedBackground';

interface GreetingScreenProps {
  greetingText: string;
  animationType?:
    | 'slideIn'
    | 'scaleBounce'
    | 'letterReveal'
    | 'wave'
    | 'glitch'
    | 'fadeInUp'
    | 'typewriter';
}

const ANIMATION_DURATION = 2000;
const AFTER_ANIMATION_DELAY = 1500;
const FADE_OUT_DURATION = 500;

const getAnimationStyles = (greetingText: string, animationType: string) => {
  const baseStyles = `
    @keyframes fadeOut {
      from { opacity: 1; }
      to { opacity: 0; }
    }
    .fade-out-animation {
      animation: fadeOut ${FADE_OUT_DURATION}ms ease-out forwards;
    }
  `;

  switch (animationType) {
    case 'slideIn':
      return (
        baseStyles +
        `
        @keyframes slideInFromTop {
          0% { transform: translateY(-100px); opacity: 0; }
          50% { transform: translateY(10px); opacity: 0.8; }
          100% { transform: translateY(0); opacity: 1; }
        }
        .slide-in-animation {
          animation: slideInFromTop ${ANIMATION_DURATION}ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
      `
      );

    case 'scaleBounce':
      return (
        baseStyles +
        `
        @keyframes scaleBounce {
          0% { transform: scale(0); opacity: 0; }
          50% { transform: scale(1.1); opacity: 0.8; }
          70% { transform: scale(0.95); opacity: 0.9; }
          100% { transform: scale(1); opacity: 1; }
        }
        .scale-bounce-animation {
          animation: scaleBounce ${ANIMATION_DURATION}ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
      `
      );

    case 'letterReveal':
      return (
        baseStyles +
        `
        @keyframes letterReveal {
          0% { opacity: 0; transform: translateY(20px) rotateX(90deg); }
          100% { opacity: 1; transform: translateY(0) rotateX(0deg); }
        }
        .letter-reveal-animation .letter {
          display: inline-block;
          opacity: 0;
          animation: letterReveal 0.6s ease-out forwards;
        }
        ${greetingText
          .split('')
          .map(
            (_, index: number) =>
              `.letter-reveal-animation .letter:nth-child(${index + 1}) { animation-delay: ${index * 0.1}s; }`,
          )
          .join('\n')}
      `
      );

    case 'wave':
      return (
        baseStyles +
        `
        @keyframes wave {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }
        .wave-animation .letter {
          display: inline-block;
          animation: wave 1s ease-in-out infinite;
        }
        ${greetingText
          .split('')
          .map(
            (_, index) =>
              `.wave-animation .letter:nth-child(${index + 1}) { animation-delay: ${index * 0.1}s; }`,
          )
          .join('\n')}
      `
      );

    case 'glitch':
      return (
        baseStyles +
        `
          @keyframes glitch {
            0% { transform: translate(0); }
            20% { transform: translate(-2px, 2px); }
            40% { transform: translate(-2px, -2px); }
            60% { transform: translate(2px, 2px); }
            80% { transform: translate(2px, -2px); }
            100% { transform: translate(0); }
          }
          @keyframes glitchColor {
            0% { text-shadow: 0 0 0 #f85d01; }
            25% { text-shadow: -2px 0 0 #ff0000, 2px 0 0 #00ff00; }
            50% { text-shadow: -2px 0 0 #00ff00, 2px 0 0 #0000ff; }
            75% { text-shadow: -2px 0 0 #0000ff, 2px 0 0 #ff0000; }
            100% { text-shadow: 0 0 0 #f85d01; }
          }
          .glitch-animation {
            animation: glitch 0.3s ease-in-out infinite alternate, glitchColor 0.3s ease-in-out infinite alternate;
          }
        `
      );

    case 'fadeInUp':
      return (
        baseStyles +
        `
          @keyframes fadeInUp {
            0% { 
              opacity: 0; 
              transform: translateY(60px); 
            }
            100% { 
              opacity: 1; 
              transform: translateY(0); 
            }
          }
          .fade-in-up-animation {
            animation: fadeInUp ${ANIMATION_DURATION}ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
          }
        `
      );

    case 'typewriter':
    default:
      return (
        baseStyles +
        `
        .typewriter-effect {
          display: inline-block;
          line-height: normal;
          overflow: hidden;
          white-space: nowrap;
          animation: typing ${greetingText.length * 50}ms steps(${greetingText.length}, end);
          font-family: inherit;
        }
        @keyframes typing {
          from { width: 0 }
          to { width: 100% }
        }
      `
      );
  }
};

const GreetingScreen: FC<GreetingScreenProps> = ({
  greetingText,
  animationType = 'scaleBounce',
}) => {
  const [visible, setVisible] = useState(true);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const [animationStarted, setAnimationStarted] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!greetingText) {
      setVisible(false);
      return;
    }
    setVisible(true);
    setIsFadingOut(false);

    // Start animation after a brief delay
    const startAnimationTimeout = setTimeout(() => {
      setAnimationStarted(true);
    }, 100);

    const totalDuration = ANIMATION_DURATION + AFTER_ANIMATION_DELAY;

    const fadeOutTimeout = setTimeout(() => {
      setIsFadingOut(true);
    }, totalDuration);

    const removeTimeout = setTimeout(() => {
      setVisible(false);
    }, totalDuration + FADE_OUT_DURATION);

    return () => {
      clearTimeout(startAnimationTimeout);
      clearTimeout(fadeOutTimeout);
      clearTimeout(removeTimeout);
      setVisible(false);
      setAnimationStarted(false);
    };
  }, [greetingText]);

  if (!visible) return null;

  const renderAnimatedText = () => {
    const baseClasses =
      'text-3xl md:text-5xl font-bold text-[#f85d01] text-center select-none';

    if (!animationStarted) {
      return <h1 className={`${baseClasses} opacity-0`}>{greetingText}</h1>;
    }

    switch (animationType) {
      case 'slideIn':
        return (
          <h1 className={`${baseClasses} slide-in-animation`}>
            {greetingText}
          </h1>
        );

      case 'scaleBounce':
        return (
          <h1 className={`${baseClasses} scale-bounce-animation`}>
            {greetingText}
          </h1>
        );

      case 'letterReveal':
        return (
          <h1 className={`${baseClasses} letter-reveal-animation`}>
            {greetingText.split('').map((char, index) => (
              <span key={index} className='letter'>
                {char === ' ' ? '\u00A0' : char}
              </span>
            ))}
          </h1>
        );

      case 'wave':
        return (
          <h1 className={`${baseClasses} wave-animation`}>
            {greetingText.split('').map((char, index) => (
              <span key={index} className='letter'>
                {char === ' ' ? '\u00A0' : char}
              </span>
            ))}
          </h1>
        );

      case 'glitch':
        return (
          <h1 className={`${baseClasses} glitch-animation`}>{greetingText}</h1>
        );

      case 'fadeInUp':
        return (
          <h1 className={`${baseClasses} fade-in-up-animation`}>
            {greetingText}
          </h1>
        );

      case 'typewriter':
      default:
        return (
          <h1 className={baseClasses}>
            <span className='typewriter-effect'>{greetingText}</span>
          </h1>
        );
    }
  };

  return (
    <>
      <style>{getAnimationStyles(greetingText, animationType)}</style>
      <div
        className={`fixed inset-0 z-50 flex items-center justify-center bg-[#f2f2f2] pointer-events-auto ${isFadingOut ? 'fade-out-animation' : ''}`}
        ref={containerRef}
      >
        <div className='w-full flex flex-col items-center'>
          {renderAnimatedText()}
        </div>
        <AnimatedBackground
          containerRef={containerRef as React.RefObject<HTMLElement>}
          particleCount={40}
          colors={[
            '#f85d01',
            '#ffffff',
            '#3b82f6',
            '#8b5cf6',
            '#06b6d4',
            '#10b981',
          ]}
          className='opacity-50'
        />
      </div>
    </>
  );
};

export default GreetingScreen;
