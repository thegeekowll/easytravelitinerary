import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Plane, Calendar, Users, BarChart3 } from 'lucide-react';

export default async function HomePage() {
  let homeContent = {
    heroTitle: "Travel Agency Management System",
    heroSubtitle: "Comprehensive platform for creating and managing professional travel itineraries",
    feat1Title: "200+ Tour Packages", feat1Desc: "Pre-loaded templates for quick itinerary creation",
    feat2Title: "Smart Scheduling", feat2Desc: "Day-by-day itinerary builder with auto-fill",
    feat3Title: "Role-Based Access", feat3Desc: "Admin, CS agents, and public view management",
    feat4Title: "Analytics Dashboard", feat4Desc: "Real-time insights and performance metrics",
    linksTitle: "Platform Features",
    col1Title: "For CS Agents", col1Items: ["Create custom itineraries", "Edit existing packages", "Send PDFs via email", "Track payments"],
    col2Title: "For Admins", col2Items: ["Manage users & permissions", "Content management", "System-wide analytics", "Bulk import/export"],
    col3Title: "For Travelers", col3Items: ["Public web links", "Professional 8-page PDFs", "Email delivery", "Mobile-responsive"]
  };

  try {
    const apiUrl = process.env.INTERNAL_API_URL || 'http://backend:8000/api/v1';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);

    const res = await fetch(`${apiUrl}/public/company`, {
      cache: 'no-store', // Always fetch fresh settings
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (res.ok) {
        const data = await res.json();
        const parseItems = (str: string) => str ? str.split('\n').filter(s => s.trim()) : [];
        
        homeContent = {
            heroTitle: data.home_hero_title || homeContent.heroTitle,
            heroSubtitle: data.home_hero_subtitle || homeContent.heroSubtitle,
            feat1Title: data.home_feat1_title || homeContent.feat1Title,
            feat1Desc: data.home_feat1_desc || homeContent.feat1Desc,
            feat2Title: data.home_feat2_title || homeContent.feat2Title,
            feat2Desc: data.home_feat2_desc || homeContent.feat2Desc,
            feat3Title: data.home_feat3_title || homeContent.feat3Title,
            feat3Desc: data.home_feat3_desc || homeContent.feat3Desc,
            feat4Title: data.home_feat4_title || homeContent.feat4Title,
            feat4Desc: data.home_feat4_desc || homeContent.feat4Desc,
            linksTitle: data.home_links_title || homeContent.linksTitle,
            col1Title: data.home_links_col1_title || homeContent.col1Title,
            col1Items: data.home_links_col1_items ? parseItems(data.home_links_col1_items) : homeContent.col1Items,
            col2Title: data.home_links_col2_title || homeContent.col2Title,
            col2Items: data.home_links_col2_items ? parseItems(data.home_links_col2_items) : homeContent.col2Items,
            col3Title: data.home_links_col3_title || homeContent.col3Title,
            col3Items: data.home_links_col3_items ? parseItems(data.home_links_col3_items) : homeContent.col3Items,
        };
    }
  } catch (e) {
      // Fallback to internal defaults if fetch fails
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            {homeContent.heroTitle}
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            {homeContent.heroSubtitle}
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/auth/login">
              <Button size="lg" className="text-lg px-8">
                Sign In
              </Button>
            </Link>
            <Link href="/auth/register">
              <Button size="lg" variant="outline" className="text-lg px-8">
                Register
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mt-20">
          <FeatureCard
            icon={<Plane className="h-10 w-10 text-primary" />}
            title={homeContent.feat1Title}
            description={homeContent.feat1Desc}
          />
          <FeatureCard
            icon={<Calendar className="h-10 w-10 text-primary" />}
            title={homeContent.feat2Title}
            description={homeContent.feat2Desc}
          />
          <FeatureCard
            icon={<Users className="h-10 w-10 text-primary" />}
            title={homeContent.feat3Title}
            description={homeContent.feat3Desc}
          />
          <FeatureCard
            icon={<BarChart3 className="h-10 w-10 text-primary" />}
            title={homeContent.feat4Title}
            description={homeContent.feat4Desc}
          />
        </div>

        {/* Quick Links */}
        <div className="mt-20 p-8 bg-white rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4 text-center">{homeContent.linksTitle}</h2>
          <div className="grid md:grid-cols-3 gap-6 text-center">
            <div>
              <h3 className="font-semibold text-lg mb-2">{homeContent.col1Title}</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                {homeContent.col1Items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">{homeContent.col2Title}</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                {homeContent.col2Items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">{homeContent.col3Title}</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                {homeContent.col3Items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-20">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm">
            © 2024 Travel Agency Management System. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
