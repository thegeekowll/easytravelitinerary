'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Plus, Search, User as UserIcon, Trash2, Pencil, Camera } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from '@/components/ui/label';
import ImageGalleryModal from '@/components/shared/image-gallery-modal';

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newUser, setNewUser] = useState({
    email: '',
    full_name: '',
    password: '',
    phone_number: '',
    profile_photo_url: '',
    position: '',
    role: 'cs_agent',
    permission_ids: [] as string[]
  });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [permissions, setPermissions] = useState<any[]>([]);
  
  // Gallery State
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);

  const fetchPermissions = async () => {
    try {
      const data = await apiClient.getPermissions();
      console.log('Permissions fetched:', data);
      setPermissions(data);
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
      toast.error('Failed to load permissions configuration');
    }
  };

  useEffect(() => {
    fetchPermissions();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getUsers();
      console.log('API Response Data:', data);
      if (data.items) {
        console.log('Items found:', data.items.length);
        setUsers(data.items);
      } else {
        console.error('No items in response data:', data);
        setUsers([]);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleSaveUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        const updateData: any = { ...newUser };
        if (!updateData.password) delete updateData.password;
        
        await apiClient.updateUser(editingId, updateData);
        toast.success('User updated successfully');
      } else {
        await apiClient.createUser(newUser);
        toast.success('User created successfully');
      }
      setIsDialogOpen(false);
      setNewUser({ email: '', full_name: '', password: '', phone_number: '', profile_photo_url: '', position: '', role: 'cs_agent', permission_ids: [] });
      setEditingId(null);
      fetchUsers();
    } catch (error: any) {
      console.error('Save user failed:', error);
      toast.error(error.response?.data?.detail || 'Failed to save user');
    }
  };

  const handleEditClick = async (user: any) => {
    const toastId = toast.loading('Loading user details...');
    try {
      // Fetch full user details to get permissions
      const userDetails = await apiClient.getUser(user.id);
      const userPermissionIds = userDetails.permissions ? userDetails.permissions.map((p: any) => p.id) : [];

      setNewUser({
        email: userDetails.email,
        full_name: userDetails.full_name,
        phone_number: userDetails.phone_number || '',
        profile_photo_url: userDetails.profile_photo_url || '',
        position: userDetails.position || '',
        password: '',
        role: userDetails.role?.name || userDetails.role || 'cs_agent',
        permission_ids: userPermissionIds
      });
      setEditingId(user.id);
      setIsDialogOpen(true);
      toast.dismiss(toastId);
    } catch (error) {
      console.error('Failed to fetch user details:', error);
      toast.error('Failed to load user details', { id: toastId });
    }
  };

  const handleGallerySelect = (images: {url: string, caption?: string}[]) => {
    if (images && images.length > 0) {
      setNewUser(prev => ({ ...prev, profile_photo_url: images[0].url }));
      setIsGalleryOpen(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;
    
    const toastId = toast.loading('Deleting user...');
    try {
      await apiClient.deleteUser(userId);
      toast.success('User deleted', { id: toastId });
      fetchUsers();
    } catch (error: any) {
      console.error('Delete user failed:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete user', { id: toastId });
    }
  };

  const filteredUsers = users.filter(user => 
    user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage system users and their roles (Total: {users.length})</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => {
              setEditingId(null);
              setNewUser({ email: '', full_name: '', password: '', phone_number: '', profile_photo_url: '', position: '', role: 'cs_agent', permission_ids: [] });
            }}>
              <Plus className="h-4 w-4 mr-2" />
              Add User
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
            <DialogHeader>
              <DialogTitle>{editingId ? 'Edit User' : 'Create New User'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSaveUser} className="space-y-4 py-4 overflow-y-auto flex-1 px-2">
              
              {/* Profile Image Picker */}
              <div className="flex flex-col items-center justify-center space-y-4 mb-6">
                <div className="relative h-24 w-24 rounded-full overflow-hidden border-2 border-gray-100 bg-gray-50 group">
                    {newUser.profile_photo_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img 
                            src={newUser.profile_photo_url} 
                            alt="Profile" 
                            className="h-full w-full object-cover" 
                        />
                    ) : (
                        <div className="h-full w-full flex items-center justify-center">
                            <UserIcon className="h-10 w-10 text-gray-300" />
                        </div>
                    )}
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer" onClick={() => setIsGalleryOpen(true)}>
                        <Camera className="text-white h-6 w-6" />
                    </div>
                </div>
                <Button type="button" variant="outline" size="sm" onClick={() => setIsGalleryOpen(true)}>
                    {newUser.profile_photo_url ? 'Change Photo' : 'Select Photo'}
                </Button>
              </div>

              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input 
                  id="full_name"
                  value={newUser.full_name}
                  onChange={(e) => setNewUser({...newUser, full_name: e.target.value})}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input 
                  id="email"
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone_number">Phone Number</Label>
                <Input 
                  id="phone_number"
                  type="tel"
                  placeholder="+1234567890"
                  value={newUser.phone_number}
                  onChange={(e) => setNewUser({...newUser, phone_number: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="position">Position / Job Title</Label>
                <Input 
                  id="position"
                  placeholder="e.g. Senior Safari Specialist"
                  value={newUser.position || ''}
                  onChange={(e) => setNewUser({...newUser, position: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input 
                  id="password"
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                  required={!editingId}
                  minLength={8}
                />
                <p className="text-xs text-gray-500">
                  {editingId ? 'Leave blank to keep current password' : 'Min 8 chars, 1 uppercase, 1 special'}
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <select 
                  id="role"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={newUser.role}
                  onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                >
                  <option value="cs_agent">CS Agent</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              {(newUser.role === 'cs_agent' || newUser.role === 'CS_AGENT') && (
                <div className="pt-6 border-t mt-4">
                  <Label className="text-lg font-semibold block mb-4">Permissions</Label>
                  {permissions.length === 0 ? (
                    <div className="text-sm text-amber-600 bg-amber-50 p-2 rounded">
                      No permissions loaded. Ensure the backend has seeded permissions.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {Object.entries(permissions.reduce((acc: any, perm: any) => {
                        const cat = perm.category || 'Other';
                        if (!acc[cat]) acc[cat] = [];
                        acc[cat].push(perm);
                        return acc;
                      }, {})).map(([category, perms]: [string, any]) => (
                        <div key={category} className="space-y-2 border rounded-lg p-3 bg-gray-50/50">
                          <h4 className="text-sm font-bold text-gray-700 uppercase tracking-wider border-b pb-2 mb-2">
                            {category.replace(/_/g, ' ')}
                          </h4>
                          <div className="grid grid-cols-1 gap-2">
                            {perms.map((perm: any) => (
                              <div key={perm.id} className="flex items-start space-x-2">
                                <input
                                    type="checkbox"
                                    id={`perm-${perm.id}`}
                                    className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                    checked={newUser.permission_ids?.includes(perm.id)}
                                    onChange={(e) => {
                                      const current = newUser.permission_ids || [];
                                      if (e.target.checked) {
                                        setNewUser({...newUser, permission_ids: [...current, perm.id]});
                                      } else {
                                        setNewUser({...newUser, permission_ids: current.filter(id => id !== perm.id)});
                                      }
                                    }}
                                />
                                <label htmlFor={`perm-${perm.id}`} className="text-sm leading-tight cursor-pointer pb-1">
                                    <span className="font-medium text-gray-900">{perm.name}</span>
                                    {perm.description && <span className="block text-xs text-gray-500">{perm.description}</span>}
                                </label>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              <Button type="submit" className="w-full">
                {editingId ? 'Update User' : 'Create User'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            placeholder="Search users..."
            className="pl-9"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <p>Loading users...</p>
        ) : filteredUsers.length > 0 ? (
          filteredUsers.map((user) => (
            <Card key={user.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="bg-blue-100 p-0.5 rounded-full h-10 w-10 flex-shrink-0 overflow-hidden relative">
                      {user.profile_photo_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={user.profile_photo_url} alt={user.full_name} className="h-full w-full object-cover" />
                      ) : (
                        <div className="h-full w-full flex items-center justify-center bg-blue-100 text-blue-600">
                            <UserIcon className="h-5 w-5" />
                        </div>
                      )}
                    </div>
                    <div className="overflow-hidden">
                      <p className="font-semibold truncate pr-2">{user.full_name}</p>
                      <p className="text-sm text-gray-500 truncate">{user.email}</p>
                      {user.phone_number && <p className="text-xs text-gray-400 mt-0.5">{user.phone_number}</p>}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                        user.role?.name === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                    }`}>
                        {user.role?.name || user.role}
                    </span>
                    <div className="flex gap-1">
                        <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8 text-gray-400 hover:text-blue-500"
                            onClick={() => handleEditClick(user)}
                        >
                            <Pencil className="h-4 w-4" />
                        </Button>
                        <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8 text-gray-400 hover:text-red-500"
                            onClick={() => handleDeleteUser(user.id)}
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>
                  </div>
                </div>
                <div className="mt-4 text-xs text-gray-500">
                  Last login: {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <p className="col-span-full text-center py-8 text-gray-500">No users found.</p>
        )}
      </div>

      <ImageGalleryModal
        open={isGalleryOpen}
        onOpenChange={setIsGalleryOpen}
        onSelect={handleGallerySelect}
        limit={1}
      />
    </div>
  );
}
