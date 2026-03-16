
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

export const useNotifications = (
    filters?: { 
        type?: string; 
        status?: string; // 'all' | 'read' | 'unread'
    }
) => {
    const queryClient = useQueryClient();
    const [page, setPage] = useState(1);

    // Prepare params for API
    const apiParams: any = { page, limit: 10 };
    
    if (filters?.type && filters.type !== 'all') {
        apiParams.notification_type = filters.type;
    }
    
    if (filters?.status) {
        if (filters.status === 'read') apiParams.is_read = true;
        if (filters.status === 'unread') apiParams.is_read = false;
        // if 'all', we don't send is_read param
    }

    // Fetch Notifications List
    const { data: notificationsData, isLoading } = useQuery({
        queryKey: ['notifications', page, filters?.type, filters?.status],
        queryFn: () => apiClient.getNotifications(apiParams),
        refetchInterval: 30000, 
    });

    // Fetch Unread Count
    const { data: unreadData } = useQuery({
        queryKey: ['notifications-unread'],
        queryFn: () => apiClient.getUnreadCount(),
        refetchInterval: 15000,
    });

    // Mutations
    const markReadMutation = useMutation({
        mutationFn: (id: string) => apiClient.markNotificationRead(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['notifications-unread'] });
        }
    });

    const markAllReadMutation = useMutation({
        mutationFn: () => apiClient.markAllNotificationsRead(),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['notifications-unread'] });
            toast.success('All notifications marked as read');
        }
    });

    const deleteMutation = useMutation({
        mutationFn: (id: string) => apiClient.deleteNotification(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['notifications-unread'] });
            toast.success('Notification deleted');
        }
    });

    return {
        notifications: notificationsData?.items || [],
        total: notificationsData?.total || 0,
        unreadCount: unreadData?.unread_count || 0,
        isLoading,
        page,
        setPage,
        totalPages: notificationsData?.total_pages || 1,
        markAsRead: markReadMutation.mutate,
        markAllAsRead: markAllReadMutation.mutate,
        deleteNotification: deleteMutation.mutate,
    };
};
