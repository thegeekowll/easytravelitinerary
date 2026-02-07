'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMatrixGrid, updateCombination, createCombination } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { Loader2, Plus } from 'lucide-react';

interface GridData {
  rows: Array<{ id: string; name: string }>;
  cols: Array<{ id: string; name: string }>;
  combinations: Record<string, { id: string; description_content?: string; activity_content?: string }>;
}

export default function MatrixPage() {
  const queryClient = useQueryClient();
  const [isBidirectional, setIsBidirectional] = useState(false);
  const [selectedCell, setSelectedCell] = useState<{
    rowId: string;
    colId: string;
    rowName: string;
    colName: string;
    combinationId?: string;
    description: string;
    activity: string;
  } | null>(null);

  const { data: grid, isLoading, error } = useQuery<GridData>({
    queryKey: ['matrix-grid'],
    queryFn: () => getMatrixGrid(0, 0), // Fetch first page for now
  });

  const updateMutation = useMutation({
    mutationFn: (data: { id: string; description: string; activity: string; bidirectional: boolean }) =>
      updateCombination(data.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matrix-grid'] });
      toast.success('Combination updated');
      setSelectedCell(null);
      setIsBidirectional(false);
    },
    onError: () => toast.error('Failed to update'),
  });

  const createMutation = useMutation({
    mutationFn: (data: { dest1Id: string; dest2Id?: string; description: string; activity: string; bidirectional: boolean }) =>
      createCombination(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matrix-grid'] });
      toast.success('Combination created');
      setSelectedCell(null);
      setIsBidirectional(false);
    },
    onError: () => toast.error('Failed to create'),
  });

  const handleCellClick = (rowId: string, colId: string, rowName: string, colName: string) => {
    // Key format must match api.ts logic: rowId_colId
    const key = `${rowId}_${colId}`;
    const combo = grid?.combinations[key];

    setSelectedCell({
      rowId,
      colId,
      rowName,
      colName,
      combinationId: combo?.id,
      description: combo?.description_content || '',
      activity: combo?.activity_content || '',
    });
    setIsBidirectional(false); // Reset default
  };

  const handleSave = () => {
    if (!selectedCell) return;

    if (selectedCell.combinationId) {
      updateMutation.mutate({
        id: selectedCell.combinationId,
        description: selectedCell.description,
        activity: selectedCell.activity,
        bidirectional: isBidirectional,
      });
    } else {
      createMutation.mutate({
        dest1Id: selectedCell.rowId,
        dest2Id: selectedCell.rowId === selectedCell.colId ? undefined : selectedCell.colId,
        description: selectedCell.description,
        activity: selectedCell.activity,
        bidirectional: isBidirectional,
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-red-500">
        <h3 className="font-bold">Error loading matrix</h3>
        <p>{error instanceof Error ? error.message : 'Unknown error'}</p>
        <pre className="mt-2 text-xs bg-gray-100 p-2 rounded">
          {JSON.stringify(error, null, 2)}
        </pre>
      </div>
    );
  }

  if (!grid) return <div>Failed to load matrix (No Data)</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Destination Matrix</h1>
          <p className="text-gray-600">Manage descriptions and activities for destination pairs.</p>
        </div>
      </div>

      <div className="overflow-x-auto border rounded-lg shadow-sm bg-white">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10 border-r">
                Destination
              </th>
              {grid.cols.map((col) => (
                <th key={col.id} className="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                  {col.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {grid.rows.map((row) => (
              <tr key={row.id}>
                <td className="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white border-r z-10">
                  {row.name}
                </td>
                {grid.cols.map((col) => {
                  const key = `${row.id}_${col.id}`;
                  const combo = grid.combinations[key];
                  const isDiagonal = row.id === col.id;
                  
                  return (
                    <td 
                      key={col.id} 
                      className={`px-3 py-2 whitespace-nowrap text-sm border-l hover:bg-blue-50 cursor-pointer ${
                        !combo ? 'bg-gray-50' : ''
                      } ${isDiagonal ? 'bg-blue-50/50' : ''}`}
                      onClick={() => handleCellClick(row.id, col.id, row.name, col.name)}
                    >
                      {combo ? (
                        <div className="max-w-[150px] truncate text-xs">
                          {combo.description_content ? (
                            <span className="text-green-600">✓ Content</span>
                          ) : (
                             <span className="text-orange-400">⚠ Empty</span>
                          )}
                        </div>
                      ) : (
                        <div className="text-center text-gray-300">
                          <Plus className="h-4 w-4 mx-auto" />
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Editor Dialog */}
      <Dialog open={!!selectedCell} onOpenChange={(open) => !open && setSelectedCell(null)}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>
              {selectedCell?.rowId === selectedCell?.colId 
                ? `Edit: ${selectedCell?.rowName}`
                : `Edit Pair: ${selectedCell?.rowName} + ${selectedCell?.colName}`
              }
            </DialogTitle>
            <DialogDescription>
              Define the automated content required for this destination combination.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            {/* Bidirectional Option */}
            {selectedCell?.rowId !== selectedCell?.colId && (
              <div className="flex items-center space-x-2 pb-2 border-b">
                <Checkbox 
                  id="bidirectional" 
                  checked={isBidirectional}
                  onCheckedChange={(checked) => setIsBidirectional(checked as boolean)}
                />
                <div className="grid gap-1.5 leading-none">
                  <Label htmlFor="bidirectional" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Apply to both directions (Bidirectional)
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    If checked, this content will also be applied to {selectedCell?.colName} → {selectedCell?.rowName}.
                  </p>
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea 
                placeholder="Enter a captivating description for this combination..."
                className="h-32"
                value={selectedCell?.description || ''}
                onChange={(e) => setSelectedCell(prev => prev ? { ...prev, description: e.target.value } : null)}
              />
            </div>
            <div className="space-y-2">
              <Label>Activity / Highlights</Label>
              <Textarea 
                placeholder="List key activities and highlights..."
                className="h-32"
                value={selectedCell?.activity || ''}
                 onChange={(e) => setSelectedCell(prev => prev ? { ...prev, activity: e.target.value } : null)}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedCell(null)}>Cancel</Button>
            <Button onClick={handleSave} disabled={updateMutation.isPending || createMutation.isPending}>
              {updateMutation.isPending || createMutation.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
