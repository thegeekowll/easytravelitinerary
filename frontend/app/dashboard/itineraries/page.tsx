'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Plus, Search, Filter, Trash2, Loader2, Eye } from 'lucide-react';
import { deleteItinerary, Itinerary } from '@/lib/api';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

const statusColors: Record<string, 'default' | 'warning' | 'success' | 'info' | 'destructive' | 'secondary' | 'purple'> = {
  draft: 'secondary',
  confirmed: 'info',
  sent: 'purple',
  under_review: 'warning',
  completed: 'success',
  cancelled: 'destructive',
};

const paymentStatusColors: Record<string, 'default' | 'warning' | 'success' | 'destructive'> = {
  not_paid: 'destructive',
  partially_paid: 'warning',
  fully_paid: 'success',
  custom: 'default',
};

export default function ItinerariesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [paymentFilter, setPaymentFilter] = useState('all');
  
  // Advanced Filters
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [creatorFilter, setCreatorFilter] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [createdFrom, setCreatedFrom] = useState('');
  const [createdTo, setCreatedTo] = useState('');

  // Fetch Agents for Filter
  const { data: agents = [] } = useQuery({
      queryKey: ['agents'],
      queryFn: () => apiClient.getAgents().then(data => data.items || data), // Handle pagination or list
      staleTime: 5 * 60 * 1000 // Cache for 5 mins
  });

  // Fetch Itineraries
  const { data: itinerariesData, isLoading, isError } = useQuery({
    queryKey: ['itineraries', statusFilter, searchQuery, creatorFilter, dateFrom, dateTo, createdFrom, createdTo],
    queryFn: () => apiClient.getItineraries({
        search: searchQuery || undefined,
        status_filter: statusFilter !== 'all' ? statusFilter : undefined,
        creator_id: creatorFilter !== 'all' ? creatorFilter : undefined,
        departure_date_from: dateFrom || undefined,
        departure_date_to: dateTo || undefined,
        created_at_from: createdFrom || undefined,
        created_at_to: createdTo || undefined,
    }),
  });
  
  const itineraries = itinerariesData?.items || [];

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: deleteItinerary,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['itineraries'] });
      toast.success('Itinerary deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete itinerary');
    },
  });

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this itinerary?')) {
      deleteMutation.mutate(id);
    }
  };



  // Client-side filtering for payment status only (since backend doesn't support it yet)
  const filteredItineraries = (itineraries as Itinerary[]).filter((itinerary) => {
     const matchesPayment = paymentFilter === 'all' || itinerary.payment_status === paymentFilter;
     return matchesPayment;
  });

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Itineraries</h1>
          <p className="text-gray-600 mt-1">
            Manage all travel itineraries and bookings
          </p>
        </div>
        <Link href="/create-tour">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Create Itinerary
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              {Object.keys(statusColors).map(status => (
                  <option key={status} value={status}>{status.replace('_', ' ').toUpperCase()}</option>
              ))}
            </Select>

            <Select
              value={paymentFilter}
              onChange={(e) => setPaymentFilter(e.target.value)}
            >
              <option value="all">All Payments</option>
              {Object.keys(paymentStatusColors).map(status => (
                  <option key={status} value={status}>{status.replace('_', ' ').toUpperCase()}</option>
              ))}
            </Select>

             <Button 
                variant={showAdvancedFilters ? "secondary" : "outline"}
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            >
                <Filter className="h-4 w-4 mr-2" />
                {showAdvancedFilters ? 'Hide Filters' : 'More Filters'}
            </Button>
          </div>

          {showAdvancedFilters && (
               <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
                  <div>
                      <label className="text-sm font-medium text-gray-700 mb-1 block">Created By</label>
                      <Select
                          value={creatorFilter}
                          onChange={(e) => setCreatorFilter(e.target.value)}
                      >
                          <option value="all">All Agents</option>
                          {agents.map((agent: any) => (
                              <option key={agent.id} value={agent.id}>{agent.full_name}</option>
                          ))}
                      </Select>
                  </div>
                  <div>
                      <label className="text-sm font-medium text-gray-700 mb-1 block">Departure Date (From/To)</label>
                      <div className="flex gap-2">
                        <Input 
                            type="date"
                            value={dateFrom}
                            onChange={(e) => setDateFrom(e.target.value)}
                        />
                        <Input 
                            type="date"
                            value={dateTo}
                            onChange={(e) => setDateTo(e.target.value)}
                        />
                      </div>
                  </div>
                   <div>
                      <label className="text-sm font-medium text-gray-700 mb-1 block">Created Date (From/To)</label>
                      <div className="flex gap-2">
                        <Input 
                            type="date"
                            value={createdFrom}
                            onChange={(e) => setCreatedFrom(e.target.value)}
                        />
                        <Input 
                            type="date"
                            value={createdTo}
                            onChange={(e) => setCreatedTo(e.target.value)}
                        />
                      </div>
                  </div>
               </div>
          )}
        </div>
      </div>

      {/* Itineraries Table */}
      <div className="bg-white rounded-lg shadow">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Reference</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Customer</TableHead>
              <TableHead>Source</TableHead>
              <TableHead>Dates</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Payment</TableHead>
              <TableHead>Total</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
               <TableRow>
                <TableCell colSpan={10} className="text-center py-8">
                  <div className="flex justify-center items-center">
                    <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                    <span className="ml-2 text-gray-500">Loading itineraries...</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={10} className="text-center py-8 text-red-500">
                  Failed to load itineraries
                </TableCell>
              </TableRow>
            ) : filteredItineraries.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} className="text-center py-8 text-gray-500">
                  No itineraries found
                </TableCell>
              </TableRow>
            ) : (
              filteredItineraries.map((itinerary) => (
                <TableRow
                  key={itinerary.id}
                  className="cursor-pointer hover:bg-gray-50"
                  onClick={() => router.push(`/dashboard/itineraries/${itinerary.id}`)}
                >
                  <TableCell className="font-medium">
                    {itinerary.unique_code}
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="font-medium text-gray-900">{itinerary.tour_title}</p>
                      <p className="text-xs text-gray-500">by {itinerary.created_by_name || 'Unknown'}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="text-gray-900">{itinerary.client_name || 'Guest'}</p>
                      <p className="text-xs text-gray-500">{itinerary.client_email || ''}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                       {itinerary.creation_method === 'custom' && (
                         <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50">Custom Build</Badge>
                       )}
                       {itinerary.creation_method === 'choose_existing' && (
                         <div>
                           <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">Base Tour</Badge>
                           <p className="text-xs text-gray-500 mt-1 truncate max-w-[150px]" title={itinerary.base_tour_title}>
                             {itinerary.base_tour_title || 'Unknown Tour'}
                           </p>
                         </div>
                       )}
                       {itinerary.creation_method === 'edit_existing' && (
                         <div>
                           <Badge variant="outline" className="text-purple-600 border-purple-200 bg-purple-50">Customized</Badge>
                           <p className="text-xs text-gray-500 mt-1 truncate max-w-[150px]" title={itinerary.base_tour_title}>
                             {itinerary.base_tour_title || 'Unknown Tour'}
                           </p>
                         </div>
                       )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <p>{new Date(itinerary.departure_date).toLocaleDateString()}</p>
                      <p className="text-gray-500">to {new Date(itinerary.return_date).toLocaleDateString()}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    {itinerary.duration_days}D / {itinerary.duration_nights}N
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusColors[itinerary.status] || 'default'}>
                      {itinerary.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                   <Badge variant={paymentStatusColors[itinerary.payment_status || 'not_paid'] || 'default'}>
                      {itinerary.payment_status || 'not_paid'}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-semibold">
                    {itinerary.total_price ? `$${itinerary.total_price.toLocaleString()}` : '-'}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                       <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(`/view/${itinerary.unique_code}`, '_blank');
                        }}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={(e) => handleDelete(itinerary.id, e)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Itineraries</p>
          <p className="text-2xl font-bold text-gray-900">{filteredItineraries.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Confirmed</p>
          <p className="text-2xl font-bold text-green-600">
            {filteredItineraries.filter((i) => i.status === 'confirmed').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Drafts</p>
          <p className="text-2xl font-bold text-yellow-600">
            {filteredItineraries.filter((i) => i.status === 'draft').length}
          </p>
        </div>
        {/* Revenue can be added if totals are sum-able */}
      </div>
    </div>
  );
}
