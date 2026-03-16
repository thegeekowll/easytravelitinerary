'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Plus, X, Pencil, Check, CheckCircle2, XCircle } from 'lucide-react';
import ImageGalleryModal from '@/components/shared/image-gallery-modal';

interface Item {
  id: string;
  name: string;
  description?: string;
  icon_name?: string;
  image_url?: string;
  sort_order?: number;
}

function ItemForm({
  title,
  onSave,
  saving,
  initial,
  onCancel,
}: {
  title: string;
  onSave: (data: { name: string; description: string; icon_name: string; image_url: string | null }) => void;
  saving: boolean;
  initial?: Item;
  onCancel?: () => void;
}) {
  const [name, setName] = useState(initial?.name || '');
  const [description, setDescription] = useState(initial?.description || '');
  const [iconName, setIconName] = useState(initial?.icon_name || '');
  const [image, setImage] = useState<string | null>(initial?.image_url || null);
  const [galleryOpen, setGalleryOpen] = useState(false);

  const handleSubmit = () => {
    if (!name.trim()) return;
    onSave({ name, description, icon_name: iconName, image_url: image });
    if (!initial) {
      setName('');
      setDescription('');
      setIconName('');
      setImage(null);
    }
  };

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>Title *</Label>
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Airport Transfer" />
        </div>
        <div className="space-y-1">
          <Label>Icon Name</Label>
          <Input value={iconName} onChange={(e) => setIconName(e.target.value)} placeholder="e.g. plane (optional)" />
        </div>
      </div>
      <div className="space-y-1">
        <Label>Description</Label>
        <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Brief details..." />
      </div>
      <div className="space-y-1">
        <Label>Image (Optional)</Label>
        <div className="flex items-center gap-2">
          {image ? (
            <div className="relative h-14 w-14 rounded overflow-hidden border">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={image} alt="selected" className="h-full w-full object-cover" />
              <button
                type="button"
                onClick={() => setImage(null)}
                className="absolute top-0 right-0 bg-red-500 text-white p-0.5 rounded-bl hover:bg-red-600"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <Button type="button" variant="outline" size="sm" onClick={() => setGalleryOpen(true)}>
                From Gallery
              </Button>
              <div className="relative">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => document.getElementById(`item-upload-${title}`)?.click()}
                >
                  Upload
                </Button>
                <input
                  id={`item-upload-${title}`}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (!file) return;
                    const toastId = toast.loading('Uploading...');
                    try {
                      const res = await apiClient.uploadCompanyAsset(file, 'DEFAULT_IMAGE');
                      setImage(res.asset_url);
                      toast.success('Uploaded', { id: toastId });
                    } catch {
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
        <Button type="button" onClick={handleSubmit} disabled={saving || !name.trim()} className="flex-1">
          {saving ? 'Saving...' : initial ? (
            <><Check className="h-4 w-4 mr-2" /> Save Changes</>
          ) : (
            <><Plus className="h-4 w-4 mr-2" /> {title}</>
          )}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
      <ImageGalleryModal
        open={galleryOpen}
        onOpenChange={setGalleryOpen}
        limit={1}
        onSelect={(selected: any[]) => {
          if (selected[0]) setImage(selected[0].url);
        }}
      />
    </div>
  );
}

function ItemList({
  items,
  type,
  onUpdate,
  onDelete,
}: {
  items: Item[];
  type: 'inclusion' | 'exclusion';
  onUpdate: (id: string, data: any) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editSaving, setEditSaving] = useState(false);

  const handleSave = async (id: string, data: any) => {
    setEditSaving(true);
    try {
      await onUpdate(id, data);
      setEditingId(null);
    } finally {
      setEditSaving(false);
    }
  };

  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p className="text-sm">No {type}s yet. Add one above.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.id} className="border rounded-md">
          {editingId === item.id ? (
            <div className="p-4 bg-blue-50">
              <ItemForm
                title="Save Changes"
                initial={item}
                saving={editSaving}
                onSave={(data) => handleSave(item.id, data)}
                onCancel={() => setEditingId(null)}
              />
            </div>
          ) : (
            <div className="flex items-center justify-between p-3 hover:bg-gray-50">
              <div className="flex items-center gap-3">
                {item.image_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={item.image_url} alt={item.name} className="h-10 w-10 rounded object-cover border flex-shrink-0" />
                ) : (
                  <div className="h-10 w-10 rounded border bg-gray-100 flex items-center justify-center flex-shrink-0">
                    {type === 'inclusion' ? (
                      <CheckCircle2 className="h-5 w-5 text-green-400" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-400" />
                    )}
                  </div>
                )}
                <div>
                  <p className="font-medium text-sm">{item.name}</p>
                  {item.description && <p className="text-xs text-gray-500">{item.description}</p>}
                  {item.icon_name && <p className="text-xs text-gray-400">Icon: {item.icon_name}</p>}
                </div>
              </div>
              <div className="flex items-center gap-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0 text-blue-500 hover:text-blue-700 hover:bg-blue-50"
                  onClick={() => setEditingId(item.id)}
                >
                  <Pencil className="h-3.5 w-3.5" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                  onClick={async () => {
                    if (!confirm(`Delete "${item.name}"? This will remove it from all tours.`)) return;
                    await onDelete(item.id);
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function InclusionsPage() {
  const [inclusions, setInclusions] = useState<Item[]>([]);
  const [exclusions, setExclusions] = useState<Item[]>([]);
  const [loadingInclusions, setLoadingInclusions] = useState(true);
  const [loadingExclusions, setLoadingExclusions] = useState(true);
  const [savingInclusion, setSavingInclusion] = useState(false);
  const [savingExclusion, setSavingExclusion] = useState(false);

  const fetchAll = async () => {
    try {
      const [inc, exc] = await Promise.all([
        apiClient.getInclusions(),
        apiClient.getExclusions(),
      ]);
      setInclusions(inc);
      setExclusions(exc);
    } catch {
      toast.error('Failed to load data');
    } finally {
      setLoadingInclusions(false);
      setLoadingExclusions(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleCreateInclusion = async (data: any) => {
    setSavingInclusion(true);
    try {
      const res = await apiClient.createInclusion(data);
      setInclusions(prev => [...prev, res]);
      toast.success('Inclusion created');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to create inclusion');
    } finally {
      setSavingInclusion(false);
    }
  };

  const handleUpdateInclusion = async (id: string, data: any) => {
    const res = await apiClient.updateInclusion(id, data);
    setInclusions(prev => prev.map(i => (i.id === id ? res : i)));
    toast.success('Inclusion updated');
  };

  const handleDeleteInclusion = async (id: string) => {
    await apiClient.deleteInclusion(id);
    setInclusions(prev => prev.filter(i => i.id !== id));
    toast.success('Inclusion deleted');
  };

  const handleCreateExclusion = async (data: any) => {
    setSavingExclusion(true);
    try {
      const res = await apiClient.createExclusion(data);
      setExclusions(prev => [...prev, res]);
      toast.success('Exclusion created');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to create exclusion');
    } finally {
      setSavingExclusion(false);
    }
  };

  const handleUpdateExclusion = async (id: string, data: any) => {
    const res = await apiClient.updateExclusion(id, data);
    setExclusions(prev => prev.map(i => (i.id === id ? res : i)));
    toast.success('Exclusion updated');
  };

  const handleDeleteExclusion = async (id: string) => {
    await apiClient.deleteExclusion(id);
    setExclusions(prev => prev.filter(i => i.id !== id));
    toast.success('Exclusion deleted');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Inclusions & Exclusions</h1>
        <p className="text-gray-600">Manage what&apos;s included or excluded in your tours</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inclusions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-700">
              <CheckCircle2 className="h-5 w-5" />
              Inclusions ({inclusions.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border rounded-md p-4 bg-gray-50">
              <p className="text-sm font-medium text-gray-700 mb-3">Add New Inclusion</p>
              <ItemForm
                title="Add Inclusion"
                saving={savingInclusion}
                onSave={handleCreateInclusion}
              />
            </div>
            {loadingInclusions ? (
              <p className="text-sm text-gray-500 text-center py-4">Loading...</p>
            ) : (
              <ItemList
                items={inclusions}
                type="inclusion"
                onUpdate={handleUpdateInclusion}
                onDelete={handleDeleteInclusion}
              />
            )}
          </CardContent>
        </Card>

        {/* Exclusions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700">
              <XCircle className="h-5 w-5" />
              Exclusions ({exclusions.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border rounded-md p-4 bg-gray-50">
              <p className="text-sm font-medium text-gray-700 mb-3">Add New Exclusion</p>
              <ItemForm
                title="Add Exclusion"
                saving={savingExclusion}
                onSave={handleCreateExclusion}
              />
            </div>
            {loadingExclusions ? (
              <p className="text-sm text-gray-500 text-center py-4">Loading...</p>
            ) : (
              <ItemList
                items={exclusions}
                type="exclusion"
                onUpdate={handleUpdateExclusion}
                onDelete={handleDeleteExclusion}
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
