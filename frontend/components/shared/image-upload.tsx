'use client';

import { useState, useRef } from 'react';
import { Upload, X, ImageIcon } from 'lucide-react';
import ImageGalleryModal from '@/components/shared/image-gallery-modal';

interface ImageUploadProps {
  onImagesSelected: (files: File[]) => void;
  onGalleryImagesSelected?: (urls: string[]) => void;
  maxFiles?: number;
  existingImages?: { id: string; url?: string; image_url?: string; caption?: string }[];
  onDeleteExisting?: (id: string) => void;
  disabled?: boolean;
}

export default function ImageUpload({
  onImagesSelected,
  onGalleryImagesSelected,
  maxFiles = 5,
  existingImages = [],
  onDeleteExisting,
  disabled = false
}: ImageUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [galleryUrls, setGalleryUrls] = useState<string[]>([]);
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const totalCount = existingImages.length + selectedFiles.length + galleryUrls.length;

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      if (totalCount + newFiles.length > maxFiles) {
        alert(`You can only have up to ${maxFiles} images total.`);
        return;
      }

      setSelectedFiles(prev => [...prev, ...newFiles]);
      onImagesSelected([...selectedFiles, ...newFiles]);

      // Create previews
      newFiles.forEach(file => {
        const reader = new FileReader();
        reader.onloadend = () => {
          setPreviews(prev => [...prev, reader.result as string]);
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    const newPreviews = previews.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    setPreviews(newPreviews);
    onImagesSelected(newFiles);
  };

  const removeGalleryUrl = (index: number) => {
    const newUrls = galleryUrls.filter((_, i) => i !== index);
    setGalleryUrls(newUrls);
    onGalleryImagesSelected?.(newUrls);
  };

  const handleGallerySelect = (images: { url: string; caption?: string }[]) => {
    const remaining = maxFiles - totalCount;
    const newUrls = images.slice(0, remaining).map(img => img.url);
    const updated = [...galleryUrls, ...newUrls];
    setGalleryUrls(updated);
    onGalleryImagesSelected?.(updated);
    setIsGalleryOpen(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        {/* Existing Images */}
        {existingImages.map((img) => {
          const src = img.url || img.image_url || '';
          return (
            <div key={img.id} className="relative w-28 h-28 rounded-lg overflow-hidden border bg-gray-100 group">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={src}
                alt={img.caption || 'Image'}
                className="w-full h-full object-cover"
              />
              {onDeleteExisting && !disabled && (
                <button
                  type="button"
                  onClick={() => onDeleteExisting(img.id)}
                  className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
          );
        })}

        {/* Gallery Selected Images */}
        {galleryUrls.map((url, index) => (
          <div key={`gallery-${index}`} className="relative w-28 h-28 rounded-lg overflow-hidden border border-primary/30 bg-gray-100 group">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={url}
              alt="Gallery selection"
              className="w-full h-full object-cover"
            />
            {!disabled && (
              <button
                type="button"
                onClick={() => removeGalleryUrl(index)}
                className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </div>
        ))}

        {/* New File Previews */}
        {previews.map((preview, index) => (
          <div key={`new-${index}`} className="relative w-28 h-28 rounded-lg overflow-hidden border bg-gray-100 group">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={preview}
              alt="New upload"
              className="w-full h-full object-cover"
            />
            {!disabled && (
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </div>
        ))}

        {/* Action Buttons */}
        {totalCount < maxFiles && !disabled && (
          <div className="flex gap-2">
            {/* Upload from device */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className="w-28 h-28 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-primary hover:bg-gray-50 transition-colors"
            >
              <Upload className="h-6 w-6 text-gray-400 mb-1" />
              <span className="text-[10px] text-gray-500 font-medium text-center px-1">Upload</span>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept="image/*"
                multiple
                onChange={handleFileSelect}
              />
            </div>

            {/* Pick from gallery */}
            <div
              onClick={() => setIsGalleryOpen(true)}
              className="w-28 h-28 border-2 border-dashed border-primary/30 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-primary hover:bg-primary/5 transition-colors"
            >
              <ImageIcon className="h-6 w-6 text-primary/50 mb-1" />
              <span className="text-[10px] text-primary/70 font-medium text-center px-1">Gallery</span>
            </div>
          </div>
        )}
      </div>

      <ImageGalleryModal
        open={isGalleryOpen}
        onOpenChange={setIsGalleryOpen}
        onSelect={handleGallerySelect}
        limit={maxFiles - totalCount}
      />
    </div>
  );
}
