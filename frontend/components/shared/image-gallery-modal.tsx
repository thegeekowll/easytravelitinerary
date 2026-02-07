'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2, Search, Check, Trash2 } from 'lucide-react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api/client';
import { cn } from '@/lib/utils/cn';
import { toast } from 'sonner';

interface ImageGalleryModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSelect: (selectedImages: {url: string, caption?: string}[]) => void;
    limit?: number; // Max selectable images
}

export default function ImageGalleryModal({ open, onOpenChange, onSelect, limit = 10 }: ImageGalleryModalProps) {
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const [selectedIds, setSelectedIds] = useState<string[]>([]);
    const queryClient = useQueryClient();
    
    // Fetch Images
    const { data, isLoading, isError } = useQuery({
        queryKey: ['media-library', page, search],
        queryFn: () => apiClient.getMediaLibrary({ page, limit: 20, search }),
        enabled: open // Only fetch when open
    });
    
    const images = data?.items || [];
    
    const handleSelect = (img: any) => {
        if (selectedIds.includes(img.id)) {
            setSelectedIds(prev => prev.filter(id => id !== img.id));
        } else {
            if (limit === 1) {
                 setSelectedIds([img.id]);
            } else {
                 if (selectedIds.length >= limit) return;
                 setSelectedIds(prev => [...prev, img.id]);
            }
        }
    };
    
    const handleSubmit = () => {
        // Find full image objects
        // Logic: Should we store selected objects? Yes, easier.
        // But since we navigate pages, IDs are safer.
        // For this simple MVP, we assume current page selection or we keep a map.
        // To be safe across pages, we won't support multi-page selection in this MVP iteration.
        // We will just filter from currently visible 'images' for now.
        // Proper way: Maintenance of a separate 'selectedImages' map.
        
        const selectedObjs = images.filter((img: any) => selectedIds.includes(img.id)).map((img: any) => ({
            url: img.url,
            caption: img.caption || img.source_name
        }));
        
        onSelect(selectedObjs);
        setSelectedIds([]);
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-4xl h-[80vh] flex flex-col p-0 gap-0">
                <DialogHeader className="px-6 py-4 border-b">
                    <DialogTitle>Image Library</DialogTitle>
                </DialogHeader>
                
                {/* Toolbar */}
                <div className="p-4 border-b bg-gray-50 flex gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                        <Input 
                            placeholder="Search destinations or hotels..." 
                            className="pl-9"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                </div>
                
                {/* Grid */}
                <div className="flex-1 p-6 overflow-y-auto">
                    {isLoading ? (
                        <div className="flex justify-center py-20"><Loader2 className="animate-spin h-8 w-8 text-blue-600" /></div>
                    ) : isError ? (
                        <div className="text-center py-20 text-red-500">Failed to load library.</div>
                    ) : images.length === 0 ? (
                        <div className="text-center py-20 text-gray-400">No images found.</div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {images.map((img: any) => {
                                const isSelected = selectedIds.includes(img.id);
                                return (
                                    <div 
                                        key={img.id} 
                                        className={cn(
                                            "group relative aspect-video rounded-lg overflow-hidden cursor-pointer border-2 transition-all",
                                            isSelected ? "border-blue-600 ring-2 ring-blue-100" : "border-transparent hover:border-gray-200"
                                        )}
                                        onClick={() => handleSelect(img)}
                                    >
                                        <img src={img.url} className="object-cover w-full h-full" alt={img.caption} />
                                        
                                        {/* Overlay Info */}
                                        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent p-2 text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                                            <p className="font-semibold truncate">{img.source_name}</p>
                                            <p className="opacity-80 truncate">{img.source_type}</p>
                                        </div>
                                        
                                        {/* Selection Check */}
                                        {isSelected && (
                                            <div className="absolute top-2 right-2 bg-blue-600 text-white rounded-full p-1 shadow-md z-10">
                                                <Check className="h-3 w-3" />
                                            </div>
                                        )}
                                        
                                        {/* Delete Action - Only visible on hover */}
                                        <div 
                                            className="absolute top-2 left-2 bg-red-600/80 hover:bg-red-600 text-white rounded-full p-1.5 shadow-md opacity-0 group-hover:opacity-100 transition-opacity z-20"
                                            onClick={(e) => {
                                                e.stopPropagation(); // Prevent selection
                                                if (window.confirm("Are you sure you want to delete this image permanently?")) { // Simple confirmation
                                                    const loadingId = toast.loading("Deleting...");
                                                    apiClient.deleteMediaImage(img.source_type, img.id)
                                                        .then(() => {
                                                            toast.success("Image deleted", { id: loadingId });
                                                            // Invalidate query
                                                            queryClient.invalidateQueries({ queryKey: ['media-library'] });
                                                        })
                                                        .catch(err => {
                                                            console.error(err);
                                                            toast.error("Failed to delete", { id: loadingId });
                                                        });
                                                }
                                            }}
                                        >
                                            <Trash2 className="h-3 w-3" />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
                
                {/* Footer */}
                <DialogFooter className="p-4 border-t bg-gray-50 flex items-center justify-between gap-4">
                     <div className="text-sm text-gray-500 flex items-center gap-4">
                        <div className="space-x-2">
                             <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
                             <span className="text-xs">Page {page}</span>
                             <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)} disabled={!data || data.items.length < 20}>Next</Button>
                        </div>
                     </div>
                     <div className="flex items-center gap-2">
                         <span className="text-sm text-gray-600">{selectedIds.length} selected</span>
                         <Button onClick={handleSubmit} disabled={selectedIds.length === 0}>
                            Add Selected Images
                         </Button>
                     </div>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
