'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Plus, Search, Map, Download, Upload as UploadIcon } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { useAuth } from '@/lib/hooks/useAuth';

export default function ToursPage() {
  const { user, hasPermission } = useAuth();
  const isAdmin = user?.role === 'admin';
  const canAdd = isAdmin || hasPermission('add_tour_package');
  const canEdit = isAdmin || hasPermission('edit_tour_package');

  const [tours, setTours] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchTours = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getBaseTours();
      setTours(data.items || []);
    } catch (error) {
      console.error('Failed to fetch tours:', error);
      toast.error('Failed to load tours');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTours();
  }, []);

  const handleExport = async () => {
    try {
      const blob = await apiClient.exportData('base-tours');
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'base_tours.csv');
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      toast.error('Export failed');
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const toastId = toast.loading('Importing tours...');
    try {
      const result = await apiClient.importData('base-tours', file);
      toast.success(`Imported ${result.imported_count} tours. Failed: ${result.failed_count}`, { id: toastId });
      fetchTours();
    } catch (error) {
      toast.error('Import failed', { id: toastId });
    }
    e.target.value = '';
  };

  const filteredTours = tours.filter(tour => 
    tour.tour_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tour.tour_code?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Base Tours</h1>
          <p className="text-gray-600">Manage tour templates and packages</p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            CSV Ex
          </Button>
          <div>
            <input type="file" id="import-tours" accept=".csv" className="hidden" onChange={handleImport} />
            <Button variant="outline" onClick={() => document.getElementById('import-tours')?.click()}>
              <UploadIcon className="h-4 w-4 mr-2" />
              CSV Im
            </Button>
          </div>
          {canAdd && (
            <Link href="/admin/tours/create">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Tour
              </Button>
            </Link>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            placeholder="Search tours..."
            className="pl-9"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <p>Loading tours...</p>
        ) : filteredTours.length > 0 ? (
          filteredTours.map((tour) => (
            <Card key={tour.id} className="overflow-hidden hover:shadow-md transition-shadow">
              <div className="h-48 bg-gray-200 relative">
                {tour.hero_image_url ? (
                  <img 
                    src={tour.hero_image_url} 
                    alt={tour.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <Map className="h-12 w-12" />
                  </div>
                )}
                <div className="absolute top-2 right-2">
                  <Badge variant="secondary" className="bg-white/90 backdrop-blur-sm">
                    {tour.number_of_days} Days
                  </Badge>
                </div>
              </div>
              <CardContent className="pt-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-lg line-clamp-1">{tour.tour_name}</h3>
                    <p className="text-sm text-gray-500">{tour.tour_code || 'No Code'}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 text-sm text-gray-600 mt-2">
                  <span className="bg-primary/10 text-primary px-2 py-0.5 rounded text-xs px-2">
                    {tour.tour_type || 'Safari'}
                  </span>
                </div>
                
                {canEdit && (
                  <div className="mt-4 flex gap-2">
                    <Button variant="outline" size="sm" className="w-full" asChild>
                      <Link href={`/admin/tours/${tour.id}`}>Edit</Link>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
            <div className="bg-gray-100 p-4 rounded-full mb-4">
              <Map className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">No tours found</h3>
            <p className="text-gray-500 mt-1 max-w-sm">
              Get started by creating your first base tour template.
            </p>
            {canAdd && (
              <Button className="mt-4" asChild>
                <Link href="/admin/tours/create">Create Tour</Link>
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
