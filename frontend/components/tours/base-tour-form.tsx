'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Loader2, Plus } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import DayEditor from './day-editor';
import InclusionManager from './inclusion-manager';
import ImageGalleryModal from '@/components/shared/image-gallery-modal';
import { useRouter } from 'next/navigation';

interface BaseTourFormProps {
  initialData?: any;
  isEditing?: boolean;
  isCustomItinerary?: boolean;
}

export default function BaseTourForm({ initialData, isEditing = false, isCustomItinerary = false }: BaseTourFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [dataLoaded, setDataLoaded] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    tour_name: '',
    tour_code: '',
    tour_type_id: '',
    accommodation_level_id: '',
    number_of_days: 1,
    number_of_nights: 0,
    description: '',
    highlights: '',
    difficulty_level: 'Moderate',
    is_active: true,
    days: [] as any[],
    id: '' // added id to state for creation flow
  });

  const [types, setTypes] = useState<any[]>([]);
  const [levels, setLevels] = useState<any[]>([]);
  const [destinations, setDestinations] = useState<any[]>([]);
  const [accommodations, setAccommodations] = useState<any[]>([]);
  
  // Selection State for Inclusions/Exclusions
  const [selectedInclusionIds, setSelectedInclusionIds] = useState<string[]>([]);
  const [selectedExclusionIds, setSelectedExclusionIds] = useState<string[]>([]);

  // Images
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  const [targetImageRole, setTargetImageRole] = useState<string | null>(null);

  const [defaultImages, setDefaultImages] = useState<any[]>([]);

  // Inline Creation State
  const [isTypeDialogOpen, setIsTypeDialogOpen] = useState(false);
  const [isLevelDialogOpen, setIsLevelDialogOpen] = useState(false);
  const [newType, setNewType] = useState({ name: '', description: '' });
  const [newLevel, setNewLevel] = useState({ name: '', description: '' });
  const [creatingInline, setCreatingInline] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [typesRes, levelsRes, destRes, accRes, defaultsRes] = await Promise.all([
          apiClient.getTourTypes(),
          apiClient.getAccommodationLevels(),
          apiClient.getDestinations({ limit: 100 }),
          apiClient.getAccommodations({ limit: 100 }),
          apiClient.listCompanyAssets('DEFAULT_IMAGE')
        ]);
        
        const typesList = Array.isArray(typesRes) ? typesRes : (typesRes?.items || []);
        const levelsList = Array.isArray(levelsRes) ? levelsRes : (levelsRes?.items || []);
        
        setTypes(typesList);
        setLevels(levelsList);
        setDestinations(destRes?.items || []);
        setAccommodations(accRes?.items || []);
        setDefaultImages(defaultsRes || []);
        
        if (initialData) {
            setFormData({
                tour_name: initialData.tour_name || initialData.title || '',
                tour_code: initialData.tour_code || '',
                tour_type_id: initialData.tour_type_id,
                accommodation_level_id: initialData.accommodation_level_id || '',
                number_of_days: initialData.number_of_days || initialData.duration_days || 1,
                number_of_nights: initialData.number_of_nights || 0,
                description: initialData.description || '',
                highlights: initialData.highlights || '',
                difficulty_level: initialData.difficulty_level || 'Moderate',
                is_active: initialData.is_active,
                days: (initialData.days || []).map((day: any) => ({
                    ...day,
                    destination_ids: day.destinations?.map((d: any) => d.id) || []
                })),
                id: initialData.id
            });
            setSelectedInclusionIds(initialData.inclusions?.map((i: any) => i.id) || []);
            setSelectedExclusionIds(initialData.exclusions?.map((e: any) => e.id) || []);
        } else {
            // Check for intake data
            let intakeDays = 1;
            if (typeof window !== 'undefined') {
                const savedIntake = sessionStorage.getItem('draft_traveler_info');
                if (savedIntake) {
                    try {
                        const intake = JSON.parse(savedIntake);
                        if (intake.numberOfDays) intakeDays = intake.numberOfDays;
                        // We also need to set client name implies stored elsewhere or use it here
                        // For now we trust handleSubmit to read it again or we can store it in a new state if needed.
                    } catch (e) {
                        console.error("Failed to parse", e);
                    }
                }
            }
            generateDays(intakeDays);
        }
        
      } finally {
        setDataLoaded(true);
      }
    };
    fetchData();
  }, [initialData]);

  // ... (keep generateDays and other methods)

  const handleCreateType = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingInline(true);
    try {
      const created = await apiClient.createTourType(newType);
      setTypes([...types, created]);
      setFormData({ ...formData, tour_type_id: created.id });
      setIsTypeDialogOpen(false);
      setNewType({ name: '', description: '' });
      toast.success('Tour Type created');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create tour type');
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
      setFormData({ ...formData, accommodation_level_id: created.id });
      setIsLevelDialogOpen(false);
      setNewLevel({ name: '', description: '' });
      toast.success('Level created');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create level');
    } finally {
      setCreatingInline(false);
    }
  };

  const generateDays = (count: number) => {
    const days = [];
    for (let i = 1; i <= count; i++) {
        const existing = formData.days?.find(d => d.day_number === i);
        days.push(existing || {
            day_number: i,
            day_title: `Day ${i}`,
            description: '',
            activities: '',
            destination_ids: [],
            accommodation_id: null
        });
    }
    setFormData(prev => ({ ...prev, days: days, number_of_days: count }));
  };

  const handleDayChange = (updatedDay: any) => {
    const newDays = formData.days.map(d => d.day_number === updatedDay.day_number ? updatedDay : d);
    setFormData({ ...formData, days: newDays });
  };

  const handleRemoveDay = (dayNum: number) => {
      const newDuration = formData.number_of_days - 1;
      if (newDuration < 1) return;
      generateDays(newDuration);
  }

  const handleAddDay = () => {
      generateDays(formData.number_of_days + 1);
  }
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
        if (isCustomItinerary) {
            // Retrieve intake data for payload
            let intake: any = {};
            if (typeof window !== 'undefined') {
                const saved = sessionStorage.getItem('draft_traveler_info');
                if (saved) intake = JSON.parse(saved);
            }

            // Calculate dates based on intake or defaults
            const depDateStr = intake.arrivalDate || new Date().toISOString().split('T')[0];
            const depDate = new Date(depDateStr);
            
            const numDays = intake.numberOfDays || formData.number_of_days || 1;
            const retDate = new Date(depDate);
            retDate.setDate(retDate.getDate() + (numDays - 1)); // -1 because day 1 is included

            // Payload for Itinerary

            // Construct Travelers List
            const primaryTraveler = {
                full_name: intake.primaryName || "Unknown Client",
                email: intake.primaryEmail || "guest@example.com",
                phone: intake.primaryPhone || "",
                age: parseInt(intake.primaryAge) || null,
                nationality: intake.primaryCountry || "Unknown",
                is_primary: true
            };

            const otherTravelers = (intake.otherTravelers || []).map((t: any) => ({
                full_name: t.name,
                email: null,
                phone: null,
                age: parseInt(t.age) || null,
                nationality: "Unknown",
                is_primary: false
            }));

            const allTravelers = [primaryTraveler, ...otherTravelers];

            // Payload for Itinerary
            const itineraryPayload = {
                tour_title: formData.tour_name, 
                client_name: primaryTraveler.full_name,
                client_email: primaryTraveler.email,
                client_phone: primaryTraveler.phone,
                number_of_travelers: allTravelers.length,
                departure_date: depDateStr, 
                return_date: retDate.toISOString().split('T')[0],
                days: formData.days.map(d => ({
                    itinerary_id: "00000000-0000-0000-0000-000000000000",
                    day_number: d.day_number,
                    day_title: d.day_title || `Day ${d.day_number}`,
                    description: d.description || '',
                    activities: d.activities || '',
                    meals_included: d.meals_included || null,
                    destination_ids: d.destination_ids || [],
                    accommodation_id: d.accommodation_id,
                    is_description_custom: true, 
                    is_activity_custom: true,
                    atmospheric_image_url: d.atmospheric_image_url
                })),
                inclusion_ids: selectedInclusionIds,
                exclusion_ids: selectedExclusionIds,
                tour_type_id: formData.tour_type_id || null,
                accommodation_level_id: formData.accommodation_level_id || null,
                difficulty_level: formData.difficulty_level || null,
                description: formData.description || null,
                highlights: formData.highlights || null,
                creation_method: 'custom',
                travelers: allTravelers
            };
            
            console.log('Sending Custom Itinerary Payload:', JSON.stringify(itineraryPayload, null, 2));
            const newItinerary = await apiClient.createCustomItinerary(itineraryPayload);
            
            // Upload images if any
            if (selectedFiles.length > 0 && newItinerary.id) {
                try {
                    await apiClient.uploadItineraryImages(newItinerary.id, selectedFiles);
                } catch (imgError) {
                    console.error("Failed to upload images:", imgError);
                    toast.error("Itinerary created but image upload failed");
                }
            }

            toast.success("Custom Itinerary created successfully");
            sessionStorage.removeItem('draft_traveler_info'); // Clean up
            router.push('/dashboard/itineraries');
            return;
        }

        const tourPayload = {
            // ... (keep existing)
            tour_name: formData.tour_name,
            tour_code: formData.tour_code,
            tour_type_id: formData.tour_type_id,
            accommodation_level_id: formData.accommodation_level_id || null,
            number_of_days: formData.number_of_days,
            number_of_nights: formData.number_of_nights,
            description: formData.description,
            highlights: formData.highlights,
            difficulty_level: formData.difficulty_level,
            is_active: formData.is_active,
            days: formData.days,
            inclusion_ids: selectedInclusionIds,
            exclusion_ids: selectedExclusionIds
        };

        let tourId = initialData?.id;

        if (isEditing && tourId) {
            await apiClient.updateBaseTour(tourId, tourPayload);
        } else {
           const res = await apiClient.createBaseTour(tourPayload);
           tourId = res.id;
        }
        
        // Handle images separately for now if needed, or rely on them being empty first.
        if (selectedFiles.length > 0 && tourId) {
             await apiClient.uploadBaseTourImages(tourId, selectedFiles);
        }

        toast.success("Tour saved successfully");
        // router.push('/admin/tours'); // Keep user on page for further edits
        
    } catch (error: any) {
        console.error('API Error Details:', error);
        if (error.code === "ERR_NETWORK" || !error.response) {
             toast.error("Connection failed. Please ensure the backend server is running.");
             return;
        }
        console.error('Response Data:', error.response?.data);
        const detail = error.response?.data?.detail;
        let errorMessage = "Failed to save tour";
        
        if (typeof detail === 'string') {
            errorMessage = detail;
        } else if (Array.isArray(detail)) {
            // Handle Pydantic validation errors (list of objects)
            errorMessage = detail.map((err: any) => err.msg).join(', ');
        } else if (typeof detail === 'object' && detail !== null) {
            errorMessage = JSON.stringify(detail);
        }
        
        toast.error(errorMessage);
    } finally {
        setLoading(false);
    }
  };

  if (!dataLoaded) return <div className="flex justify-center p-8"><Loader2 className="animate-spin" /></div>;

  return (
    <form onSubmit={handleSubmit} className="space-y-8 max-w-5xl mx-auto py-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{isEditing ? 'Edit Base Tour' : 'Create Base Tour'}</h1>
        <div className="space-x-2">
            <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
            <Button type="submit" disabled={loading}>{loading && <Loader2 className="mr-2 h-4 w-4 animate-spin"/>} Save Tour</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Metadata */}
        <div className="md:col-span-1 space-y-6">
            <Card>
                <CardContent className="pt-6 space-y-4">
                    <div className="space-y-2">
                        <Label>Tour Name</Label>
                        <Input value={formData.tour_name} onChange={e => setFormData({...formData, tour_name: e.target.value})} required placeholder="e.g. Serengeti Migration" />
                    </div>
                    <div className="space-y-2">
                        <Label>Tour Code</Label>
                        <Input value={formData.tour_code} onChange={e => setFormData({...formData, tour_code: e.target.value})} required placeholder="e.g. KEN001" />
                    </div>
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <Label>Type</Label>
                            <Dialog open={isTypeDialogOpen} onOpenChange={setIsTypeDialogOpen}>
                                <DialogTrigger asChild>
                                    <Button type="button" variant="ghost" size="sm" className="h-4 p-0 px-2 text-xs text-blue-600">
                                        <Plus className="h-3 w-3 mr-1" /> Add New
                                    </Button>
                                </DialogTrigger>
                                <DialogContent className="max-w-sm">
                                    <DialogHeader><DialogTitle>Add Tour Type</DialogTitle></DialogHeader>
                                    <div className="space-y-4 pt-4">
                                        <div className="space-y-2">
                                            <Label>Name</Label>
                                            <Input value={newType.name} onChange={e => setNewType({...newType, name: e.target.value})} placeholder="e.g. Safari" />
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
                            value={formData.tour_type_id} 
                            onChange={(e) => setFormData({...formData, tour_type_id: e.target.value})} 
                            required
                        >
                            <option value="">Select type</option>
                            {types.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                        </Select>
                    </div>
                     <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <Label>Level</Label>
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
                            value={formData.accommodation_level_id} 
                            onChange={(e) => setFormData({...formData, accommodation_level_id: e.target.value})}
                            required
                        >
                            <option value="">Select level</option>
                            {levels.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                        </Select>
                    </div>
                    <div className="space-y-2">
                        <Label>Duration (Days)</Label>
                        <Input 
                            type="number" 
                            min="1" 
                            value={formData.number_of_days} 
                            onChange={e => generateDays(parseInt(e.target.value) || 1)} 
                            required 
                        />
                    </div>
                    <div className="space-y-2">
                        <Label>Duration (Nights)</Label>
                         <Input 
                            type="number" 
                            min="0" 
                            value={formData.number_of_nights} 
                            onChange={e => setFormData({...formData, number_of_nights: parseInt(e.target.value) || 0})}
                            required 
                        />
                    </div>
                     <div className="space-y-2">
                        <Label>Difficulty</Label>
                        <Select 
                            value={formData.difficulty_level} 
                            onChange={(e) => setFormData({...formData, difficulty_level: e.target.value})}
                        >
                            <option value="Easy">Easy</option>
                            <option value="Moderate">Moderate</option>
                            <option value="Challenging">Challenging</option>
                        </Select>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="pt-6 space-y-4">
                     <Label>Inclusions / Exclusions</Label>
                     <InclusionManager 
                        type="inclusion" 
                        selectedIds={selectedInclusionIds} 
                        onSelectionChange={setSelectedInclusionIds} 
                     />
                     <InclusionManager 
                        type="exclusion" 
                        selectedIds={selectedExclusionIds} 
                        onSelectionChange={setSelectedExclusionIds} 
                     />
                </CardContent>
            </Card>
            
                <CardContent className="pt-6 space-y-4">
                     <Label>Images</Label>
                     
                     <div className="space-y-4">
                        {[
                            { role: 'cover', label: 'Cover Photo', desc: 'Main image for the tour card and pdf cover.' },
                            { role: 'accommodation_end', label: 'After Accommodations', desc: 'Displayed after the accommodation section.' },
                            { role: 'inclusions', label: 'Includes/Excludes Page', desc: 'Background or banner for inclusions.' },
                            { role: 'about_banner', label: 'About Us Banner', desc: 'Banner image for the About Us section.' },
                            { role: 'end', label: 'End of Itinerary', desc: 'Final image closing the itinerary.' }
                        ].map((slot) => {
                            let currentImage = initialData?.images?.find((img: any) => img.image_role === slot.role);
                            let isDefault = false;

                            if (!currentImage) {
                                // Try fallback to default image
                                const defaultImg = defaultImages.find((img: any) => img.asset_name === slot.role);
                                if (defaultImg) {
                                    currentImage = {
                                        id: defaultImg.id, 
                                        image_url: defaultImg.asset_url, // Map asset_url to image_url
                                        caption: 'Default Image'
                                    };
                                    isDefault = true;
                                }
                            }
                            
                            return (
                                <div key={slot.role} className="border rounded-lg p-4 space-y-3">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className="font-medium text-sm">{slot.label}</h4>
                                            <p className="text-xs text-muted-foreground">{slot.desc}</p>
                                        </div>
                                        {currentImage && !isDefault && (
                                            <Button 
                                                variant="ghost" 
                                                size="sm" 
                                                className="text-red-500 hover:text-red-700 h-6 px-2"
                                                onClick={async () => {
                                                    if(confirm("Remove this image?")) {
                                                        await apiClient.deleteBaseTourImage(currentImage.id);
                                                        window.location.reload();
                                                    }
                                                }}
                                            >
                                                Remove
                                            </Button>
                                        )}
                                        {isDefault && (
                                            <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-1 rounded">Default</span>
                                        )}
                                    </div>

                                    {currentImage ? (
                                        <div className="relative aspect-video w-full overflow-hidden rounded-md border bg-muted">
                                            <img 
                                                src={currentImage.image_url} 
                                                alt={slot.label} 
                                                className="h-full w-full object-cover" 
                                            />
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-2 gap-2">
                                            <Button 
                                                type="button" 
                                                variant="outline" 
                                                className="h-20 flex flex-col gap-2 border-dashed"
                                                onClick={() => document.getElementById(`upload-${slot.role}`)?.click()}
                                            >
                                                <div className="h-6 w-6 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
                                                    <Plus className="h-4 w-4" />
                                                </div>
                                                <span className="text-xs">Upload New</span>
                                            </Button>
                                            <input 
                                                type="file" 
                                                id={`upload-${slot.role}`} 
                                                className="hidden" 
                                                accept="image/*"
                                                onChange={async (e) => {
                                                    const file = e.target.files?.[0];
                                                    if (!file) return;
                                                    
                                                    const loadingId = toast.loading("Uploading...");
                                                    try {
                                                        // 1. Upload generic
                                                        const tourId_ = initialData?.id || formData.id; // Need ID
                                                        if (!tourId_) {
                                                            toast.error("Save tour first before adding images", {id: loadingId});
                                                            return;
                                                        }
                                                        
                                                        const uploaded = await apiClient.uploadBaseTourImages(tourId_, [file]);
                                                        const newImage = uploaded[0];
                                                        
                                                        // 2. Set Role
                                                        // Delete old if exists? Backend doesn't enforce unique role per tour automatically, but we should.
                                                        // For now just update the new one.
                                                        // Filter out old image locally or logic below.
                                                        
                                                        await apiClient.updateBaseTourImage(newImage.id, { image_role: slot.role });
                                                        toast.success("Uploaded", { id: loadingId });
                                                        window.location.reload(); 
                                                    } catch (err) {
                                                        console.error(err);
                                                        toast.error("Failed", { id: loadingId });
                                                    }
                                                }}
                                            />

                                            <Button 
                                                type="button" 
                                                variant="outline" 
                                                className="h-20 flex flex-col gap-2 border-dashed"
                                                onClick={() => {
                                                    setTargetImageRole(slot.role);
                                                    setIsGalleryOpen(true);
                                                }}
                                            >
                                                <div className="h-6 w-6 rounded-full bg-purple-50 text-purple-600 flex items-center justify-center">
                                                    <div className="h-4 w-4 border-2 border-current rounded-sm" /> 
                                                </div>
                                                <span className="text-xs">Library</span>
                                            </Button>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                     </div>
                     <ImageGalleryModal 
                        open={isGalleryOpen}
                        onOpenChange={(open) => {
                            setIsGalleryOpen(open);
                            // if(!open) setTargetImageRole(null);
                        }}
                        limit={1}
                        onSelect={async (selected) => {
                             if (!targetImageRole || !selected[0]) return;
                             const loadingId = toast.loading("Linking image...");
                             try {
                                 const tourId_ = initialData?.id || formData.id || (isEditing ? initialData.id : null);
                                 if (!tourId_) {
                                     toast.error("Please save the tour first", {id: loadingId});
                                     return;
                                 }
                                
                                 // Add new image link
                                 await apiClient.linkBaseTourImages(tourId_, [{
                                     image_url: selected[0].url,
                                     caption: selected[0].caption,
                                     image_role: targetImageRole
                                 }]);
                                 
                                 toast.success("Image added", { id: loadingId });
                                 window.location.reload();

                             } catch (err) {
                                 console.error(err);
                                 toast.error("Failed to link image", { id: loadingId });
                             }
                        }}
                     />
                </CardContent>
        </div>

        {/* Right Column: Itinerary */}
        <div className="md:col-span-2 space-y-6">
            <Card>
                 <CardContent className="pt-6 space-y-4">
                    <Label className="text-lg font-semibold">Day-by-Day Itinerary</Label>
                    <div className="space-y-4">
                        {formData.days.map((day, idx) => (
                            <DayEditor 
                                key={day.day_number} 
                                index={idx}
                                day={day}
                                destinations={destinations}
                                accommodations={accommodations}
                                onChange={handleDayChange}
                                onRemove={() => handleRemoveDay(day.day_number)}
                            />
                        ))}
                    </div>
                    <div className="flex justify-center pt-4">
                        <Button variant="outline" onClick={handleAddDay} className="w-full border-dashed">
                             <Plus className="mr-2 h-4 w-4" /> Add Day
                        </Button>
                    </div>
                 </CardContent>
            </Card>
        </div>
      </div>
    </form>
  );
}
