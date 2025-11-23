'use client';

import { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  opacity: number;
  color: string;
  type:
    | 'sparkle'
    | 'circle'
    | 'star'
    | 'triangle'
    | 'plane'
    | 'camera'
    | 'compass'
    | 'suitcase'
    | 'mountain'
    | 'palm';
  rotation: number;
  rotationSpeed: number;
  pulsePhase: number;
}

interface AnimatedBackgroundProps {
  className?: string;
  particleCount?: number;
  colors?: string[];
  containerRef?: React.RefObject<HTMLElement>;
}

const AnimatedBackground: React.FC<AnimatedBackgroundProps> = ({
  className = '',
  particleCount = 50,
  colors = ['#f85d01', '#ffffff', '#3b82f6', '#8b5cf6', '#06b6d4'],
  containerRef,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(0);
  const particlesRef = useRef<Particle[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size based on container or window
    const resizeCanvas = () => {
      if (containerRef?.current) {
        const rect = containerRef.current.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;
      } else {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      }
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize particles
    const initParticles = () => {
      particlesRef.current = [];
      for (let i = 0; i < particleCount; i++) {
        particlesRef.current.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          size: Math.random() * 4 + 1,
          speedX: (Math.random() - 0.5) * 0.5,
          speedY: (Math.random() - 0.5) * 0.5,
          opacity: Math.random() * 0.8 + 0.2,
          color: colors[Math.floor(Math.random() * colors.length)],
          type: [
            'sparkle',
            'circle',
            'star',
            'triangle',
            'plane',
            'camera',
            'compass',
            'suitcase',
            'mountain',
            'palm',
          ][Math.floor(Math.random() * 10)] as Particle['type'],
          rotation: Math.random() * Math.PI * 2,
          rotationSpeed: (Math.random() - 0.5) * 0.02,
          pulsePhase: Math.random() * Math.PI * 2,
        });
      }
    };

    initParticles();

    // Draw functions for different particle types
    const drawSparkle = (ctx: CanvasRenderingContext2D, particle: Particle) => {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);

      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.3);

      // Draw sparkle rays
      ctx.strokeStyle = particle.color;
      ctx.lineWidth = 1;
      ctx.globalAlpha = particle.opacity;

      for (let i = 0; i < 4; i++) {
        ctx.rotate(Math.PI / 2);
        ctx.beginPath();
        ctx.moveTo(0, -size);
        ctx.lineTo(0, size);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(-size * 0.5, 0);
        ctx.lineTo(size * 0.5, 0);
        ctx.stroke();
      }

      ctx.restore();
    };

    const drawCircle = (ctx: CanvasRenderingContext2D, particle: Particle) => {
      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.2);

      ctx.globalAlpha = particle.opacity;
      ctx.fillStyle = particle.color;
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, size, 0, Math.PI * 2);
      ctx.fill();

      // Add glow effect
      ctx.shadowBlur = 10;
      ctx.shadowColor = particle.color;
      ctx.fill();
      ctx.shadowBlur = 0;
    };

    const drawStar = (ctx: CanvasRenderingContext2D, particle: Particle) => {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);

      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.2);
      const spikes = 5;
      const outerRadius = size;
      const innerRadius = size * 0.4;

      ctx.globalAlpha = particle.opacity;
      ctx.fillStyle = particle.color;
      ctx.beginPath();

      for (let i = 0; i < spikes * 2; i++) {
        const radius = i % 2 === 0 ? outerRadius : innerRadius;
        const angle = (i * Math.PI) / spikes;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }

      ctx.closePath();
      ctx.fill();
      ctx.restore();
    };

    const drawTriangle = (
      ctx: CanvasRenderingContext2D,
      particle: Particle,
    ) => {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);

      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.2);

      ctx.globalAlpha = particle.opacity;
      ctx.fillStyle = particle.color;
      ctx.beginPath();
      ctx.moveTo(0, -size);
      ctx.lineTo(-size * 0.866, size * 0.5);
      ctx.lineTo(size * 0.866, size * 0.5);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    };

    const drawPlane = (ctx: CanvasRenderingContext2D, particle: Particle) => {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);

      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.2);

      ctx.globalAlpha = particle.opacity;
      ctx.fillStyle = particle.color;
      ctx.beginPath();

      // Plane body
      ctx.moveTo(size * 1.5, 0);
      ctx.lineTo(-size, 0);

      // Wings
      ctx.moveTo(-size * 0.5, 0);
      ctx.lineTo(-size * 0.8, -size * 0.8);
      ctx.lineTo(-size * 0.5, -size * 0.6);

      ctx.moveTo(-size * 0.5, 0);
      ctx.lineTo(-size * 0.8, size * 0.8);
      ctx.lineTo(-size * 0.5, size * 0.6);

      // Tail
      ctx.moveTo(-size, 0);
      ctx.lineTo(-size * 1.2, -size * 0.5);
      ctx.lineTo(-size, -size * 0.3);

      ctx.strokeStyle = particle.color;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      ctx.restore();
    };

    const drawCamera = (ctx: CanvasRenderingContext2D, particle: Particle) => {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);

      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.2);

      ctx.globalAlpha = particle.opacity;
      ctx.fillStyle = particle.color;

      // Camera body
      ctx.fillRect(-size, -size * 0.7, size * 2, size * 1.4);

      // Lens
      ctx.beginPath();
      ctx.arc(size * 0.3, 0, size * 0.6, 0, Math.PI * 2);
      ctx.strokeStyle = particle.color;
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.restore();
    };

    const drawCompass = (ctx: CanvasRenderingContext2D, particle: Particle) => {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);

      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.2);

      ctx.globalAlpha = particle.opacity;

      // Compass circle
      ctx.strokeStyle = particle.color;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(0, 0, size, 0, Math.PI * 2);
      ctx.stroke();

      // Compass needle (North pointing)
      ctx.fillStyle = particle.color;
      ctx.beginPath();
      ctx.moveTo(0, -size * 0.7);
      ctx.lineTo(-size * 0.2, 0);
      ctx.lineTo(size * 0.2, 0);
      ctx.closePath();
      ctx.fill();

      ctx.restore();
    };

    const drawSuitcase = (
      ctx: CanvasRenderingContext2D,
      particle: Particle,
    ) => {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);

      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.2);

      ctx.globalAlpha = particle.opacity;
      ctx.strokeStyle = particle.color;
      ctx.fillStyle = particle.color;
      ctx.lineWidth = 1.5;

      // Suitcase body
      ctx.strokeRect(-size, -size * 0.8, size * 2, size * 1.6);

      // Handle
      ctx.beginPath();
      ctx.arc(0, -size * 0.8, size * 0.4, Math.PI, 0, false);
      ctx.stroke();

      // Center line
      ctx.beginPath();
      ctx.moveTo(0, -size * 0.8);
      ctx.lineTo(0, size * 0.8);
      ctx.stroke();

      ctx.restore();
    };

    const drawMountain = (
      ctx: CanvasRenderingContext2D,
      particle: Particle,
    ) => {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);

      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.2);

      ctx.globalAlpha = particle.opacity;
      ctx.fillStyle = particle.color;
      ctx.beginPath();

      // Mountain peaks
      ctx.moveTo(-size * 1.5, size);
      ctx.lineTo(-size * 0.5, -size * 0.5);
      ctx.lineTo(0, size * 0.2);
      ctx.lineTo(size * 0.8, -size);
      ctx.lineTo(size * 1.5, size);
      ctx.closePath();
      ctx.fill();

      ctx.restore();
    };

    const drawPalm = (ctx: CanvasRenderingContext2D, particle: Particle) => {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);

      const size = particle.size * (1 + Math.sin(particle.pulsePhase) * 0.2);

      ctx.globalAlpha = particle.opacity;
      ctx.strokeStyle = particle.color;
      ctx.lineWidth = 2;

      // Trunk
      ctx.beginPath();
      ctx.moveTo(0, size);
      ctx.lineTo(0, -size * 0.3);
      ctx.stroke();

      // Palm leaves
      ctx.lineWidth = 1.5;
      for (let i = 0; i < 5; i++) {
        ctx.save();
        ctx.rotate((i * Math.PI * 2) / 5);
        ctx.beginPath();
        ctx.moveTo(0, -size * 0.3);
        ctx.quadraticCurveTo(size * 0.3, -size * 0.6, size * 0.6, -size);
        ctx.stroke();
        ctx.restore();
      }

      ctx.restore();
    };

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particlesRef.current.forEach(particle => {
        // Update particle position
        particle.x += particle.speedX;
        particle.y += particle.speedY;
        particle.rotation += particle.rotationSpeed;
        particle.pulsePhase += 0.05;

        // Wrap around screen edges
        if (particle.x < 0) particle.x = canvas.width;
        if (particle.x > canvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = canvas.height;
        if (particle.y > canvas.height) particle.y = 0;

        // Draw particle based on type
        switch (particle.type) {
          case 'sparkle':
            drawSparkle(ctx, particle);
            break;
          case 'circle':
            drawCircle(ctx, particle);
            break;
          case 'star':
            drawStar(ctx, particle);
            break;
          case 'triangle':
            drawTriangle(ctx, particle);
            break;
          case 'plane':
            drawPlane(ctx, particle);
            break;
          case 'camera':
            drawCamera(ctx, particle);
            break;
          case 'compass':
            drawCompass(ctx, particle);
            break;
          case 'suitcase':
            drawSuitcase(ctx, particle);
            break;
          case 'mountain':
            drawMountain(ctx, particle);
            break;
          case 'palm':
            drawPalm(ctx, particle);
            break;
        }
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [particleCount, containerRef, colors]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 pointer-events-none ${className}`}
      style={{ zIndex: 1 }}
    />
  );
};

export default AnimatedBackground;
