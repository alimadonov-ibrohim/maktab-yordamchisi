const ADMIN_ROLES = ['super_admin', 'admin', 'school_admin'];

export function hasAdminAccess(role: string): boolean {
  return ADMIN_ROLES.includes(role);
}

export function isSuperAdmin(role: string): boolean {
  return role === 'super_admin';
}

export const ROLE_NAMES: Record<string, string> = {
  super_admin: 'Super Admin',
  admin: 'Admin',
  school_admin: 'School Admin',
  teacher: "O'qituvchi",
  parent: 'Ota-ona',
};
