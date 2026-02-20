import type { Metadata } from 'next';
import { Inter, Playfair_Display, Lato } from 'next/font/google';
import './globals.css';
import { Providers } from '@/components/providers';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' });
const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-playfair', display: 'swap' });
const lato = Lato({
  subsets: ['latin'],
  weight: ['100', '300', '400', '700', '900'],
  variable: '--font-lato',
  display: 'swap',
});

export async function generateMetadata(): Promise<Metadata> {
  const fallback: Metadata = {
    title: 'Easy. Travel Itinerary Builder',
    description: 'Easy. Travel Itinerary Builder - Create stunning travel itineraries.',
    keywords: ['travel', 'itinerary', 'builder', 'easy', 'safari', 'tour'],
  };

  try {
    // Use internal docker network URL for server-side fetching with a 3-second timeout
    const apiUrl = process.env.INTERNAL_API_URL || 'http://backend:8000/api/v1';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);

    const res = await fetch(`${apiUrl}/public/company`, {
      next: { revalidate: 60 },
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (res.ok) {
        const data = await res.json();
        const appName = data.company_name || 'Easy. Travel Itinerary Builder';
        return {
          title: appName,
          description: `${appName} - Create stunning travel itineraries.`,
          keywords: ['travel', 'itinerary', 'builder', 'easy', 'safari', 'tour'],
        };
    }
  } catch (e) {
      // Timeout or network error - use fallback silently
  }

  return fallback;
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${playfair.variable} ${lato.variable} font-sans`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
