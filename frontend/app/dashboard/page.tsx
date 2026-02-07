'use client';
import { useAuth } from '@/lib/hooks/useAuth';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { 
  FileText, DollarSign, 
  TrendingUp, Users, Calendar, Mail, AlertCircle, Layout
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

// Types aligned with backend response
interface AnalyticsData {
  overview: any;
  monthlyRevenue: any[];
  topDestinations?: any[];
  topAgents?: any[];
  bookingsByStatus: any[];
  paymentMetrics?: any;
  adminToday?: any;
  perAgentToday?: any[];
  agentToday?: any;
  upcomingDepartures?: any[];
  recentActivity?: any[];
  agentOverview?: any;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getAnalytics();
        setData(data);
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setLoading(false);
      }
    };
    loadAnalytics();
  }, []);

  if (loading) return <div className="p-8">Loading dashboard...</div>;
  if (!data) return <div className="p-8">Failed to load dashboard data.</div>;

  const isAdmin = user?.role === 'admin' || (typeof user?.role === 'object' && user?.role?.name === 'admin');

  return (
    <div>
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.full_name || 'User'}!
          </h1>
          <p className="text-gray-600 mt-1">
            {isAdmin 
              ? "Here's the system-wide overview for today." 
              : "Here's your personal activity and upcoming tasks."}
          </p>
        </div>
        <Link href="/dashboard/itineraries/new">
            <Button>
                <FileText className="mr-2 h-4 w-4" /> Create New Itinerary
            </Button>
        </Link>
      </div>

      {isAdmin ? <AdminDashboard data={data} /> : <AgentDashboard data={data} />}
    </div>
  );
}

