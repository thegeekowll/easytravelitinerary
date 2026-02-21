import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Plane, Calendar, Users, BarChart3 } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Travel Agency Management System
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Comprehensive platform for creating and managing professional travel itineraries
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
            title="200+ Tour Packages"
            description="Pre-loaded templates for quick itinerary creation"
          />
          <FeatureCard
            icon={<Calendar className="h-10 w-10 text-primary" />}
            title="Smart Scheduling"
            description="Day-by-day itinerary builder with auto-fill"
          />
          <FeatureCard
            icon={<Users className="h-10 w-10 text-primary" />}
            title="Role-Based Access"
            description="Admin, CS agents, and public view management"
          />
          <FeatureCard
            icon={<BarChart3 className="h-10 w-10 text-primary" />}
            title="Analytics Dashboard"
            description="Real-time insights and performance metrics"
          />
        </div>

        {/* Quick Links */}
        <div className="mt-20 p-8 bg-white rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4 text-center">Platform Features</h2>
          <div className="grid md:grid-cols-3 gap-6 text-center">
            <div>
              <h3 className="font-semibold text-lg mb-2">For CS Agents</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>Create custom itineraries</li>
                <li>Edit existing packages</li>
                <li>Send PDFs via email</li>
                <li>Track payments</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">For Admins</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>Manage users & permissions</li>
                <li>Content management</li>
                <li>System-wide analytics</li>
                <li>Bulk import/export</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">For Travelers</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>Public web links</li>
                <li>Professional 8-page PDFs</li>
                <li>Email delivery</li>
                <li>Mobile-responsive</li>
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
