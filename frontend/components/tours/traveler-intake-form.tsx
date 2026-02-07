'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Plus, Trash2 } from 'lucide-react';

export interface TravelerIntakeData {
  primaryName: string;
  primaryEmail: string;
  primaryPhone: string;
  primaryAge: string;
  primaryCountry: string;
  arrivalDate: string;
  numberOfDays: number;
  numberOfTravelers: number;
  otherTravelers: { name: string; age: string }[];
}

interface TravelerIntakeFormProps {
  onSubmit: (data: TravelerIntakeData) => void;
}

export default function TravelerIntakeForm({ onSubmit }: TravelerIntakeFormProps) {
  const [formData, setFormData] = useState<TravelerIntakeData>({
    primaryName: '',
    primaryEmail: '',
    primaryPhone: '',
    primaryAge: '',
    primaryCountry: '',
    arrivalDate: '',
    numberOfDays: 3,
    numberOfTravelers: 1,
    otherTravelers: []
  });

  const updateField = (field: keyof TravelerIntakeData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const updateOtherTraveler = (index: number, field: 'name' | 'age', value: string) => {
    const updated = [...formData.otherTravelers];
    updated[index] = { ...updated[index], [field]: value };
    setFormData(prev => ({ ...prev, otherTravelers: updated }));
  };

  const addTraveler = () => {
    setFormData(prev => ({
      ...prev,
      otherTravelers: [...prev.otherTravelers, { name: '', age: '' }],
      numberOfTravelers: prev.numberOfTravelers + 1
    }));
  };

  const removeTraveler = (index: number) => {
    const updated = formData.otherTravelers.filter((_, i) => i !== index);
    setFormData(prev => ({
      ...prev,
      otherTravelers: updated,
      numberOfTravelers: prev.numberOfTravelers - 1
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label>Primary Traveler Name</Label>
          <Input 
            required
            value={formData.primaryName}
            onChange={e => updateField('primaryName', e.target.value)}
            placeholder="John Doe"
          />
        </div>
        <div className="space-y-2">
          <Label>Email Address</Label>
          <Input 
            type="email"
            value={formData.primaryEmail}
            onChange={e => updateField('primaryEmail', e.target.value)}
            placeholder="email@example.com"
          />
        </div>
        <div className="space-y-2">
          <Label>Phone Number</Label>
          <Input 
            type="tel"
            value={formData.primaryPhone}
            onChange={e => updateField('primaryPhone', e.target.value)}
            placeholder="+1 (555) 000-0000"
          />
        </div>
        <div className="space-y-2">
          <Label>Age</Label>
          <Input 
            required
            type="number"
            value={formData.primaryAge}
            onChange={e => updateField('primaryAge', e.target.value)}
            placeholder="30"
          />
        </div>
        <div className="space-y-2">
          <Label>Country / Nationality</Label>
          <Input 
            required
            value={formData.primaryCountry}
            onChange={e => updateField('primaryCountry', e.target.value)}
            placeholder="USA"
          />
        </div>
        <div className="space-y-2">
          <Label>Date of Arrival</Label>
          <Input 
            required
            type="date"
            value={formData.arrivalDate}
            onChange={e => updateField('arrivalDate', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label>Tour Duration (Days)</Label>
          <Input 
            required
            type="number"
            min={1}
            value={formData.numberOfDays}
            onChange={e => updateField('numberOfDays', parseInt(e.target.value) || 1)}
          />
        </div>
        <div className="space-y-2">
          <Label>Total Travelers</Label>
          <Input 
            type="number"
            readOnly
            value={formData.numberOfTravelers}
            className="bg-gray-50"
          />
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
            <Label className="text-lg">Other Travelers</Label>
            <Button type="button" variant="outline" size="sm" onClick={addTraveler}>
                <Plus className="h-4 w-4 mr-2" /> Add 
            </Button>
        </div>
        
        {formData.otherTravelers.map((traveler, index) => (
            <Card key={index}>
                <CardContent className="pt-6 flex gap-4 items-end">
                    <div className="flex-1 space-y-2">
                        <Label>Name</Label>
                        <Input 
                            value={traveler.name}
                            onChange={e => updateOtherTraveler(index, 'name', e.target.value)}
                            placeholder="Traveler Name"
                        />
                    </div>
                    <div className="w-24 space-y-2">
                        <Label>Age</Label>
                        <Input 
                            value={traveler.age}
                            onChange={e => updateOtherTraveler(index, 'age', e.target.value)}
                            placeholder="Age"
                        />
                    </div>
                    <Button type="button" variant="ghost" size="icon" onClick={() => removeTraveler(index)} className="text-red-500">
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </CardContent>
            </Card>
        ))}
      </div>

      <Button type="submit" size="lg" className="w-full">Continue to Tour Selection</Button>
    </form>
  );
}
