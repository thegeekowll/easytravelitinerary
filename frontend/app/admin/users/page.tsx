'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Plus, Search, User as UserIcon, Trash2, Pencil, Camera, Download, Upload as UploadIcon } from 'lucide-react';
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
  
  // Gallery / Upload State
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  const [isUploadingPhoto, setIsUploadingPhoto] = useState(false);

  const fetchPermissions = async () => {
    try {
      const data = await apiClient.getPermissions();
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
      if (data.items) {
        setUsers(data.items);
      } else {
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

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploadingPhoto(true);
    const toastId = toast.loading('Uploading photo...');
    try {
      const url = await apiClient.uploadMediaFile(file);
      setNewUser(prev => ({ ...prev, profile_photo_url: url }));
      toast.success('Photo uploaded', { id: toastId });
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Upload failed', { id: toastId });
    } finally {
      setIsUploadingPhoto(false);
      e.target.value = '';
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

  const handleExport = async () => {
    try {
      const blob = await apiClient.exportData('users');
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'users.csv');
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      toast.error('Export failed');
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const toastId = toast.loading('Importing users...');
    try {
      const result = await apiClient.importData('users', file);
      toast.success(`Imported ${result.imported_count} users. Failed: ${result.failed_count}`, { id: toastId });
      fetchUsers();
    } catch (error) {
      toast.error('Import failed', { id: toastId });
    }
    e.target.value = '';
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
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            CSV Ex
          </Button>
          <div>
            <input type="file" id="import-users" accept=".csv" className="hidden" onChange={handleImport} />
            <Button variant="outline" onClick={() => document.getElementById('import-users')?.click()}>
              <UploadIcon className="h-4 w-4 mr-2" />
              CSV Im
            </Button>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => {
                setEditingId(null);
                setNewUser({ email: '', full_name: '', password: '', phone_number: '', profile_photo_url: '', position: '', role: 'cs_agent', permission_ids: [] });
              }}>
                <Plus className="h-4 w-4 mr-2" />
                Add
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
            <DialogHeader>
              <DialogTitle>{editingId ? 'Edit User' : 'Create New User'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSaveUser} className="space-y-4 py-4 overflow-y-auto flex-1 px-2">
              
              {/* Profile Image Picker */}
              <div className="flex flex-col items-center justify-center space-y-3 mb-6">
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
                    {isUploadingPhoto && (
                        <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                            <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        </div>
                    )}
                </div>
                <div className="flex gap-2">
                    {/* Upload from device */}
                    <input
                        type="file"
                        id="profile-photo-upload"
                        accept="image/*"
                        className="hidden"
                        onChange={handlePhotoUpload}
                        disabled={isUploadingPhoto}
                    />
                    <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        disabled={isUploadingPhoto}
                        onClick={() => document.getElementById('profile-photo-upload')?.click()}
                    >
                        <UploadIcon className="h-3.5 w-3.5 mr-1.5" />
                        Upload
                    </Button>
                    {/* Pick from gallery */}
                    <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        disabled={isUploadingPhoto}
                        onClick={() => setIsGalleryOpen(true)}
                    >
                        <Camera className="h-3.5 w-3.5 mr-1.5" />
                        Gallery
                    </Button>
                    {/* Clear photo */}
                    {newUser.profile_photo_url && (
                        <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-600"
                            onClick={() => setNewUser(prev => ({ ...prev, profile_photo_url: '' }))}
                        >
                            Remove
                        </Button>
                    )}
                </div>
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
                  <div className="flex items-center justify-between mb-4">
                    <Label className="text-lg font-semibold">Permissions</Label>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        className="text-xs text-primary hover:underline font-medium"
                        onClick={() => setNewUser({...newUser, permission_ids: permissions.map((p: any) => p.id)})}
                      >
                        Grant All
                      </button>
                      <span className="text-gray-300">|</span>
                      <button
                        type="button"
                        className="text-xs text-gray-500 hover:underline font-medium"
                        onClick={() => setNewUser({...newUser, permission_ids: []})}
                      >
                        Revoke All
                      </button>
                    </div>
                  </div>
                  {permissions.length === 0 ? (
                    <div className="text-sm text-amber-600 bg-amber-50 p-2 rounded">
                      No permissions loaded. Go to Settings and seed permissions first.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(permissions.reduce((acc: any, perm: any) => {
                        const cat = perm.category || 'other';
                        if (!acc[cat]) acc[cat] = [];
                        acc[cat].push(perm);
                        return acc;
                      }, {})).sort(([a], [b]) => {
                        const order = ['itinerary', 'destination', 'accommodation', 'tour_package', '2d_table', 'analytics', 'user_management', 'system'];
                        return (order.indexOf(a) === -1 ? 99 : order.indexOf(a)) - (order.indexOf(b) === -1 ? 99 : order.indexOf(b));
                      }).map(([category, perms]: [string, any]) => {
                        const catPermIds = perms.map((p: any) => p.id);
                        const allChecked = catPermIds.every((id: string) => newUser.permission_ids?.includes(id));
                        const someChecked = catPermIds.some((id: string) => newUser.permission_ids?.includes(id));

                        const categoryLabels: Record<string, string> = {
                          itinerary: 'Itineraries',
                          destination: 'Destinations',
                          accommodation: 'Accommodations',
                          tour_package: 'Base Tours',
                          '2d_table': '2D Matrix',
                          analytics: 'Analytics',
                          user_management: 'User Management',
                          system: 'System & Settings',
                        };

                        const permissionLabels: Record<string, string> = {
                          create_itinerary: 'Create',
                          edit_itinerary: 'Edit',
                          delete_itinerary: 'Delete',
                          view_all_itineraries: 'View All (not just own)',
                          send_email: 'Send Email',
                          generate_pdf: 'Generate PDF',
                          view_destinations: 'View',
                          add_destination: 'Add',
                          edit_destination: 'Edit',
                          delete_destination: 'Delete',
                          view_accommodations: 'View',
                          add_accommodation: 'Add',
                          edit_accommodation: 'Edit',
                          delete_accommodation: 'Delete',
                          view_tour_packages: 'View',
                          add_tour_package: 'Add',
                          edit_tour_package: 'Edit',
                          delete_tour_package: 'Delete',
                          view_2d_table: 'View',
                          edit_2d_table: 'Edit',
                          view_analytics: 'View Dashboard',
                          view_analytics_revenue: 'View Revenue',
                          export_analytics: 'Export Reports',
                          view_users: 'View Users',
                          manage_users: 'Create/Edit/Delete Users',
                          manage_agent_types: 'Settings & Config',
                          view_activity_logs: 'Activity Logs',
                        };

                        return (
                          <div key={category} className="border rounded-lg p-3 bg-gray-50/50">
                            <div className="flex items-center justify-between border-b pb-2 mb-3">
                              <h4 className="text-sm font-bold text-gray-700 uppercase tracking-wider">
                                {categoryLabels[category] || category.replace(/_/g, ' ')}
                              </h4>
                              <input
                                type="checkbox"
                                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                checked={allChecked}
                                ref={(el) => { if (el) el.indeterminate = someChecked && !allChecked; }}
                                onChange={(e) => {
                                  const current = newUser.permission_ids || [];
                                  if (e.target.checked) {
                                    const merged = [...new Set([...current, ...catPermIds])];
                                    setNewUser({...newUser, permission_ids: merged});
                                  } else {
                                    setNewUser({...newUser, permission_ids: current.filter((id: string) => !catPermIds.includes(id))});
                                  }
                                }}
                                title={allChecked ? 'Uncheck all in this section' : 'Check all in this section'}
                              />
                            </div>
                            <div className="grid grid-cols-1 gap-2">
                              {perms.map((perm: any) => (
                                <div key={perm.id} className="flex items-start space-x-2">
                                  <input
                                      type="checkbox"
                                      id={`perm-${perm.id}`}
                                      className="mt-0.5 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                      checked={newUser.permission_ids?.includes(perm.id)}
                                      onChange={(e) => {
                                        const current = newUser.permission_ids || [];
                                        if (e.target.checked) {
                                          setNewUser({...newUser, permission_ids: [...current, perm.id]});
                                        } else {
                                          setNewUser({...newUser, permission_ids: current.filter((id: string) => id !== perm.id)});
                                        }
                                      }}
                                  />
                                  <label htmlFor={`perm-${perm.id}`} className="text-sm leading-tight cursor-pointer">
                                      <span className="font-medium text-gray-900">{permissionLabels[perm.name] || perm.name.replace(/_/g, ' ')}</span>
                                      {perm.description && <span className="block text-xs text-gray-500">{perm.description}</span>}
                                  </label>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
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
                    <div className="bg-primary/10 p-0.5 rounded-full h-10 w-10 flex-shrink-0 overflow-hidden relative">
                      {user.profile_photo_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={user.profile_photo_url} alt={user.full_name} className="h-full w-full object-cover" />
                      ) : (
                        <div className="h-full w-full flex items-center justify-center bg-primary/10 text-primary">
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
                            className="h-8 w-8 text-gray-400 hover:text-primary"
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