function AdminDashboard({ data }: { data: AnalyticsData }) {
  const { overview, adminToday, perAgentToday, topAgents } = data;

  return (
    <div className="space-y-8">
      {/* 1. Today's Flash Report */}
      <section>
        <h2 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
            <Calendar className="h-5 w-5 text-blue-600" /> Today's Activity
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <StatCard title="Itineraries Created" value={adminToday?.total_itineraries_created ?? 0} icon={<FileText className="h-6 w-6 text-blue-600" />} trend="Today" />
            <StatCard title="Departures" value={adminToday?.departures_today ?? 0} icon={<Layout className="h-6 w-6 text-green-600" />} trend="Today" />
            <StatCard title="Emails Sent" value={adminToday?.total_emails_sent ?? 0} icon={<Mail className="h-6 w-6 text-purple-600" />} trend="Today" />
            <StatCard title="Active Agents" value={adminToday?.active_agents ?? 0} icon={<Users className="h-6 w-6 text-orange-600" />} trend="Online" />
        </div>
      </section>

       {/* 2. Overview Stats */}
       <section>
        <h2 className="text-lg font-semibold mb-4 text-gray-800">Company Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <StatCard title="Total Revenue" value={`$${overview.totalRevenue.toLocaleString()}`} icon={<DollarSign className="h-6 w-6 text-green-700" />} trend={`${overview.revenueGrowth}% growth`} />
            <StatCard title="Total Bookings" value={overview.totalBookings} icon={<FileText className="h-6 w-6 text-blue-700" />} trend={`${overview.bookingsGrowth}% growth`} />
            <StatCard title="Avg Booking Value" value={`$${overview.avgBookingValue.toLocaleString()}`} icon={<TrendingUp className="h-6 w-6 text-indigo-600" />} trend="Per booking" />
            <StatCard title="Active Customers" value={overview.activeCustomers} icon={<Users className="h-6 w-6 text-pink-600" />} trend="Total unique" />
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 3. Agent Performance Today */}
        <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4 text-gray-800">Itineraries Created Today (By Agent)</h3>
            {perAgentToday && perAgentToday.length > 0 ? (
                <div className="space-y-3">
                    {perAgentToday.map((item: any, idx: number) => (
                        <div key={idx} className="flex justify-between items-center border-b pb-2 last:border-0 hover:bg-gray-50 p-2 rounded">
                            <span className="text-gray-700 font-medium">{item.agent}</span>
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-bold">{item.itineraries_created} created</span>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="text-gray-500 text-sm italic">No itineraries created yet today.</p>
            )}
        </div>

        {/* 4. Top Performing Agents (All Time/Recent) */}
        <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4 text-gray-800">Top Agents (Revenue)</h3>
            <div className="space-y-4">
                {topAgents?.map((agent: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">
                                {agent.name.charAt(0)}
                            </div>
                            <div>
                                <p className="text-sm font-medium">{agent.name}</p>
                                <p className="text-xs text-gray-500">{agent.bookings} bookings</p>
                            </div>
                        </div>
                        <div className="text-right">
                             <p className="text-sm font-bold text-gray-900">${agent.revenue.toLocaleString()}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
      </div>
    </div>
  );
}

function AgentDashboard({ data }: { data: AnalyticsData }) {
  const { agentToday, upcomingDepartures, recentActivity, agentOverview } = data;

  return (
    <div className="space-y-8">
      {/* 1. My Day Stats */}
      <section>
        <h2 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
            <Calendar className="h-5 w-5 text-blue-600" /> My Day
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <StatCard title="Created Today" value={agentToday?.itineraries_created ?? 0} icon={<FileText className="h-6 w-6 text-blue-600" />} trend="Itineraries" />
            <StatCard title="Edited Today" value={agentToday?.itineraries_edited ?? 0} icon={<FileText className="h-6 w-6 text-yellow-600" />} trend="Itineraries" />
            <StatCard title="Emails Sent" value={agentToday?.emails_sent ?? 0} icon={<Mail className="h-6 w-6 text-purple-600" />} trend="Today" />
            <StatCard title="Drafts" value={agentOverview?.incomplete_count ?? 0} icon={<AlertCircle className="h-6 w-6 text-orange-600" />} trend="Total Incomplete" />
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
         {/* 2. Upcoming Departures */}
         <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4 text-gray-800 flex justify-between items-center">
                <span>My Upcoming Departures</span>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Next 10</span>
            </h3>
            <div className="space-y-4">
                {upcomingDepartures && upcomingDepartures.length > 0 ? upcomingDepartures.map((trip: any, idx: number) => (
                    <div key={idx} className="flex items-start gap-3 border-b pb-3 last:border-0">
                         <div className="bg-green-50 p-2 rounded text-green-600 text-center min-w-[60px]">
                            <p className="text-xs font-bold uppercase">{new Date(trip.departure_date).toLocaleDateString('en-US', { month: 'short' })}</p>
                            <p className="text-lg font-bold">{new Date(trip.departure_date).getDate()}</p>
                        </div>
                        <div>
                            <p className="font-medium text-gray-900">{trip.title}</p>
                            <p className="text-sm text-gray-600">Client: {trip.traveler}</p>
                            <p className="text-xs text-orange-600 font-medium mt-1">
                                {trip.days_until === 0 ? 'Departs Today!' : `In ${trip.days_until} days`}
                            </p>
                        </div>
                        <div className="ml-auto">
                           <Link href={`/dashboard/itineraries/${trip.id}`}>
                                <Button size="sm" variant="outline" className="h-7 text-xs">View</Button>
                           </Link>
                        </div>
                    </div>
                )) : (
                    <p className="text-gray-500 text-sm">No upcoming departures soon.</p>
                )}
            </div>
         </div>

         {/* 3. Recent Activity */}
         <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-4 text-gray-800">My Recent Activity</h3>
            <div className="space-y-4">
                {recentActivity && recentActivity.length > 0 ? recentActivity.map((act: any, idx: number) => (
                     <ActivityItem 
                        key={idx}
                        title={act.description || act.action} 
                        description={`${act.entity_type} - ${new Date(act.timestamp).toLocaleTimeString()}`} 
                        time={new Date(act.timestamp).toLocaleDateString()}
                    />
                )) : (
                    <p className="text-gray-500 text-sm">No recent activity recorded.</p>
                )}
            </div>
         </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, trend }: { title: string; value: string | number; icon: React.ReactNode; trend: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-transparent hover:border-blue-500 transition-all">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          <p className="text-xs text-gray-400 mt-1 font-medium">{trend}</p>
        </div>
        <div className="p-3 bg-gray-50 rounded-full">{icon}</div>
      </div>
    </div>
  );
}

function ActivityItem({ title, description, time }: { title: string; description: string; time: string }) {
  return (
    <div className="flex items-start gap-3 pb-3 border-b last:border-b-0 border-dashed">
      <div className="w-2.5 h-2.5 bg-gray-300 rounded-full mt-2 ring-4 ring-white"></div>
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-800">{title}</p>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
      <span className="text-xs text-gray-400 whitespace-nowrap">{time}</span>
    </div>
  );
}
