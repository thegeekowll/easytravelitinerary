'use client';

import * as React from 'react';
import { Check, ChevronsUpDown, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import { getDestinations, Destination } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';

interface DestinationSelectorProps {
  selectedIds: string[];
  onChange: (ids: string[]) => void;
}

export function DestinationSelector({ selectedIds, onChange }: DestinationSelectorProps) {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState('');

  const { data: destinations = [] } = useQuery({
    queryKey: ['destinations', search],
    queryFn: () => getDestinations(search),
    enabled: open, // only fetch when open
  });

  const selectedDestinations = selectedIds.map((id: string) =>
    destinations.find(d => d.id === id) || { id, name: 'Loading...', country: '' }
  );

  const handleSelect = (currentValue: string) => {
    const isSelected = selectedIds.includes(currentValue);
    if (isSelected) {
      onChange(selectedIds.filter(id => id !== currentValue));
    } else {
      onChange([...selectedIds, currentValue]);
    }
  };

  const removeDestination = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(selectedIds.filter(itemId => itemId !== id));
  };

  return (
    <div className="space-y-2">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between min-h-[40px] h-auto"
          >
            <div className="flex flex-wrap gap-1 justify-start">
              {selectedIds.length === 0 && <span className="text-muted-foreground font-normal">Select destinations...</span>}
              {selectedDestinations.map((dest) => (
                <Badge key={dest.id} variant="secondary" className="mr-1 mb-1">
                  {dest.name}
                  <button
                    className="ml-1 ring-offset-background rounded-full outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        removeDestination(dest.id, e as any);
                      }
                    }}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                    }}
                    onClick={(e) => removeDestination(dest.id, e)}
                  >
                    <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                  </button>
                </Badge>
              ))}
            </div>
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[300px] p-0">
          <Command>
            <CommandInput placeholder="Search destination..." onValueChange={setSearch} />
            <CommandEmpty>No destination found.</CommandEmpty>
            <CommandGroup className="max-h-[200px] overflow-auto">
              {destinations.map((destination: Destination) => (
                <CommandItem
                  key={destination.id}
                  value={destination.id}
                  onSelect={() => handleSelect(destination.id)}
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      selectedIds.includes(destination.id) ? "opacity-100" : "opacity-0"
                    )}
                  />
                  {destination.name}
                  <span className="ml-2 text-xs text-gray-500 truncate">
                    {destination.country}
                  </span>
                </CommandItem>
              ))}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
