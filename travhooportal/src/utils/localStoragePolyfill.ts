/**
 * localStorage polyfill for SSR
 * This ensures localStorage is available during server-side rendering
 * to prevent errors when libraries like Swiper try to access it
 */

if (typeof window === 'undefined') {
  // Server-side: create a mock localStorage
  const storage: Record<string, string> = {};
  
  (global as any).localStorage = {
    getItem: (key: string) => storage[key] || null,
    setItem: (key: string, value: string) => {
      storage[key] = value;
    },
    removeItem: (key: string) => {
      delete storage[key];
    },
    clear: () => {
      Object.keys(storage).forEach(key => delete storage[key]);
    },
    get length() {
      return Object.keys(storage).length;
    },
    key: (index: number) => {
      const keys = Object.keys(storage);
      return keys[index] || null;
    },
  };
}
