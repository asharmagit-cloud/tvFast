import { Metadata } from 'next';
import { Urbanist, Playfair_Display, Inter } from 'next/font/google';
import '@/styles/base.css';
import '@/utils/localStoragePolyfill';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Script from 'next/script';

const urbanist = Urbanist({
  subsets: ['latin'],
  display: 'swap',
  preload: true,
  // Reduce font weight variants if not all are used
  weight: ['400', '500', '600', '700'],
});

const playfair = Playfair_Display({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-playfair',
  preload: false, // Not critical for initial render
  weight: ['400', '500', '600', '700'],
});

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  preload: false, // Not critical for initial render
  weight: ['400', '500', '600'],
});

export const metadata: Metadata = {
  title: 'Travhoo',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang='en'>
      <head>
        {/* Font Awesome - Load with low priority to improve initial page load */}
        <link
          rel='preload'
          href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
          as='style'
        />
      </head>
      <body
        className={`${urbanist.className} ${playfair.variable} ${inter.variable}`}
      >
        <Navbar />
        {children}
        <Footer />
        {/* Load Font Awesome asynchronously after page load */}
        <Script
          id='font-awesome-loader'
          strategy='lazyOnload'
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                var link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css';
                document.head.appendChild(link);
              })();
            `,
          }}
        />
      </body>
    </html>
  );
}
