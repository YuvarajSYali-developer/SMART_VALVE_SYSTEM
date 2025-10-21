# System Credentials

## Default Users

### Primary Admin Account
- **Username**: `yuvarajyali@gmail`
- **Password**: `SMART_VALVE_SYSTEM`
- **Role**: Admin
- **Permissions**: Full access (valve control, force open, reset emergency, view all)

### Alternative Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Admin
- **Permissions**: Full access

### Operator Account
- **Username**: `operator`
- **Password**: `operator123`
- **Role**: Operator
- **Permissions**: Open/close valve, view data (cannot force open or reset emergency)

### Viewer Account
- **Username**: `viewer`
- **Password**: `viewer123`
- **Role**: Viewer
- **Permissions**: Read-only access (no valve control)

---

## Role Permissions Matrix

| Action | Admin | Operator | Viewer |
|--------|-------|----------|--------|
| View Status | ✅ | ✅ | ✅ |
| View Telemetry | ✅ | ✅ | ✅ |
| View Alerts | ✅ | ✅ | ✅ |
| Open Valve | ✅ | ✅ | ❌ |
| Close Valve | ✅ | ✅ | ❌ |
| Force Open | ✅ | ❌ | ❌ |
| Reset Emergency | ✅ | ❌ | ❌ |
| View Operations Log | ✅ | ✅ | ✅ |

---

## Security Notes

⚠️ **IMPORTANT**: These are default credentials for development/testing purposes.

**For Production:**
1. Change all default passwords immediately
2. Use strong passwords (min 12 characters, mixed case, numbers, symbols)
3. Enable HTTPS/TLS for encrypted communication
4. Implement password rotation policy
5. Consider adding 2FA/MFA
6. Regularly audit user access

---

## Password Requirements (Recommended for Production)

- Minimum length: 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- No common dictionary words
- Different from previous 5 passwords

---

**Last Updated**: 2025-10-22  
**Environment**: Development
