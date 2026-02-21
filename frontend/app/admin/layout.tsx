'use client';

import { useAuth } from '@/lib/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Home,
  FileText,
  MapPin,
  Building,
  Package,
  Users,
  Bell,
  BarChart3,
  Settings,
  LogOut,
  Grid,
  Image,
} from 'lucide-react';
import { useNotifications } from '@/hooks/use-notifications';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, logout, isLoading, hasPermission } = useAuth();
  const router = useRouter();

  // Platform Branding State
  const [logoUrl, setLogoUrl] = useState("/Easy-Travel-Logo-Black.webp");
  const [appName, setAppName] = useState("Easy. Travel");

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login');
    }
  }, [user, isLoading, router]);

  // Fetch Branding
  useEffect(() => {
     const fetchBranding = async () => {
         try {
             const [assets, templates] = await Promise.all([
                 import('@/lib/api/client').then(m => m.apiClient.listCompanyAssets('LOGO').catch(() => [])),
                 import('@/lib/api/client').then(m => m.apiClient.getCompanyTemplates().catch(() => []))
             ]);

             // Set Logo
             if (Array.isArray(assets) && assets.length > 0) {
                 const latest = assets[assets.length - 1];
                 setLogoUrl(latest.asset_url);
             }

             // Set App Name
             if (Array.isArray(templates)) {
                 const nameTpl = templates.find((t: any) => t.key === 'app_name');
                 if (nameTpl && nameTpl.content) {
                     setAppName(nameTpl.content);
                 }
             }

         } catch (e) {
             console.error("Failed to load branding", e);
         }
     };
     fetchBranding();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const isAdmin = user?.role === 'admin';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-3">
               {/* eslint-disable-next-line @next/next/no-img-element */}
               <img src={logoUrl} alt={appName} className="h-14 w-auto object-contain" />
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700">
                {user.full_name || user.email}
              </span>
              <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded">
                {user.role}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  logout();
                  router.push('/auth/login');
                }}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white shadow-sm min-h-[calc(100vh-4rem)]">
          <nav className="p-4 space-y-2">
            <NavLink href="/dashboard" icon={<Home className="h-4 w-4" />}>
              Dashboard
            </NavLink>
            <NavLink href="/dashboard/itineraries" icon={<FileText className="h-4 w-4" />}>
              Itineraries
            </NavLink>
            <NavLink href="/dashboard/notifications" icon={<Bell className="h-4 w-4" />}>
              Notifications
              {/* Notification Badge */}
              <NotificationBadge />
            </NavLink>
            <NavLink href="/dashboard/analytics" icon={<BarChart3 className="h-4 w-4" />}>
              Analytics
            </NavLink>

            {/* Admin / Management Section */}
            {(isAdmin || 
              hasPermission('view_users') || 
              hasPermission('view_destinations') || 
              hasPermission('view_2d_table') || 
              hasPermission('view_accommodations') || 
              hasPermission('view_tour_packages') ||
              hasPermission('manage_settings')
            ) && (
              <>
                <div className="pt-4 pb-2">
                  <p className="text-xs font-semibold text-gray-500 uppercase px-3">
                    Management
                  </p>
                </div>
                
                {(isAdmin || hasPermission('view_users')) && (
                  <NavLink href="/admin/users" icon={<Users className="h-4 w-4" />}>
                    Users
                  </NavLink>
                )}
                
                {(isAdmin || hasPermission('view_destinations')) && (
                  <NavLink href="/admin/destinations" icon={<MapPin className="h-4 w-4" />}>
                    Destinations
                  </NavLink>
                )}
                
                {(isAdmin || hasPermission('view_2d_table')) && (
                  <NavLink href="/admin/matrix" icon={<Grid className="h-4 w-4" />}>
                    2D Matrix
                  </NavLink>
                )}
                
                {(isAdmin || hasPermission('view_accommodations')) && (
                  <NavLink href="/admin/accommodations" icon={<Building className="h-4 w-4" />}>
                    Accommodations
                  </NavLink>
                )}
                
                {(isAdmin || hasPermission('view_tour_packages')) && (
                  <NavLink href="/admin/tours" icon={<Package className="h-4 w-4" />}>
                    Base Tours
                  </NavLink>
                )}
                
                {(isAdmin || hasPermission('manage_settings')) && (
                  <NavLink href="/admin/gallery" icon={<Image className="h-4 w-4" />}>
                    Image Gallery
                  </NavLink>
                )}

                {isAdmin && (
                  <NavLink href="/admin/settings" icon={<Settings className="h-4 w-4" />}>
                    Settings
                  </NavLink>
                )}
              </>
            )}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8 text-black">{children}</main>
      </div>
    </div>
  );
}

function NavLink({
  href,
  icon,
  children,
}: {
  href: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
    >
      {icon}
      {children}
    </Link>
  );
}


function NotificationBadge() {
  const { unreadCount } = useNotifications();
  if (!unreadCount || unreadCount === 0) return null;
  
  return (
    <span className="ml-auto bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full min-w-[20px] text-center">
      {unreadCount > 99 ? '99+' : unreadCount}
    </span>
  );
}
