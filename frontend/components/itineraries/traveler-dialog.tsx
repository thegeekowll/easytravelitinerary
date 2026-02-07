'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/lib/api/client';

interface TravelerDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (traveler: any) => void;
  itineraryId: string;
  travelerToEdit?: any; // If null, means adding new
  defaultNationality?: string;
}

export default function TravelerDialog({
  isOpen,
  onClose,
  onSuccess,
  itineraryId,
  travelerToEdit,
  defaultNationality,
}: TravelerDialogProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    age: '',
    nationality: '',
    special_requests: '',
    is_primary: false,
  });

  useEffect(() => {
    if (travelerToEdit) {
      // Split full name if necessary or use fields if backend separates them
      // Backend Traveler model has full_name. Logic in backend endpoints tries to use first/last if provided, but stores full_name.
      // We will ask for First/Last in UI and combine for full_name if needed, or just editing full_name?
      // Better to stick to what the form usually expects. Let's provide First/Last inputs and construct full_name.
      
      const names = (travelerToEdit.full_name || '').split(' ');
      const firstName = names[0] || '';
      const lastName = names.slice(1).join(' ') || '';

      setFormData({
        first_name: firstName,
        last_name: lastName,
        email: travelerToEdit.email || '',
        phone: travelerToEdit.phone || '',
        age: travelerToEdit.age?.toString() || '',
        nationality: travelerToEdit.nationality || '',
        special_requests: travelerToEdit.special_requests || '',
        is_primary: travelerToEdit.is_primary || false,
      });
    } else {
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        age: '',
        nationality: defaultNationality || '',
        special_requests: '',
        is_primary: false,
      });
    }
  }, [travelerToEdit, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        full_name: `${formData.first_name} ${formData.last_name}`.trim(),
        age: formData.age ? parseInt(formData.age) : null,
        email: formData.email || null,
        phone: formData.phone || null,
        nationality: formData.nationality || null,
        special_requests: formData.special_requests || null,
        itinerary_id: itineraryId
      };

      let result;
      if (travelerToEdit) {
        result = await apiClient.updateTraveler(itineraryId, travelerToEdit.id, payload);
        toast.success("Traveler updated successfully");
      } else {
        result = await apiClient.addTraveler(itineraryId, payload);
        toast.success("Traveler added successfully");
      }

      onSuccess(result);
      onClose();
    } catch (error: any) {
      console.error('Failed to save traveler:', error);
      let msg = "Failed to save traveler";
      if (error.response?.data?.detail) {
          const detail = error.response.data.detail;
          if (Array.isArray(detail)) {
              msg = detail.map((e: any) => e.msg).join(', ');
          } else if (typeof detail === 'object') {
              msg = JSON.stringify(detail);
          } else {
              msg = String(detail);
          }
      }
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{travelerToEdit ? 'Edit Traveler' : 'Add Traveler'}</DialogTitle>
          <DialogDescription>
            {travelerToEdit ? 'Update traveler details below.' : 'Add a new traveler to this itinerary.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="first_name">First Name</Label>
                <Input
                  id="first_name"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                />
              </div>
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="age">Age</Label>
                  <Input
                    id="age"
                    type="number"
                    value={formData.age}
                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  />
                </div>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="nationality">Nationality</Label>
              <Input
                id="nationality"
                value={formData.nationality}
                onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="special_requests">Special Requests / Dietary</Label>
              <Textarea
                id="special_requests"
                value={formData.special_requests}
                onChange={(e) => setFormData({ ...formData, special_requests: e.target.value })}
                placeholder="Vegetarian, Allergies, Accessibility needs..."
              />
            </div>

            <div className="flex items-center space-x-2">
                <Checkbox 
                    id="is_primary" 
                    checked={formData.is_primary}
                    onCheckedChange={(checked: boolean) => setFormData({ ...formData, is_primary: checked })}
                />
                <Label htmlFor="is_primary">Set as Primary Contact</Label>
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Traveler
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
