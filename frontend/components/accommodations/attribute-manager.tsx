'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Trash2, Loader2, Settings } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import toast from 'react-hot-toast';

interface AttributeManagerProps {
    title: string;
    items: any[];
    onCreate: (data: { name: string; description?: string }) => Promise<any>;
    onDelete: (id: string) => Promise<any>;
    onRefresh: () => void;
}

export default function AttributeManager({ title, items, onCreate, onDelete, onRefresh }: AttributeManagerProps) {
    const [loading, setLoading] = useState(false);
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await onCreate({ name: newName, description: newDesc });
            toast.success(`${title} created successfully`);
            setNewName('');
            setNewDesc('');
            onRefresh();
        } catch (error: any) {
            console.error(error);
            toast.error(error.response?.data?.detail || 'Failed to create item');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this item?')) return;
        try {
            await onDelete(id);
            toast.success('Item deleted');
            onRefresh();
        } catch (error: any) {
             toast.error(error.response?.data?.detail || 'Failed to delete item');
        }
    };

    return (
        <div className="space-y-4">
             <form onSubmit={handleCreate} className="flex gap-2 items-end bg-gray-50 p-3 rounded-md">
                <div className="space-y-1 flex-1">
                    <Label className="text-xs">Name</Label>
                    <Input 
                        value={newName} 
                        onChange={(e) => setNewName(e.target.value)} 
                        placeholder={`New ${title}...`}
                        className="h-8"
                        required
                    />
                </div>
                <div className="space-y-1 flex-[2]">
                    <Label className="text-xs">Description</Label>
                    <Input 
                         value={newDesc} 
                         onChange={(e) => setNewDesc(e.target.value)} 
                         placeholder="Description (optional)"
                         className="h-8"
                    />
                </div>
                <Button type="submit" size="sm" disabled={loading}>
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                </Button>
            </form>

            <div className="border rounded-md max-h-[300px] overflow-auto">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>Description</TableHead>
                            <TableHead className="w-[50px]"></TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {items.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={3} className="text-center text-gray-500 py-4">
                                    No items found.
                                </TableCell>
                            </TableRow>
                        ) : (
                            items.map((item) => (
                                <TableRow key={item.id}>
                                    <TableCell className="font-medium">{item.name}</TableCell>
                                    <TableCell className="text-muted-foreground text-sm">{item.description}</TableCell>
                                    <TableCell>
                                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-red-500 hover:text-red-700" onClick={() => handleDelete(item.id)}>
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
