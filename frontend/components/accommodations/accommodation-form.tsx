'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Loader2, Plus } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

import ImageUpload from '@/components/shared/image-upload';

interface AccommodationFormProps {
  initialData?: any;
  onSuccess: () => void;
}

export default function AccommodationForm({ initialData, onSuccess }: AccommodationFormProps) {
  const [loading, setLoading] = useState(false);
  const [destinations, setDestinations] = useState<any[]>([]);
  const [types, setTypes] = useState<any[]>([]);
  const [levels, setLevels] = useState<any[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  
  // Inline creation states
  const [isTypeDialogOpen, setIsTypeDialogOpen] = useState(false);
  const [isLevelDialogOpen, setIsLevelDialogOpen] = useState(false);
  const [isLocationDialogOpen, setIsLocationDialogOpen] = useState(false);
  const [newType, setNewType] = useState({ name: '', description: '' });
  const [newLevel, setNewLevel] = useState({ name: '', description: '' });
  const [newLocation, setNewLocation] = useState({ name: '', country: '' });
  const [creatingInline, setCreatingInline] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    location_destination_id: '',
    type_id: '',
    level_id: '',
    star_rating: 4,
    ...initialData
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [destRes, typeRes, levelRes] = await Promise.all([
          apiClient.getDestinations({ limit: 100 }), // Get first 100 for now
          apiClient.getAccommodationTypes(),
          apiClient.getAccommodationLevels()
        ]);
        setDestinations(destRes.items || []);
        setTypes(typeRes || []);
        setLevels(levelRes || []);
      } catch (error) {
        console.error('Failed to load form data:', error);
        toast.error('Failed to load form options');
      }
    };
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        level_id: formData.level_id || null, // Convert empty string to null for UUID validation
      };

      let newAccommodation;
      if (initialData?.id) {
        await apiClient.updateAccommodation(initialData.id, payload);
        newAccommodation = { id: initialData.id };
        toast.success('Accommodation updated successfully');
      } else {
        newAccommodation = await apiClient.createAccommodation(payload);
        toast.success('Accommodation created successfully');
      }

      // Upload images if allowed
      if (selectedFiles.length > 0 && newAccommodation?.id) {
         try {
             await apiClient.uploadAccommodationImages(newAccommodation.id, selectedFiles);
         } catch (uploadError) {
             console.error("Image upload failed", uploadError);
             toast.error("Accommodation created, but image upload failed");
         }
      }

      onSuccess();
    } catch (error: any) {
      console.error('Submit failed:', error);
      const errorMsg = error.response?.data?.detail;
      if (typeof errorMsg === 'string') {
        toast.error(errorMsg);
      } else if (Array.isArray(errorMsg)) {
        // Handle Pydantic validation errors (array of objects)
        toast.error(errorMsg.map(e => e.msg).join(', '));
      } else if (typeof errorMsg === 'object') {
        toast.error(JSON.stringify(errorMsg));
      } else {
        toast.error('Operation failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateType = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingInline(true);
    try {
      const created = await apiClient.createAccommodationType(newType);
      setTypes([...types, created]);
      setFormData({ ...formData, type_id: created.id });
      setIsTypeDialogOpen(false);
      setNewType({ name: '', description: '' });
      toast.success('Type created');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create type');
    } finally {
      setCreatingInline(false);
    }
  };

  const handleCreateLevel = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingInline(true);
    try {
      const created = await apiClient.createAccommodationLevel(newLevel);
      setLevels([...levels, created]);
      setFormData({ ...formData, level_id: created.id });
      setIsLevelDialogOpen(false);
      setNewLevel({ name: '', description: '' });
      toast.success('Level created');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create level');
    } finally {
      setCreatingInline(false);
    }
  };

  const handleCreateLocation = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingInline(true);
    try {
      const payload = {
         name: newLocation.name,
         country: newLocation.country,
         description: ''
      };
      const created = await apiClient.createDestination(payload);
      setDestinations([...destinations, created]);
      setFormData({ ...formData, location_destination_id: created.id });
      setIsLocationDialogOpen(false);
      setNewLocation({ name: '', country: '' });
      toast.success('Location created');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create location');
    } finally {
      setCreatingInline(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="space-y-2">
        <Label htmlFor="name">Accommodation Name</Label>
        <Input 
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          placeholder="e.g. Serengeti Safari Lodge"
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="type">Type</Label>
              <Dialog open={isTypeDialogOpen} onOpenChange={setIsTypeDialogOpen}>
                  <DialogTrigger asChild>
                      <Button type="button" variant="ghost" size="sm" className="h-4 p-0 px-2 text-xs text-blue-600">
                          <Plus className="h-3 w-3 mr-1" /> Add New
                      </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-sm">
                      <DialogHeader><DialogTitle>Add Accommodation Type</DialogTitle></DialogHeader>
                      <div className="space-y-4 pt-4">
                          <div className="space-y-2">
                              <Label>Name</Label>
                              <Input value={newType.name} onChange={e => setNewType({...newType, name: e.target.value})} placeholder="e.g. Resort" />
                          </div>
                          <div className="space-y-2">
                              <Label>Description (Optional)</Label>
                              <Input value={newType.description} onChange={e => setNewType({...newType, description: e.target.value})} />
                          </div>
                          <Button type="button" onClick={handleCreateType} disabled={creatingInline || !newType.name} className="w-full">
                              {creatingInline ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Create Type'}
                          </Button>
                      </div>
                  </DialogContent>
              </Dialog>
            </div>
            <Select 
                value={formData.type_id} 
                onChange={(e) => setFormData({...formData, type_id: e.target.value})}
                required
            >
                <option value="">Select type</option>
                {types.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                ))}
            </Select>
        </div>

        <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="level">Level</Label>
              <Dialog open={isLevelDialogOpen} onOpenChange={setIsLevelDialogOpen}>
                  <DialogTrigger asChild>
                      <Button type="button" variant="ghost" size="sm" className="h-4 p-0 px-2 text-xs text-blue-600">
                          <Plus className="h-3 w-3 mr-1" /> Add New
                      </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-sm">
                      <DialogHeader><DialogTitle>Add Accommodation Level</DialogTitle></DialogHeader>
                      <div className="space-y-4 pt-4">
                          <div className="space-y-2">
                              <Label>Name</Label>
                              <Input value={newLevel.name} onChange={e => setNewLevel({...newLevel, name: e.target.value})} placeholder="e.g. Luxury" />
                          </div>
                          <div className="space-y-2">
                              <Label>Description (Optional)</Label>
                              <Input value={newLevel.description} onChange={e => setNewLevel({...newLevel, description: e.target.value})} />
                          </div>
                          <Button type="button" onClick={handleCreateLevel} disabled={creatingInline || !newLevel.name} className="w-full">
                              {creatingInline ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Create Level'}
                          </Button>
                      </div>
                  </DialogContent>
              </Dialog>
            </div>
            <Select 
                value={formData.level_id} 
                onChange={(e) => setFormData({...formData, level_id: e.target.value})}
            >
                <option value="">Select level (optional)</option>
                {levels.map((l) => (
                    <option key={l.id} value={l.id}>{l.name}</option>
                ))}
            </Select>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="location">Location</Label>
          <Dialog open={isLocationDialogOpen} onOpenChange={setIsLocationDialogOpen}>
              <DialogTrigger asChild>
                  <Button type="button" variant="ghost" size="sm" className="h-4 p-0 px-2 text-xs text-blue-600">
                      <Plus className="h-3 w-3 mr-1" /> Add New
                  </Button>
              </DialogTrigger>
              <DialogContent className="max-w-sm">
                  <DialogHeader><DialogTitle>Add Location (Destination)</DialogTitle></DialogHeader>
                  <div className="space-y-4 pt-4">
                      <div className="space-y-2">
                          <Label>Name / City</Label>
                          <Input value={newLocation.name} onChange={e => setNewLocation({...newLocation, name: e.target.value})} placeholder="e.g. Serengeti National Park" />
                      </div>
                      <div className="space-y-2">
                          <Label>Country</Label>
                          <Input value={newLocation.country} onChange={e => setNewLocation({...newLocation, country: e.target.value})} placeholder="e.g. Tanzania" />
                      </div>
                      <Button type="button" onClick={handleCreateLocation} disabled={creatingInline || !newLocation.name || !newLocation.country} className="w-full">
                          {creatingInline ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Create Location'}
                      </Button>
                  </div>
              </DialogContent>
          </Dialog>
        </div>
        <Select 
            value={formData.location_destination_id} 
            onChange={(e) => setFormData({...formData, location_destination_id: e.target.value})}
            required
        >
            <option value="">Select location</option>
            {destinations.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
            ))}
        </Select>
      </div>

      <div className="space-y-2 border-t pt-4">
        <Label>Images</Label>
        <ImageUpload 
            onImagesSelected={setSelectedFiles}
            existingImages={initialData?.images || []}
            onDeleteExisting={async (id) => {
                if (confirm('Delete this image?')) {
                    await apiClient.deleteAccommodationImage(id);
                    onSuccess(); // Refresh parent to hide deleted image
                }
            }}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="stars">Star Rating (1-5)</Label>
         <Input 
          id="stars"
          type="number"
          min="1"
          max="5"
          value={formData.star_rating}
          onChange={(e) => setFormData({...formData, star_rating: parseInt(e.target.value)})}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea 
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            placeholder="Detailed description..."
            rows={4}
        />
      </div>

      <Button type="submit" className="w-full" disabled={loading}>
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {initialData?.id ? 'Update Accommodation' : 'Create Accommodation'}
      </Button>
    </form>
  );
}
