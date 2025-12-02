import React, { useState, useEffect } from 'react';
import { Check, ChevronsUpDown, Search } from 'lucide-react';
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
import { documentService } from '@/services/documents';
import type { User } from '@/types/document';
import { toast } from 'sonner';

interface UserPickerProps {
    value?: string[];
    onChange: (userIds: string[]) => void;
    multiple?: boolean;
    placeholder?: string;
    className?: string;
}

export const UserPicker: React.FC<UserPickerProps> = ({
    value = [],
    onChange,
    multiple = false,
    placeholder = 'Select user...',
    className,
}) => {
    const [open, setOpen] = useState(false);
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState('');

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            setLoading(true);
            const data = await documentService.getUsers();
            setUsers(data);
        } catch (error) {
            toast.error('Failed to load users');
            console.error('Error loading users:', error);
        } finally {
            setLoading(false);
        }
    };

    const selectedUsers = users.filter(user => value.includes(user.id));

    const handleSelect = (userId: string) => {
        if (multiple) {
            const newValue = value.includes(userId)
                ? value.filter(id => id !== userId)
                : [...value, userId];
            onChange(newValue);
        } else {
            onChange(value.includes(userId) ? [] : [userId]);
            setOpen(false);
        }
    };

    const displayText = selectedUsers.length > 0
        ? multiple
            ? `${selectedUsers.length} selected`
            : selectedUsers[0].full_name
        : placeholder;

    return (
        <div className={cn('space-y-2', className)}>
            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        className="w-full justify-between"
                    >
                        <span className="truncate">{displayText}</span>
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0" align="start">
                    <Command>
                        <CommandInput
                            placeholder="Search users..."
                            value={search}
                            onValueChange={setSearch}
                        />
                        <CommandEmpty>
                            {loading ? 'Loading...' : 'No users found.'}
                        </CommandEmpty>
                        <CommandGroup className="max-h-64 overflow-auto">
                            {users.map((user) => (
                                <CommandItem
                                    key={user.id}
                                    value={user.id}
                                    onSelect={() => handleSelect(user.id)}
                                >
                                    <Check
                                        className={cn(
                                            'mr-2 h-4 w-4',
                                            value.includes(user.id) ? 'opacity-100' : 'opacity-0'
                                        )}
                                    />
                                    <div className="flex flex-col">
                                        <span className="font-medium">{user.full_name}</span>
                                        <span className="text-xs text-muted-foreground">
                                            {user.email}
                                            {user.designation && ` • ${user.designation}`}
                                            {user.division && ` • ${user.division}`}
                                        </span>
                                    </div>
                                </CommandItem>
                            ))}
                        </CommandGroup>
                    </Command>
                </PopoverContent>
            </Popover>

            {/* Display selected users as badges */}
            {multiple && selectedUsers.length > 0 && (
                <div className="flex flex-wrap gap-2">
                    {selectedUsers.map((user) => (
                        <Badge
                            key={user.id}
                            variant="secondary"
                            className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors"
                            onClick={() => handleSelect(user.id)}
                        >
                            {user.full_name}
                            <span className="ml-1 text-xs">×</span>
                        </Badge>
                    ))}
                </div>
            )}
        </div>
    );
};
