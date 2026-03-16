'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Plus, X, List as ListIcon } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import ImageGalleryModal from '@/components/shared/image-gallery-modal';

interface Item {
  id: string;
  name: string;
  description?: string;
  icon_name?: string;
  image_url?: string;
}

interface InclusionManagerProps {
  type: 'inclusion' | 'exclusion';
  selectedIds: string[];
  onSelectionChange: (ids: string[], items?: Item[]) => void;
}

export default function InclusionManager({ type, selectedIds, onSelectionChange }: InclusionManagerProps) {
  const [items, setItems] = useState<Item[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newIcon, setNewIcon] = useState(''); // Simple text input for now, could be icon picker
  const [loading, setLoading] = useState(false);

  // ... (fetchItems same as before) ...
  const fetchItems = async () => {
    try {
      const res = type === 'inclusion' 
        ? await apiClient.getInclusions()
        : await apiClient.getExclusions();
      setItems(res);
    } catch (error) {
      console.error('Failed to fetch items', error);
      toast.error('Failed to load items');
    }
  };

  useEffect(() => {
    fetchItems();
  }, [type]);


  // ... inside InclusionManager component
  const [newImage, setNewImage] = useState<string | null>(null);
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setLoading(true);
    try {
      const payload = { 
          name: newTitle, 
          description: newDescription,
          icon_name: newIcon,
          image_url: newImage
      };
      
      const res = type === 'inclusion'
        ? await apiClient.createInclusion(payload)
        : await apiClient.createExclusion(payload);
      
      setItems([...items, res]);
      setNewTitle('');
      setNewDescription('');
      setNewIcon('');
      setNewImage(null);
      toast.success(`${type === 'inclusion' ? 'Inclusion' : 'Exclusion'} created`);
    } catch (error) {
        console.error(error);
      toast.error('Failed to create item');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this item globally?')) return;
    
    try {
      if (type === 'inclusion') {
        await apiClient.deleteInclusion(id);
      } else {
        await apiClient.deleteExclusion(id);
      }
      const newItems = items.filter(i => i.id !== id);
      setItems(newItems);
      if (selectedIds.includes(id)) {
        const newSelectedIds = selectedIds.filter(sid => sid !== id);
        onSelectionChange(newSelectedIds, newItems.filter(i => newSelectedIds.includes(i.id)));
      }
      toast.success('Item deleted');
    } catch (error) {
        console.error(error);
      toast.error('Failed to delete item');
    }
  };

  const toggleSelection = (id: string) => {
    let newSelectedIds;
    if (selectedIds.includes(id)) {
      newSelectedIds = selectedIds.filter(sid => sid !== id);
    } else {
      newSelectedIds = [...selectedIds, id];
    }
    onSelectionChange(newSelectedIds, items.filter(i => newSelectedIds.includes(i.id)));
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Label className="capitalize">{type}s</Label>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              <ListIcon className="h-4 w-4 mr-2" />
              Manage {type}s
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Manage {type === 'inclusion' ? 'Inclusions' : 'Exclusions'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="grid gap-4 border p-4 rounded-md bg-gray-50">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <Label>Title</Label>
                        <Input 
                        value={newTitle}
                        onChange={(e) => setNewTitle(e.target.value)}
                        placeholder="e.g. Airport Transfer"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label>Icon Name</Label>
                        <Input 
                        value={newIcon}
                        onChange={(e) => setNewIcon(e.target.value)}
                        placeholder="e.g. plane (optional)"
                        />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Input 
                      value={newDescription}
                      onChange={(e) => setNewDescription(e.target.value)}
                      placeholder="Brief details..."
                    />
                  </div>
                  
                  <div className="space-y-2">
                      <Label>Image (Optional)</Label>
                      <div className="flex items-center gap-4">
                          {newImage ? (
                              <div className="relative h-16 w-16 rounded overflow-hidden border">
                                  {/* eslint-disable-next-line @next/next/no-img-element */}
                                  <img src={newImage} alt="Selected" className="h-full w-full object-cover" />
                                  <button 
                                      onClick={() => setNewImage(null)}
                                      className="absolute top-0 right-0 bg-red-500 text-white p-0.5 rounded-bl hover:bg-red-600"
                                  >
                                      <X className="h-3 w-3" />
                                  </button>
                              </div>
                          ) : (
                              <div className="flex gap-2">
                                  <Button 
                                    type="button" 
                                    variant="outline" 
                                    size="sm" 
                                    onClick={() => setIsGalleryOpen(true)}
                                  >
                                    Select from Gallery
                                  </Button>
                                  
                                  <div className="relative">
                                      <Button 
                                        type="button" 
                                        variant="outline" 
                                        size="sm"
                                        onClick={() => document.getElementById('inclusion-upload')?.click()}
                                      >
                                        Upload New
                                      </Button>
                                      <input 
                                          id="inclusion-upload"
                                          type="file"
                                          accept="image/*"
                                          className="hidden"
                                          onChange={async (e) => {
                                              const file = e.target.files?.[0];
                                              if (!file) return;
                                              
                                              const toastId = toast.loading("Uploading...");
                                              try {
                                                  // Use generic asset upload, treating it as a 'DEFAULT_IMAGE' or similar for now
                                                  // or we can add a specific type if backend supports it. 'DEFAULT_IMAGE' is safe.
                                                  const res = await apiClient.uploadCompanyAsset(file, 'DEFAULT_IMAGE');
                                                  setNewImage(res.asset_url);
                                                  toast.success("Uploaded", { id: toastId });
                                              } catch (err) {
                                                  console.error(err);
                                                  toast.error("Upload failed", { id: toastId });
                                              }
                                              // Reset input
                                              e.target.value = '';
                                          }}
                                      />
                                  </div>
                              </div>
                          )}
                      </div>
                  </div>

                  <Button onClick={handleCreate} disabled={loading || !newTitle.trim()} className="w-full">
                    <Plus className="h-4 w-4 mr-2" /> Create New {type === 'inclusion' ? 'Inclusion' : 'Exclusion'}
                  </Button>
              </div>
              
              <div className="max-h-[300px] overflow-y-auto space-y-2 border rounded-md p-2">
                {items.length === 0 && <p className="text-sm text-gray-500 text-center py-4">No items yet</p>}
                {items.map((item: any) => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-white border rounded text-sm hover:shadow-sm transition-shadow">
                    <div className="flex items-center gap-3">
                        {item.image_url && (
                             /* eslint-disable-next-line @next/next/no-img-element */
                            <img src={item.image_url} alt={item.name} className="h-10 w-10 rounded object-cover border" />
                        )}
                        <div className="flex flex-col">
                            <span className="font-medium">{item.name}</span>
                            {item.description && <span className="text-xs text-gray-500">{item.description}</span>}
                        </div>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-8 w-8 p-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                      onClick={(e) => handleDelete(item.id, e)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
            
            <ImageGalleryModal 
                open={isGalleryOpen}
                onOpenChange={setIsGalleryOpen}
                limit={1}
                onSelect={(selected: any[]) => {
                    if (selected[0]) {
                        setNewImage(selected[0].url);
                    }
                }}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="border rounded-md p-4 min-h-[100px] space-y-2">
         <div className="flex flex-wrap gap-2">
            {items.map((item: any) => {
                const isSelected = selectedIds.includes(item.id);
                return (
                    <Badge 
                        key={item.id}
                        variant={isSelected ? "default" : "outline"}
                        className="cursor-pointer hover:bg-primary/90 py-1.5 px-3"
                        onClick={() => toggleSelection(item.id)}
                    >
                        <span className="flex flex-col items-start text-left">
                            <span className="font-medium">{item.name}</span>
                        </span>
                        {isSelected && <X className="ml-2 h-3 w-3" />}
                    </Badge>
                );
            })}
            {items.length === 0 && <span className="text-sm text-gray-400">No {type}s available. Click Manage to add some.</span>}
         </div>
      </div>
       <p className="text-xs text-gray-500">Click items to select/deselect.</p>
    </div>
  );
}
