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

// Helper to convert HEX to HSL format matching Tailwind CSS variables (e.g., "221.2 83.2% 53.3%")
function hexToHSL(hex: string) {
  // Remove hash if present
  hex = hex.replace(/^#/, '');

  // Parse RGB
  let r = 0, g = 0, b = 0;
  if (hex.length === 3) {
    r = parseInt(hex[0] + hex[0], 16);
    g = parseInt(hex[1] + hex[1], 16);
    b = parseInt(hex[2] + hex[2], 16);
  } else if (hex.length === 6) {
    r = parseInt(hex.substring(0, 2), 16);
    g = parseInt(hex.substring(2, 4), 16);
    b = parseInt(hex.substring(4, 6), 16);
  }

  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h = 0, s = 0, l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }
    h /= 6;
  }

  h = Math.round(h * 360 * 10) / 10;
  s = Math.round(s * 100 * 10) / 10;
  l = Math.round(l * 100 * 10) / 10;

  return `${h} ${s}% ${l}%`;
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  let primaryHsl = '';
  let ringHsl = '';
  let fontFamily = '';

  try {
    const apiUrl = process.env.INTERNAL_API_URL || 'http://backend:8000/api/v1';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);

    const res = await fetch(`${apiUrl}/public/company`, {
      cache: 'no-store',
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (res.ok) {
      const data = await res.json();
      
      const themeColor = data.theme_primary_color;
      if (themeColor && themeColor.startsWith('#')) {
        primaryHsl = hexToHSL(themeColor);
        ringHsl = primaryHsl; // Use the same color for the ring/focus outline
      }
      
      const themeFont = data.theme_font_family;
      if (themeFont === 'inter') {
         fontFamily = 'var(--font-inter), sans-serif';
      } else if (themeFont === 'lato') {
         fontFamily = 'var(--font-lato), sans-serif';
      } else if (themeFont === 'playfair') {
         fontFamily = 'var(--font-playfair), serif';
      }
    }
  } catch (e) {
    // Silently continue if fetch fails
  }

  // Create the dynamic style string
  let dynamicStyles = '';
  if (primaryHsl) {
     dynamicStyles += `
      :root {
        --primary: ${primaryHsl};
        --ring: ${ringHsl};
      }
      .dark {
        --primary: ${primaryHsl};
        --ring: ${ringHsl};
      }
    `;
  }
  if (fontFamily) {
     dynamicStyles += `
      body {
        font-family: ${fontFamily} !important;
      }
    `;
  }

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${playfair.variable} ${lato.variable} font-sans`}>
        {dynamicStyles && (
           <style dangerouslySetInnerHTML={{ __html: dynamicStyles }} />
        )}
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
