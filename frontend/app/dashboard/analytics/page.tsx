'use client';

import { useState } from 'react';
import { 
  DollarSign, 
  Users, 
  Calendar, 
  TrendingUp, 
  TrendingDown, 
  FileText, 
  Download, 
  Loader2 
} from 'lucide-react';
import { usePermissions, useAuth } from '@/lib/hooks/useAuth';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { getAnalytics } from '@/lib/api';

// Assuming AnalyticsData is a defined type, if not, it would need to be imported or defined.
interface AnalyticsData {
  overview: {
    totalRevenue: number;
    revenueGrowth: number;
    totalBookings: number;
    bookingsGrowth: number;
    activeCustomers: number;
    customersGrowth: number;
    avgBookingValue: number;
    avgBookingGrowth: number;
  };
  monthlyRevenue: {
    month: string;
    bookings: number;
    revenue: number;
  }[];
  bookingsByStatus: {
    status: string;
    count: number;
  }[];
  topDestinations?: {
    destination: string;
    bookings: number;
    revenue: number;
  }[];
  topAgents?: {
    name: string;
    bookings: number;
    revenue: number;
    conversion: number;
  }[];
  paymentMetrics?: {
    totalPaid: number;
    totalPending: number;
    totalDeposits: number;
    avgPaymentTime: number;
  };
}

