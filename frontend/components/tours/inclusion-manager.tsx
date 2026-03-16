'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Plus, X, List as ListIcon, Pencil, Check } from 'lucide-react';
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
  const [loading, setLoading] = useState(false);

  // Create form state
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newIcon, setNewIcon] = useState('');
  const [newImage, setNewImage] = useState<string | null>(null);
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);

  // Edit state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editIcon, setEditIcon] = useState('');
  const [editImage, setEditImage] = useState<string | null>(null);
  const [isEditGalleryOpen, setIsEditGalleryOpen] = useState(false);
  const [editLoading, setEditLoading] = useState(false);

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

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setLoading(true);
    try {
      const payload = {
        name: newTitle,
        description: newDescription || undefined,
        icon_name: newIcon || undefined,
        image_url: newImage,
      };

      const res = type === 'inclusion'
        ? await apiClient.createInclusion(payload)
        : await apiClient.createExclusion(payload);

      setItems(prev => [...prev, res]);
      setNewTitle('');
      setNewDescription('');
      setNewIcon('');
      setNewImage(null);
      toast.success(`${type === 'inclusion' ? 'Inclusion' : 'Exclusion'} created`);
    } catch (error: any) {
      console.error(error);
      const msg = error?.response?.data?.detail || 'Failed to create item';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (item: Item) => {
    setEditingId(item.id);
    setEditTitle(item.name);
    setEditDescription(item.description || '');
    setEditIcon(item.icon_name || '');
    setEditImage(item.image_url || null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
    setEditDescription('');
    setEditIcon('');
    setEditImage(null);
  };

  const handleSaveEdit = async (id: string) => {
    if (!editTitle.trim()) return;
    setEditLoading(true);
    try {
      const payload = {
        name: editTitle,
        description: editDescription || undefined,
        icon_name: editIcon || undefined,
        image_url: editImage,
      };

      const res = type === 'inclusion'
        ? await apiClient.updateInclusion(id, payload)
        : await apiClient.updateExclusion(id, payload);

      setItems(prev => prev.map(i => (i.id === id ? res : i)));
      cancelEdit();
      toast.success('Updated successfully');
    } catch (error: any) {
      console.error(error);
      const msg = error?.response?.data?.detail || 'Failed to update item';
      toast.error(msg);
    } finally {
      setEditLoading(false);
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
        <Dialog open={isOpen} onOpenChange={(open) => { setIsOpen(open); if (!open) cancelEdit(); }}>
          <DialogTrigger asChild>
            <Button type="button" variant="outline" size="sm">
              <ListIcon className="h-4 w-4 mr-2" />
              Manage {type}s
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Manage {type === 'inclusion' ? 'Inclusions' : 'Exclusions'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              {/* Create New */}
              <div className="grid gap-4 border p-4 rounded-md bg-gray-50">
                <p className="text-sm font-medium text-gray-700">Add New</p>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Title *</Label>
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
                          type="button"
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
                          From Gallery
                        </Button>
                        <div className="relative">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => document.getElementById(`inclusion-upload-new-${type}`)?.click()}
                          >
                            Upload
                          </Button>
                          <input
                            id={`inclusion-upload-new-${type}`}
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={async (e) => {
                              const file = e.target.files?.[0];
                              if (!file) return;
                              const toastId = toast.loading('Uploading...');
                              try {
                                const res = await apiClient.uploadCompanyAsset(file, 'DEFAULT_IMAGE');
                                setNewImage(res.asset_url);
                                toast.success('Uploaded', { id: toastId });
                              } catch (err) {
                                console.error(err);
                                toast.error('Upload failed', { id: toastId });
                              }
                              e.target.value = '';
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <Button
                  type="button"
                  onClick={handleCreate}
                  disabled={loading || !newTitle.trim()}
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {loading ? 'Creating...' : `Create New ${type === 'inclusion' ? 'Inclusion' : 'Exclusion'}`}
                </Button>
              </div>

              {/* Existing Items */}
              <div className="space-y-2 border rounded-md p-2 max-h-[300px] overflow-y-auto">
                {items.length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-4">No items yet. Add one above.</p>
                )}
                {items.map((item: Item) => (
                  <div key={item.id}>
                    {editingId === item.id ? (
                      /* Edit mode row */
                      <div className="border rounded p-3 bg-blue-50 space-y-3">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="space-y-1">
                            <Label className="text-xs">Title *</Label>
                            <Input
                              value={editTitle}
                              onChange={(e) => setEditTitle(e.target.value)}
                              className="h-8 text-sm"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label className="text-xs">Icon Name</Label>
                            <Input
                              value={editIcon}
                              onChange={(e) => setEditIcon(e.target.value)}
                              className="h-8 text-sm"
                              placeholder="optional"
                            />
                          </div>
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs">Description</Label>
                          <Input
                            value={editDescription}
                            onChange={(e) => setEditDescription(e.target.value)}
                            className="h-8 text-sm"
                            placeholder="optional"
                          />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs">Image</Label>
                          <div className="flex items-center gap-2">
                            {editImage ? (
                              <div className="relative h-12 w-12 rounded overflow-hidden border">
                                {/* eslint-disable-next-line @next/next/no-img-element */}
                                <img src={editImage} alt="edit" className="h-full w-full object-cover" />
                                <button
                                  type="button"
                                  onClick={() => setEditImage(null)}
                                  className="absolute top-0 right-0 bg-red-500 text-white p-0.5 rounded-bl"
                                >
                                  <X className="h-2 w-2" />
                                </button>
                              </div>
                            ) : (
                              <div className="flex gap-2">
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  className="h-7 text-xs"
                                  onClick={() => setIsEditGalleryOpen(true)}
                                >
                                  From Gallery
                                </Button>
                                <div className="relative">
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    className="h-7 text-xs"
                                    onClick={() => document.getElementById(`inclusion-upload-edit-${type}`)?.click()}
                                  >
                                    Upload
                                  </Button>
                                  <input
                                    id={`inclusion-upload-edit-${type}`}
                                    type="file"
                                    accept="image/*"
                                    className="hidden"
                                    onChange={async (e) => {
                                      const file = e.target.files?.[0];
                                      if (!file) return;
                                      const toastId = toast.loading('Uploading...');
                                      try {
                                        const res = await apiClient.uploadCompanyAsset(file, 'DEFAULT_IMAGE');
                                        setEditImage(res.asset_url);
                                        toast.success('Uploaded', { id: toastId });
                                      } catch (err) {
                                        console.error(err);
                                        toast.error('Upload failed', { id: toastId });
                                      }
                                      e.target.value = '';
                                    }}
                                  />
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            type="button"
                            size="sm"
                            onClick={() => handleSaveEdit(item.id)}
                            disabled={editLoading || !editTitle.trim()}
                            className="flex-1"
                          >
                            <Check className="h-3 w-3 mr-1" />
                            {editLoading ? 'Saving...' : 'Save'}
                          </Button>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={cancelEdit}
                            className="flex-1"
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      /* Normal row */
                      <div className="flex items-center justify-between p-3 bg-white border rounded text-sm hover:shadow-sm transition-shadow">
                        <div className="flex items-center gap-3">
                          {item.image_url && (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img src={item.image_url} alt={item.name} className="h-10 w-10 rounded object-cover border" />
                          )}
                          <div className="flex flex-col">
                            <span className="font-medium">{item.name}</span>
                            {item.description && (
                              <span className="text-xs text-gray-500">{item.description}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-blue-500 hover:text-blue-700 hover:bg-blue-50"
                            onClick={() => startEdit(item)}
                          >
                            <Pencil className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                            onClick={(e) => handleDelete(item.id, e)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Gallery modals rendered inside dialog but managed by portal */}
            <ImageGalleryModal
              open={isGalleryOpen}
              onOpenChange={setIsGalleryOpen}
              limit={1}
              onSelect={(selected: any[]) => {
                if (selected[0]) setNewImage(selected[0].url);
              }}
            />
            <ImageGalleryModal
              open={isEditGalleryOpen}
              onOpenChange={setIsEditGalleryOpen}
              limit={1}
              onSelect={(selected: any[]) => {
                if (selected[0]) setEditImage(selected[0].url);
              }}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="border rounded-md p-4 min-h-[100px] space-y-2">
        <div className="flex flex-wrap gap-2">
          {items.map((item: Item) => {
            const isSelected = selectedIds.includes(item.id);
            return (
              <Badge
                key={item.id}
                variant={isSelected ? 'default' : 'outline'}
                className="cursor-pointer hover:bg-primary/90 py-1.5 px-3"
                onClick={() => toggleSelection(item.id)}
              >
                <span className="font-medium">{item.name}</span>
                {isSelected && <X className="ml-2 h-3 w-3" />}
              </Badge>
            );
          })}
          {items.length === 0 && (
            <span className="text-sm text-gray-400">
              No {type}s available. Click Manage to add some.
            </span>
          )}
        </div>
      </div>
      <p className="text-xs text-gray-500">Click items to select/deselect.</p>
    </div>
  );
}
