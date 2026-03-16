"use client"

import * as React from "react"
import { Check, ChevronsUpDown, PlusCircle } from "lucide-react"

import { cn } from "@/lib/utils/cn"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

interface CreatableComboboxProps {
  options: { value: string; label: string }[]
  value?: string
  onChange: (value: string) => void
  placeholder?: string
  searchPlaceholder?: string
  emptyText?: string
  createLabel?: string
  className?: string
}

export function CreatableCombobox({
  options,
  value,
  onChange,
  placeholder = "Select or type...",
  searchPlaceholder = "Search...",
  emptyText = "No match found.",
  createLabel = "Add",
  className,
}: CreatableComboboxProps) {
  const [open, setOpen] = React.useState(false)
  const [search, setSearch] = React.useState("")

  // Check if typed value matches any existing option (case-insensitive)
  const matchedOption = options.find(
    (o) => o.label.toLowerCase() === search.toLowerCase()
  )
  const filteredOptions = options.filter((o) =>
    o.label.toLowerCase().includes(search.toLowerCase())
  )
  const showCreate = search.trim() !== "" && !matchedOption

  // Display label: find from options or use raw value
  const displayLabel = value
    ? options.find((o) => o.value === value)?.label || value
    : ""

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            "w-full justify-between font-normal",
            !value && "text-muted-foreground",
            className
          )}
        >
          {displayLabel || placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            placeholder={searchPlaceholder}
            value={search}
            onValueChange={setSearch}
          />
          <CommandList>
            {filteredOptions.length === 0 && !showCreate && (
              <CommandEmpty>{emptyText}</CommandEmpty>
            )}
            {filteredOptions.length > 0 && (
              <CommandGroup heading="Existing">
                {filteredOptions.map((option) => (
                  <CommandItem
                    key={option.value}
                    value={option.label}
                    onSelect={() => {
                      onChange(option.value === value ? "" : option.value)
                      setSearch("")
                      setOpen(false)
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === option.value ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {option.label}
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
            {showCreate && (
              <>
                {filteredOptions.length > 0 && <CommandSeparator />}
                <CommandGroup heading="New">
                  <CommandItem
                    value={`create:${search}`}
                    onSelect={() => {
                      const trimmed = search.trim()
                      onChange(trimmed)
                      setSearch("")
                      setOpen(false)
                    }}
                  >
                    <PlusCircle className="mr-2 h-4 w-4 text-primary" />
                    {createLabel} &quot;{search.trim()}&quot;
                  </CommandItem>
                </CommandGroup>
              </>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