export default function AnalyticsPage() {
  const [period, setPeriod] = useState('30d');
  const { can } = usePermissions();
  const { user } = useAuth();


  // DEBUG: Delete after fixing
  if (process.env.NODE_ENV === 'development') {
      console.log('User:', user);
      console.log('Permissions:', user?.permissions);
      console.log('Can View Revenue:', can('view_analytics_revenue'));
  }
  const { data: analytics, isLoading, error } = useQuery<AnalyticsData>({
    queryKey: ['analytics', period],
    queryFn: getAnalytics,
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-500">Loading analytics...</span>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="flex justify-center items-center h-96 text-red-500">
        Failed to load analytics data.
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600">Overview of your business performance</p>
          <div className="text-xs text-gray-400 mt-2 p-2 bg-gray-100 rounded">
             DEBUG: Role: {user?.role} | Perms: {user?.permissions?.map(p => p.name).join(', ')}
          </div>
        </div>
        <div className="flex gap-3">
          <Select value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="30d">Last 30 Days</option>
            <option value="3m">Last 3 Months</option>
            <option value="6m">Last 6 Months</option>
            <option value="1y">Last Year</option>
            <option value="all">All Time</option>
          </Select>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {can('view_analytics_revenue') && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${analytics?.overview?.totalRevenue?.toLocaleString() ?? 0}
            </div>
            <p className="text-xs text-muted-foreground flex items-center mt-1">
              {analytics?.overview?.revenueGrowth >= 0 ? (
                <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-600 mr-1" />
              )}
              <span className={analytics?.overview?.revenueGrowth >= 0 ? "text-green-600" : "text-red-600"}>
                {analytics?.overview?.revenueGrowth > 0 ? "+" : ""}{analytics?.overview?.revenueGrowth}%
              </span>
              <span className="ml-1">from last period</span>
            </p>
          </CardContent>
        </Card>
        )}

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.overview.totalBookings}</div>
            <p className="text-xs text-muted-foreground flex items-center mt-1">
               {analytics.overview.bookingsGrowth >= 0 ? (
                <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-600 mr-1" />
              )}
              <span className={analytics.overview.bookingsGrowth >= 0 ? "text-green-600" : "text-red-600"}>
                {analytics.overview.bookingsGrowth > 0 ? "+" : ""}{analytics.overview.bookingsGrowth}%
              </span>
              <span className="ml-1">from last period</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Customers</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.overview.activeCustomers}
            </div>
            <p className="text-xs text-muted-foreground flex items-center mt-1">
               {analytics.overview.customersGrowth >= 0 ? (
                <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-600 mr-1" />
              )}
              <span className={analytics.overview.customersGrowth >= 0 ? "text-green-600" : "text-red-600"}>
                {analytics.overview.customersGrowth > 0 ? "+" : ""}{analytics.overview.customersGrowth}%
              </span>
              <span className="ml-1">from last period</span>
            </p>
          </CardContent>
        </Card>

        {can('view_analytics_revenue') && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Booking Value</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${analytics.overview.avgBookingValue.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground flex items-center mt-1">
              {analytics.overview.avgBookingGrowth >= 0 ? (
                <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-600 mr-1" />
              )}
              <span className={analytics.overview.avgBookingGrowth >= 0 ? "text-green-600" : "text-red-600"}>
                 {analytics.overview.avgBookingGrowth > 0 ? "+" : ""}{analytics.overview.avgBookingGrowth}%
              </span>
              <span className="ml-1">from last period</span>
            </p>
          </CardContent>
        </Card>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Monthly Revenue Trend */}
        {can('view_analytics_revenue') && (
        <Card>
          <CardHeader>
            <CardTitle>Monthly Revenue Trend</CardTitle>
            <CardDescription>Revenue and booking trends over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.monthlyRevenue.map((month) => (
                <div key={month.month}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium">{month.month}</span>
                    <span className="text-sm text-gray-600">
                      {month.bookings} bookings
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                       {/* Calculate width assuming max revenue of 50k for basic visual scaling, can be improved */}
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${Math.min((month.revenue / 50000) * 100, 100)}%`,
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold w-20 text-right">
                      ${(month.revenue / 1000).toFixed(0)}k
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        )}

        {/* Booking Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Bookings by Status</CardTitle>
            <CardDescription>Distribution of booking statuses</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.bookingsByStatus.map((item) => (
                <div key={item.status}>
                  <div className="flex justify-between items-center mb-1">
                    <Badge
                      variant={
                        item.status === 'COMPLETED'
                          ? 'success'
                          : item.status === 'CONFIRMED'
                          ? 'info'
                          : item.status === 'PAID'
                          ? 'success'
                          : 'default'
                      }
                    >
                      {item.status}
                    </Badge>
                    <span className="text-sm text-gray-600">{item.count} bookings</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          item.status === 'COMPLETED'
                            ? 'bg-green-600'
                            : item.status === 'CONFIRMED'
                            ? 'bg-blue-600'
                            : item.status === 'PAID'
                            ? 'bg-green-500'
                            : 'bg-gray-400'
                        }`}
                        // Assuming percentage is calculated or part of item, previously logic suggested item.percentage existed. 
                         // If incorrect type, I'll need to check AnalyticsData interface again.
                         // But for restoration, I stick to previous known good code.
                        style={{ width: `${(item.count / analytics.overview.totalBookings) * 100}%` }} 
                      ></div>
                    </div>
                    {/* Simplified percentage for now since item.percentage wasn't in interface I added */}
                    <span className="text-sm font-semibold w-12 text-right">
                      {Math.round((item.count / analytics.overview.totalBookings) * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>


      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Top Destinations */}
        <Card>
          <CardHeader>
            <CardTitle>Top Destinations</CardTitle>
            <CardDescription>Most popular travel packages</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Destination</TableHead>
                  <TableHead className="text-right">Bookings</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(!analytics?.topDestinations || analytics.topDestinations.length === 0) ? (
                    <TableRow>
                        <TableCell colSpan={2} className="text-center text-gray-500 py-4">No data available for your role</TableCell>
                    </TableRow>
                ) : (
                    analytics.topDestinations.map((dest, index) => (
                    <TableRow key={dest.destination}>
                        <TableCell>
                        <div className="flex items-center gap-2">
                            <span className="text-lg font-semibold text-gray-400">
                            #{index + 1}
                            </span>
                            <span className="font-medium">{dest.destination}</span>
                        </div>
                        </TableCell>
                        <TableCell className="text-right">{dest.bookings}</TableCell>
                    </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Top Agents Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Agent Performance</CardTitle>
            <CardDescription>Top performing sales agents</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Agent</TableHead>
                  <TableHead className="text-right">Bookings</TableHead>
                  <TableHead className="text-right">Revenue</TableHead>
                  <TableHead className="text-right">Conversion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(!analytics?.topAgents || analytics.topAgents.length === 0) ? (
                    <TableRow>
                        <TableCell colSpan={4} className="text-center text-gray-500 py-4">No data available for your role</TableCell>
                    </TableRow>
                ) : (
                    analytics.topAgents.map((agent, index) => (
                    <TableRow key={agent.name}>
                        <TableCell>
                        <div className="flex items-center gap-2">
                            <span className="text-lg font-semibold text-gray-400">
                            #{index + 1}
                            </span>
                            <span className="font-medium">{agent.name}</span>
                        </div>
                        </TableCell>
                        <TableCell className="text-right">{agent.bookings}</TableCell>
                        <TableCell className="text-right font-semibold">
                        ${agent.revenue.toLocaleString()}
                        </TableCell>
                        <TableCell className="text-right">
                        <Badge variant="success">{agent.conversion}%</Badge>
                        </TableCell>
                    </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

      </div>

      {/* Payment Metrics */}
      {can('view_analytics_revenue') && analytics?.paymentMetrics && (
      <Card>
        <CardHeader>
          <CardTitle>Payment Metrics</CardTitle>
          <CardDescription>Financial performance and payment tracking</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Paid</p>
              <p className="text-2xl font-bold text-green-600">
                ${analytics.paymentMetrics.totalPaid?.toLocaleString() ?? 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Pending Payments</p>
              <p className="text-2xl font-bold text-yellow-600">
                ${analytics.paymentMetrics.totalPending?.toLocaleString() ?? 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Deposits</p>
              <p className="text-2xl font-bold text-blue-600">
                ${analytics.paymentMetrics.totalDeposits?.toLocaleString() ?? 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Avg Payment Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {analytics.paymentMetrics.avgPaymentTime ?? 0} days
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
      )}
    </div>
  );
}
