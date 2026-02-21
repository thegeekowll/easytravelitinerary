'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Plus, Search, Building, MapPin, Star, Pencil, Trash2, Settings } from 'lucide-react';
import AccommodationForm from '@/components/accommodations/accommodation-form';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useAuth } from '@/lib/hooks/useAuth';


import AttributeManager from '@/components/accommodations/attribute-manager';
import Image from 'next/image';

export default function AccommodationsPage() {
  const { user, hasPermission } = useAuth();
  const isAdmin = user?.role === 'admin';
  const canAdd = isAdmin || hasPermission('add_accommodation');
  const canEdit = isAdmin || hasPermission('edit_accommodation');
  const canDelete = isAdmin || hasPermission('delete_accommodation');
  const canManageSettings = isAdmin || hasPermission('manage_accommodation_types');

  const [accommodations, setAccommodations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isAttributesOpen, setIsAttributesOpen] = useState(false);
  const [editingAccommodation, setEditingAccommodation] = useState<any>(null);
  
  // Data for attribute manager
  const [types, setTypes] = useState<any[]>([]);
  const [levels, setLevels] = useState<any[]>([]);

  const fetchAccommodations = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getAccommodations();
      setAccommodations(data.items || []);
    } catch (error) {
      console.error('Failed to fetch accommodations:', error);
      toast.error('Failed to load accommodations');
    } finally {
      setLoading(false);
    }
  };

  const fetchAttributes = async () => {
      try {
          const [typeData, levelData] = await Promise.all([
              apiClient.getAccommodationTypes(),
              apiClient.getAccommodationLevels()
          ]);
          setTypes(typeData || []);
          setLevels(levelData || []);
      } catch (error) {
          console.error(error);
      }
  };

  useEffect(() => {
    fetchAccommodations();
    fetchAttributes();
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this accommodation?')) return;
    try {
      await apiClient.deleteAccommodation(id);
      toast.success('Accommodation deleted');
      fetchAccommodations();
    } catch (error) {
      toast.error('Failed to delete accommodation');
    }
  };

  const filteredAccommodations = accommodations.filter(acc => 
    acc.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Accommodations</h1>
          <p className="text-gray-600">Manage hotels, lodges, and camps</p>
        </div>
        
        <div className="flex gap-2">
            {canManageSettings && (
                <Dialog open={isAttributesOpen} onOpenChange={setIsAttributesOpen}>
                    <DialogTrigger asChild>
                        <Button variant="outline" onClick={fetchAttributes}>
                            <Settings className="h-4 w-4 mr-2" />
                            Manage Settings
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                        <DialogHeader>
                            <DialogTitle>Accommodation Settings</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-6">
                            <AttributeManager 
                                title="Accommodation Type" 
                                items={types}
                                onCreate={apiClient.createAccommodationType.bind(apiClient)}
                                onDelete={() => Promise.resolve()} // Deletion not implemented for types yet in updated schema
                                onRefresh={fetchAttributes}
                            />
                            <div className="border-t pt-6"></div>
                            <AttributeManager 
                                title="Accommodation Level" 
                                items={levels}
                                onCreate={apiClient.createAccommodationLevel.bind(apiClient)}
                                onDelete={apiClient.deleteAccommodationLevel.bind(apiClient)}
                                onRefresh={fetchAttributes}
                            />
                        </div>
                    </DialogContent>
                </Dialog>
            )}

            {canAdd && (
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                    <Button onClick={() => setEditingAccommodation(null)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Accommodation
                    </Button>
                </DialogTrigger>
                <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                    <DialogTitle>{editingAccommodation ? 'Edit Accommodation' : 'Add New Accommodation'}</DialogTitle>
                    </DialogHeader>
                    <AccommodationForm 
                        initialData={editingAccommodation || undefined}
                        onSuccess={() => {
                            setIsDialogOpen(false);
                            fetchAccommodations();
                        }}
                    />
                </DialogContent>
                </Dialog>
            )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            placeholder="Search accommodations..."
            className="pl-9"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <p>Loading accommodations...</p>
        ) : filteredAccommodations.length > 0 ? (
          filteredAccommodations.map((acc) => (
            <Card key={acc.id} className="overflow-hidden hover:shadow-md transition-shadow group">
               <div className="h-48 bg-gray-200 relative">
                  {acc.images && acc.images.length > 0 ? (
                      <Image 
                        src={acc.images[0].image_url} 
                        alt={acc.name} 
                        fill 
                        className="object-cover"
                      />
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-400">
                        <Building className="h-12 w-12" />
                    </div>
                  )}
                  {/* Actions Overlay */}
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    {canEdit && (
                        <Button variant="secondary" size="sm" onClick={() => {
                            setEditingAccommodation(acc);
                            setIsDialogOpen(true);
                        }}>
                            <Pencil className="h-4 w-4 mr-1" /> Edit
                        </Button>
                    )}
                    {canDelete && (
                        <Button variant="destructive" size="sm" onClick={() => handleDelete(acc.id)}>
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    )}
                  </div>
              </div>
              <CardContent className="pt-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-lg line-clamp-1">{acc.name}</h3>
                   <div className="flex items-center gap-1 text-yellow-500">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="text-sm font-medium">{acc.star_rating || 4}</span>
                   </div>
                </div>
                
                <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                   <MapPin className="h-4 w-4" />
                   <span>{acc.location_destination?.name || 'Unknown Location'}</span>
                </div>
                
                 <div className="flex items-center gap-2 text-sm text-gray-600 mt-2">
                  <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded text-xs">
                    {acc.accommodation_type?.name || 'Lodge'}
                  </span>
                  {acc.accommodation_level && (
                      <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs border border-blue-100">
                        {acc.accommodation_level.name}
                      </span>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
            <div className="bg-gray-100 p-4 rounded-full mb-4">
              <Building className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">No accommodations found</h3>
            <p className="text-gray-500 mt-1 max-w-sm">
              Add your first hotel, lodge, or camp.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
