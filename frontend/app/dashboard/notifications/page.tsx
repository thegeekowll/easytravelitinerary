'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { BellOff, Check, CheckCheck, Trash2, Filter } from 'lucide-react';
import toast from 'react-hot-toast';
import { useNotifications } from '@/hooks/use-notifications';
import { apiClient } from '@/lib/api/client';


const priorityColors: Record<string, 'default' | 'warning' | 'destructive'> = {
  low: 'default',
  medium: 'warning',
  high: 'destructive',
  urgent: 'destructive',
};

const typeIcons: Record<string, string> = {
  '3_day_arrival': '✈️',
  'payment_confirmed': '💰',
  'assigned': '📋',
  'edited': '📝',
  'custom': '📬',
};

export default function NotificationsPage() {
  const router = useRouter();
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  const { 
    notifications, 
    unreadCount, 
    markAsRead, 
    markAllAsRead, 
    deleteNotification,
    isLoading 
  } = useNotifications({ type: filterType, status: filterStatus });

  const handleNotificationClick = (notification: any) => {
    if (!notification.is_read) {
      markAsRead(notification.id);
    }
    if (notification.action_url) {
      router.push(notification.action_url);
    }
  };

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) return <div className="text-center py-20">Loading notifications...</div>;

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <p className="text-gray-600 mt-1">
            {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
          </p>
        </div>
        <Button onClick={() => markAllAsRead()} disabled={unreadCount === 0}>
          <CheckCheck className="h-4 w-4 mr-2" />
          Mark All as Read
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Type
            </label>
            <Select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="3_day_arrival">Arrival Reminders</option>
              <option value="payment_confirmed">Payment Received</option>
              <option value="assigned">Assigned</option>
              <option value="edited">Edited</option>
              <option value="custom">System Message</option>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Status
            </label>
            <Select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Notifications</option>
              <option value="unread">Unread Only</option>
              <option value="read">Read Only</option>
            </Select>
          </div>

          <div className="flex items-end">
            <Button variant="outline" className="w-full">
              <Filter className="h-4 w-4 mr-2" />
              Advanced Filters
            </Button>
          </div>
        </div>
      </div>

      {/* Notifications List */}
      <div className="bg-white rounded-lg shadow divide-y">
        {notifications.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <BellOff className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p>No notifications found</p>
          </div>
        ) : (
          notifications.map((notification: any) => (
            <div
              key={notification.id}
              className={`p-4 hover:bg-gray-50 transition-colors cursor-pointer ${
                !notification.is_read ? 'bg-blue-50' : ''
              }`}
              onClick={() => handleNotificationClick(notification)}
            >
              <div className="flex items-start gap-4">
                {/* Icon */}
                <div className="flex-shrink-0">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
                      !notification.is_read ? 'bg-blue-100' : 'bg-gray-100'
                    }`}
                  >
                    {typeIcons[notification.type] || '📬'}
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <h3
                        className={`text-sm font-medium ${
                          !notification.is_read ? 'text-gray-900' : 'text-gray-700'
                        }`}
                      >
                        {notification.title}
                      </h3>
                      {!notification.is_read && (
                        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={priorityColors[notification.priority] || 'default'}>
                        {notification.priority}
                      </Badge>
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        {getTimeAgo(notification.created_at)}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                </div>

                {/* Actions */}
                <div
                  className="flex-shrink-0 flex gap-2"
                  onClick={(e) => e.stopPropagation()}
                >
                  {!notification.is_read && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => markAsRead(notification.id)}
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => deleteNotification(notification.id)}
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </Button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Notifications</p>
          <p className="text-2xl font-bold text-gray-900">{notifications.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Unread</p>
          <p className="text-2xl font-bold text-blue-600">{unreadCount}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">High Priority</p>
          <p className="text-2xl font-bold text-red-600">
            {notifications.filter((n: any) => n.priority === 'high' || n.priority === 'urgent').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 flex flex-col justify-between">
           <div>
              <p className="text-sm text-gray-600">System Actions</p>
              <p className="text-xs text-gray-500 mt-1">Force check for updates</p>
           </div>
           <Button 
            size="sm" 
            variant="outline" 
            className="w-full mt-2"
            onClick={async () => {
                const toastId = toast.loading('Running system checks...');
                try {
                    const res = await apiClient.triggerNotificationChecks();
                    toast.success(`Checks complete. Found ${res.itineraries_found} trips.`, { id: toastId });
                    window.location.reload(); // Simple reload to refresh data
                } catch (e) {
                    toast.error('Failed to run checks', { id: toastId });
                }
            }}
           >
             Run System Checks
           </Button>
        </div>
      </div>
    </div>
  );
}
