'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Edit, Trash2, Plus, User, Star } from 'lucide-react';
import TravelerDialog from './traveler-dialog';
import apiClient from '@/lib/api/client';
import toast from 'react-hot-toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface TravelersListProps {
  itineraryId: string;
  travelers: any[];
  onUpdate: () => void; // Trigger refresh
  isEditing: boolean;
}

export default function TravelersList({ itineraryId, travelers, onUpdate, isEditing }: TravelersListProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTraveler, setEditingTraveler] = useState<any>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const handleAdd = () => {
    setEditingTraveler(null);
    setIsDialogOpen(true);
  };

  const handleEdit = (traveler: any) => {
    setEditingTraveler(traveler);
    setIsDialogOpen(true);
  };

  const handleDeleteClick = (id: string) => {
    setDeleteId(id);
  };

  const confirmDelete = async () => {
    if (!deleteId) return;
    try {
      await apiClient.deleteTraveler(itineraryId, deleteId);
      toast.success("Traveler deleted");
      onUpdate();
    } catch (error) {
      console.error("Failed to delete traveler:", error);
      toast.error("Failed to delete traveler");
    } finally {
      setDeleteId(null);
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
                <CardTitle>Travelers</CardTitle>
                <CardDescription>Manage traveler details and preferences</CardDescription>
            </div>
            {isEditing && (
              <Button size="sm" onClick={handleAdd}>
                <Plus className="h-4 w-4 mr-2" />
                Add Traveler
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {travelers.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <User className="h-12 w-12 mx-auto mb-2 opacity-20" />
              <p>No travelers added yet.</p>
              {isEditing && (
                <Button variant="link" onClick={handleAdd}>Add the first traveler</Button>
              )}
            </div>
          ) : (
            <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead className="hidden md:table-cell">Contact</TableHead>
                  <TableHead className="hidden md:table-cell">Details</TableHead>
                  <TableHead>Status</TableHead>
                  {isEditing && <TableHead className="text-right">Actions</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {travelers.map((traveler) => (
                  <TableRow key={traveler.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        {traveler.full_name}
                        {traveler.is_primary && (
                            <Star className="h-3 w-3 text-yellow-500 fill-yellow-500" />
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="hidden md:table-cell">
                      <div className="text-sm">
                        {traveler.email && <div className="text-gray-600">{traveler.email}</div>}
                        {traveler.phone && <div className="text-gray-500">{traveler.phone}</div>}
                      </div>
                    </TableCell>
                    <TableCell className="hidden md:table-cell">
                        <div className="text-sm">
                            {traveler.age && <span className="mr-2">Age: {traveler.age}</span>}
                            {traveler.nationality && <span>{traveler.nationality}</span>}
                            {traveler.special_requests && (
                                <div className="text-xs text-orange-600 mt-1 max-w-[200px] truncate" title={traveler.special_requests}>
                                    Note: {traveler.special_requests}
                                </div>
                            )}
                        </div>
                    </TableCell>
                    <TableCell>
                        {traveler.is_primary ? (
                            <Badge variant="default" className="text-xs">Primary</Badge>
                        ) : (
                            <span className="text-muted-foreground text-xs">Guest</span>
                        )}
                    </TableCell>
                    {isEditing && (
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEdit(traveler)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-500 hover:text-red-600"
                          onClick={() => handleDeleteClick(traveler.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <TravelerDialog
        key={editingTraveler?.id || 'new'}
        isOpen={isDialogOpen}
        onClose={() => {
            setIsDialogOpen(false);
            setEditingTraveler(null);
        }}
        onSuccess={() => {
            onUpdate();
        }}
        itineraryId={itineraryId}
        travelerToEdit={editingTraveler}
        defaultNationality={travelers.find((t: any) => t.is_primary)?.nationality}
      />
      
      <AlertDialog open={!!deleteId} onOpenChange={(open) => !open && setDeleteId(null)}>
        <AlertDialogContent>
            <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
                This will permanently delete this traveler from the itinerary.
            </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-red-600 hover:bg-red-700">Delete</AlertDialogAction>
            </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
