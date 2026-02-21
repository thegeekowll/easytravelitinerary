'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Search, Edit, Trash2, MapPin, Image as ImageIcon, X, Upload } from 'lucide-react';
import { createDestination, deleteDestination, getDestinations, updateDestination, uploadDestinationImages } from '@/lib/api';
import toast from 'react-hot-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/lib/hooks/useAuth';

export default function DestinationsPage() {
  const queryClient = useQueryClient();
  const { user, hasPermission } = useAuth();
  const isAdmin = user?.role === 'admin';
  const canAdd = isAdmin || hasPermission('add_destination');
  const canEdit = isAdmin || hasPermission('edit_destination');
  const canDelete = isAdmin || hasPermission('delete_destination');
  
  const [searchQuery, setSearchQuery] = useState('');
  const [countryFilter, setCountryFilter] = useState('all');
  
  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentId, setCurrentId] = useState<string | null>(null);
  
  // Form State
  const [formData, setFormData] = useState({
    name: '',
    country: '',
    region: '',
    description: '',
  });
  const [imageUrls, setImageUrls] = useState<string[]>(['']);

  // Fetch Destinations
  const { data: destinations = [], isLoading } = useQuery({
    queryKey: ['destinations'],
    queryFn: () => getDestinations(searchQuery || undefined),
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: any) => createDestination(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['destinations'] });
      toast.success('Destination created successfully');
      setShowModal(false);
      resetForm();
    },
    onError: (error: any) => {
      const detail = error.response?.data?.detail;
      const message = Array.isArray(detail) ? detail[0].msg : (detail || 'Failed to create destination');
      toast.error(message);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => updateDestination(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['destinations'] });
      toast.success('Destination updated successfully');
      setShowModal(false);
      resetForm();
    },
    onError: () => toast.error('Failed to update destination'),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDestination,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['destinations'] });
      toast.success('Destination deleted');
    },
    onError: (error: any) => {
      const detail = error.response?.data?.detail;
      const message = Array.isArray(detail) ? detail[0].msg : (detail || 'Failed to delete destination');
      toast.error(message);
    },
  });

  // Helpers
  const resetForm = () => {
    setFormData({ name: '', country: '', region: '', description: '' });
    setImageUrls(['']);
    setIsEditing(false);
    setCurrentId(null);
  };

  const handleEdit = (destination: any) => {
    setFormData({
      name: destination.name,
      country: destination.country,
      region: destination.region || '',
      description: destination.description || '',
    });
    // Populate images from destination object
    if (destination.images && destination.images.length > 0) {
        setImageUrls(destination.images.map((img: any) => img.image_url));
    } else {
        setImageUrls(['']);
    } 
    setCurrentId(destination.id);
    setIsEditing(true);
    setShowModal(true);
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this destination?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleSubmit = () => {
    // Filter empty image URLs safely
    const validImages = imageUrls.filter(url => url && typeof url === 'string' && url.trim() !== '');

    if (isEditing && currentId) {
      updateMutation.mutate({
        id: currentId,
        data: {
          ...formData,
          image_urls: validImages
        }
      });
    } else {
      createMutation.mutate({
        ...formData,
        image_urls: validImages
      });
    }
  };

  const handleImageChange = (index: number, value: string) => {
    const newUrls = [...imageUrls];
    newUrls[index] = value;
    setImageUrls(newUrls);
  };

  const addImageField = () => {
    setImageUrls([...imageUrls, '']);
  };

  const removeImageField = (index: number) => {
    const newUrls = imageUrls.filter((_, i) => i !== index);
    setImageUrls(newUrls.length ? newUrls : ['']);
  };

  // Derived state
  const countries = Array.from(new Set(destinations.map((d: any) => d.country).filter(Boolean)));
  const filteredDestinations = destinations.filter((destination: any) => {
    const matchesSearch =
      destination.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (destination.region || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCountry =
      countryFilter === 'all' || destination.country === countryFilter;
    return matchesSearch && matchesCountry;
  });

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Destinations</h1>
          <p className="text-gray-600 mt-1">
            Manage travel destinations and locations
          </p>
        </div>
        {canAdd && (
          <Button onClick={() => { resetForm(); setShowModal(true); }}>
            <Plus className="h-4 w-4 mr-2" />
            Add Destination
          </Button>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total Destinations</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{destinations.length}</p>
          </CardContent>
        </Card>
        <Card>
           <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Countries</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-blue-600">{countries.length}</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search destinations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <select
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={countryFilter}
            onChange={(e) => setCountryFilter(e.target.value)}
          >
            <option value="all">All Countries</option>
            {countries.map((country: string) => (
              <option key={country} value={country}>{country}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Destination</TableHead>
              <TableHead>Country</TableHead>
              <TableHead>Region</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
               <TableRow>
                <TableCell colSpan={4} className="text-center py-8">Loading...</TableCell>
              </TableRow>
            ) : filteredDestinations.length === 0 ? (
               <TableRow>
                <TableCell colSpan={4} className="text-center py-8 text-gray-500">No destinations found</TableCell>
              </TableRow>
            ) : (
              filteredDestinations.map((destination: any) => (
                <TableRow key={destination.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
                        {destination.images && destination.images.length > 0 ? (
                            <img src={destination.images[0].image_url} alt={destination.name} className="w-full h-full object-cover" />
                        ) : (
                            <ImageIcon className="h-6 w-6 text-gray-400" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{destination.name}</p>
                        <p className="text-xs text-gray-500 line-clamp-1">{destination.description}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{destination.country}</TableCell>
                  <TableCell>{destination.region || '-'}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      {canEdit && (
                        <Button size="sm" variant="ghost" onClick={() => handleEdit(destination)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                      )}
                      {canDelete && (
                        <Button size="sm" variant="ghost" onClick={() => handleDelete(destination.id)}>
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Modal */}
      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{isEditing ? 'Edit Destination' : 'Add New Destination'}</DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label>Name *</Label>
              <Input 
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="e.g. Serengeti National Park"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Country *</Label>
                <Input 
                  value={formData.country}
                  onChange={(e) => setFormData({...formData, country: e.target.value})}
                  placeholder="e.g. Tanzania"
                />
              </div>
              <div className="space-y-2">
                <Label>Region</Label>
                <Input 
                  value={formData.region}
                  onChange={(e) => setFormData({...formData, region: e.target.value})}
                  placeholder="e.g. Northern Circuit"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea 
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Describe this destination..."
                rows={3}
              />
            </div>

            {/* Image Gallery & Upload */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <Label>Destination Images</Label>
                <div className="flex gap-2">
                   <Input
                      type="file"
                      multiple
                      className="hidden"
                      id="image-upload"
                      accept="image/*"
                      onChange={async (e) => {
                        const files = e.target.files;
                        if (files && files.length > 0 && currentId) {
                           try {
                              const uploaded = await uploadDestinationImages(currentId, Array.from(files));
                              const newUrls = uploaded.map((img: any) => img.image_url);
                              setImageUrls([...imageUrls.filter(u => u), ...newUrls]);
                              toast.success('Images uploaded');
                           } catch (err) {
                              toast.error('Failed to upload images');
                           }
                        } else if (files && files.length > 0 && !currentId) {
                            toast.error('Please create the destination first before uploading files.');
                        }
                        // Reset input
                        e.target.value = '';
                      }}
                   />
                   <Button type="button" variant="outline" size="sm" onClick={() => document.getElementById('image-upload')?.click()}>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Images
                   </Button>
                   <Button type="button" variant="outline" size="sm" onClick={addImageField}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add URL
                   </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {imageUrls.map((url, index) => (
                    <div key={index} className="relative group border rounded-lg overflow-hidden h-32 bg-gray-100">
                        {url ? (
                            <img 
                                src={url} 
                                alt={`Destination ${index + 1}`} 
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                                <ImageIcon className="h-8 w-8" />
                            </div>
                        )}
                        
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                             <Button 
                                variant="destructive" 
                                size="icon" 
                                className="h-8 w-8"
                                onClick={() => removeImageField(index)}
                             >
                                <Trash2 className="h-4 w-4" />
                             </Button>
                        </div>
                        
                        {/* URL Edit (Optional, hidden by default but good for manual tweaks) */}
                        {!url && (
                             <div className="absolute bottom-0 left-0 right-0 p-2 bg-white">
                                <Input 
                                    value={url}
                                    onChange={(e) => handleImageChange(index, e.target.value)}
                                    placeholder="Enter URL..."
                                    className="h-8 text-xs"
                                />
                             </div>
                        )}
                    </div>
                ))}
              </div>
              
              {imageUrls.length === 0 && (
                  <div className="text-sm text-gray-500 text-center py-8 border-2 border-dashed rounded-lg">
                      No images added yet. Upload files or add URLs.
                  </div>
              )}
            </div>

          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button 
                onClick={handleSubmit} 
                disabled={createMutation.isPending || updateMutation.isPending}
            >
                {createMutation.isPending || updateMutation.isPending ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Destination')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
