import { Metadata } from 'next';
import { Urbanist, Playfair_Display, Inter } from 'next/font/google';
import '@/styles/base.css';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

const urbanist = Urbanist({
  subsets: ['latin'],
  display: 'swap',
});

const playfair = Playfair_Display({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-playfair',
});

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
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
        <link
          rel='stylesheet'
          href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
        />
      </head>
      <body
        className={`${urbanist.className} ${playfair.variable} ${inter.variable}`}
      >
        <Navbar />
        {children}
        <Footer />
      </body>
    </html>
  );
}
