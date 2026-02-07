'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Trash, Wand2, Plus, X, Check, Image as ImageIcon } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import ImageGalleryModal from '@/components/shared/image-gallery-modal';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Combobox } from '@/components/ui/combobox';
import { cn } from '@/lib/utils/cn';

interface DayEditorProps {
  day: any;
  index: number;
  destinations: any[];
  accommodations: any[];
  onChange: (updatedDay: any) => void;
  onRemove: () => void;
}

export default function DayEditor({ day, destinations, accommodations, onChange, onRemove }: DayEditorProps) {
  // Destination Selector Logic
  const [isDestOpen, setIsDestOpen] = useState(false);
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  
  // Create a map for fast lookup
  const destMap = new Map(destinations.map((d: any) => [d.id, d]));
  
  // Map IDs to objects to preserve order
  const selectedDestinations = (day.destination_ids || [])
    .map((id: string) => destMap.get(id))
    .filter((d: any) => d !== undefined);

  const toggleDestination = (destId: string) => {
    const currentIds = day.destination_ids || [];
    let newIds;
    if (currentIds.includes(destId)) {
      newIds = currentIds.filter((id: string) => id !== destId);
    } else {
      newIds = [...currentIds, destId];
    }
    onChange({ ...day, destination_ids: newIds });
  };

  const handleAutoFill = async () => {
    // Check if destinations are selected
    if (selectedDestinations.length === 0) return;

    const loadingToast = toast.loading('Fetching matrix content...');
    try {
        const destIds = selectedDestinations.map((d: any) => d.id);
        const res = await apiClient.getAutoFill(destIds, 'chain');

        let newDesc = day.description;
        let newAct = day.activities;
        let filled = false;

        if (res.description) {
            newDesc = res.description;
            filled = true;
        }
        if (res.activity) {
            newAct = res.activity;
            filled = true;
        }

        if (filled) {
            onChange({
                ...day,
                description: newDesc,
                activities: newAct
            });
            toast.success('Auto-filled from Matrix', { id: loadingToast });
        } else {
            toast('No specific matrix content found for this sequence.', { icon: 'ℹ️', id: loadingToast });
        }

    } catch (error) {
        console.error("Auto-fill failed", error);
        toast.error("Failed to fetch matrix content", { id: loadingToast });
    }
  };

  const accommodationOptions = accommodations.map(acc => ({
    value: acc.id,
    label: acc.name
  }));

  return (
    <Card className="mb-4">
      <CardHeader className="flex flex-row items-center justify-between py-2 space-y-0 bg-gray-50/50">
        <CardTitle className="text-sm font-medium">Day {day.day_number}</CardTitle>
        <Button type="button" variant="ghost" size="icon" onClick={onRemove} className="text-red-500 hover:text-red-700">
          <Trash className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent className="space-y-4 pt-4">
        <div className="space-y-2">
            <Label>Title</Label>
            <Input 
                value={day.day_title || ''} 
                onChange={(e) => onChange({...day, day_title: e.target.value})}
                placeholder="Day Title e.g. Arrival"
            />
        </div>

        <div className="space-y-2">
            <Label>Destinations</Label>
            <div className="flex flex-wrap gap-2 mb-2 p-2 border rounded-md min-h-[40px]">
                {selectedDestinations.length === 0 && <span className="text-sm text-gray-400">No destinations</span>}
                {selectedDestinations.map((d: any) => (
                    <Badge key={d.id} variant="secondary">
                        {d.name}
                        <button type="button" onClick={() => toggleDestination(d.id)} className="ml-1 hover:text-red-500"><X className="h-3 w-3" /></button>
                    </Badge>
                ))}
                
                <Dialog open={isDestOpen} onOpenChange={setIsDestOpen}>
                    <DialogTrigger asChild>
                        <Button variant="outline" size="sm" className="h-6 w-6 p-0 rounded-full ml-auto">
                            <Plus className="h-3 w-3" />
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="p-0">
                        <DialogHeader className="px-4 pt-4 pb-2">
                            <DialogTitle>Select Destinations</DialogTitle>
                        </DialogHeader>
                        <Command>
                            <CommandInput placeholder="Search destinations..." />
                            <CommandList>
                                <CommandEmpty>No destination found.</CommandEmpty>
                                <CommandGroup>
                                    {destinations.map((d: any) => (
                                        <CommandItem
                                            key={d.id}
                                            value={d.name}
                                            onSelect={() => toggleDestination(d.id)}
                                        >
                                            <Check
                                                className={cn(
                                                    "mr-2 h-4 w-4",
                                                    (day.destination_ids || []).includes(d.id)
                                                        ? "opacity-100"
                                                        : "opacity-0"
                                                )}
                                            />
                                            {d.name}
                                        </CommandItem>
                                    ))}
                                </CommandGroup>
                            </CommandList>
                        </Command>
                    </DialogContent>
                </Dialog>
            </div>
        </div>

        <div className="space-y-2">
            <div className="flex justify-between items-center">
                <Label>Description</Label>
                <Button 
                    type="button"
                    variant="ghost" 
                    size="sm" 
                    onClick={handleAutoFill}
                    disabled={selectedDestinations.length === 0}
                    className="h-6 text-xs text-blue-600"
                >
                    <Wand2 className="h-3 w-3 mr-1" />
                    Auto-fill
                </Button>
            </div>
            <Textarea 
                value={day.description} 
                onChange={(e) => onChange({...day, description: e.target.value})}
                rows={3}
            />
        </div>

        <div className="space-y-2">
            <Label>Activities</Label>
             <Textarea 
                value={day.activities} 
                onChange={(e) => onChange({...day, activities: e.target.value})}
                rows={2}
                placeholder="List activities..."
            />
        </div>

        <div className="space-y-2">
            <Label>Meals Included</Label>
            <Input
                value={day.meals_included || ''}
                onChange={(e) => onChange({...day, meals_included: e.target.value})}
                placeholder="e.g. Breakfast, Lunch, Dinner"
            />
        </div>


          <div className="space-y-2">
           <Label>Accommodation</Label>
           <Combobox
             options={accommodationOptions}
             value={day.accommodation_id}
             onChange={(val) => onChange({...day, accommodation_id: val})}
             placeholder="Select accommodation..."
             searchPlaceholder="Search accommodations..."
             emptyText="No accommodation found."
           />
          </div>

          <div className="space-y-2">
            <Label>Atmospheric Image</Label>
            {day.atmospheric_image_url ? (
                <div className="relative aspect-video rounded-md overflow-hidden group border">
                    <img src={day.atmospheric_image_url} alt="Atmospheric" className="w-full h-full object-cover" />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        <Button type="button" variant="secondary" size="sm" onClick={() => setIsGalleryOpen(true)}>
                            Library
                        </Button>
                         <label 
                            htmlFor={`day-upload-${day.day_number}-change`}
                            className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-secondary text-secondary-foreground hover:bg-secondary/80 h-9 px-3"
                        >
                             Upload
                             <input
                                type="file"
                                id={`day-upload-${day.day_number}-change`}
                                className="hidden"
                                accept="image/*"
                                onChange={async (e) => {
                                    const file = e.target.files?.[0];
                                    if (!file) return;
                                    
                                    const loadingToast = toast.loading('Uploading image...');
                                    try {
                                        if (!day.itinerary_id) {
                                             toast.error("Save itinerary first", { id: loadingToast });
                                             return;
                                        }

                                        const newImages = await apiClient.uploadItineraryImages(day.itinerary_id, [file]);
                                        if (newImages && newImages.length > 0) {
                                            onChange({...day, atmospheric_image_url: newImages[0].image_url});
                                            toast.success('Image uploaded', { id: loadingToast });
                                        }
                                    } catch (error) {
                                        console.error(error);
                                        toast.error('Failed to upload', { id: loadingToast });
                                    }
                                }}
                            />
                        </label>
                        <Button type="button" variant="destructive" size="sm" onClick={() => onChange({...day, atmospheric_image_url: null})}>
                            Remove
                        </Button>
                    </div>
                </div>
            ) : (
                <div className="flex gap-2">
                    <Button type="button" variant="outline" className="flex-1 h-20 border-dashed" onClick={() => setIsGalleryOpen(true)}>
                        <ImageIcon className="mr-2 h-4 w-4" />
                        Select from Library
                    </Button>
                    <div className="flex-1">
                        <input
                            type="file"
                            id={`day-upload-${day.day_number}`}
                            className="hidden"
                            accept="image/*"
                            onChange={async (e) => {
                                const file = e.target.files?.[0];
                                if (!file) return;
                                
                                const loadingToast = toast.loading('Uploading image...');
                                try {
                                    // We need itinerary ID. It's not passed explicitly but 'day' might have it?
                                    // Actually DayEditorProps doesn't have itineraryId.
                                    // We can't upload without itinerary ID if we use uploadItineraryImages endpoint.
                                    // Checking Day object... it has itinerary_id.
                                    
                                    if (!day.itinerary_id) {
                                         toast.error("Save itinerary first before uploading day images", { id: loadingToast });
                                         return;
                                    }

                                    const newImages = await apiClient.uploadItineraryImages(day.itinerary_id, [file]);
                                    if (newImages && newImages.length > 0) {
                                        onChange({...day, atmospheric_image_url: newImages[0].image_url}); // Use image_url from response
                                        toast.success('Image uploaded', { id: loadingToast });
                                    }
                                } catch (error) {
                                    console.error(error);
                                    toast.error('Failed to upload', { id: loadingToast });
                                }
                            }}
                        />
                        <label 
                            htmlFor={`day-upload-${day.day_number}`}
                            className="flex flex-col items-center justify-center w-full h-20 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 hover:border-blue-500 transition-colors"
                        >
                            <span className="flex items-center text-sm font-medium text-gray-600">
                                <Plus className="mr-2 h-4 w-4" /> Upload New
                            </span>
                        </label>
                    </div>
                </div>
            )}
            
            <ImageGalleryModal
                open={isGalleryOpen}
                onOpenChange={setIsGalleryOpen}
                limit={1}
                onSelect={(images: any[]) => {
                    if (images.length > 0) {
                        onChange({...day, atmospheric_image_url: images[0].url});
                    }
                }}
            />
          </div>
      </CardContent>
    </Card>
  );
}
