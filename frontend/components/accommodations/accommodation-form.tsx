'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Loader2 } from 'lucide-react';

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
            <Label htmlFor="type">Type</Label>
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
            <Label htmlFor="level">Level</Label>
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
        <Label htmlFor="location">Location</Label>
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
