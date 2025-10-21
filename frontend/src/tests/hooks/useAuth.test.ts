import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAuth } from '@/hooks/useAuth';

describe('useAuth Hook', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('should initialize with unauthenticated state', () => {
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
  });

  it('should set authenticated state on login', () => {
    const { result } = renderHook(() => useAuth());
    
    const mockUser = { 
      id: 1, 
      username: 'testuser', 
      role: 'operator' as const,
      created_at: Date.now(),
      is_active: true
    };
    const mockToken = 'test-token-123';

    act(() => {
      result.current.setAuth(mockUser, mockToken);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe(mockToken);
  });

  it('should clear state on logout', () => {
    const { result } = renderHook(() => useAuth());
    
    const mockUser = { 
      id: 1, 
      username: 'testuser', 
      role: 'operator' as const,
      created_at: Date.now(),
      is_active: true
    };

    act(() => {
      result.current.setAuth(mockUser, 'test-token');
    });

    expect(result.current.isAuthenticated).toBe(true);

    act(() => {
      result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
  });

  it('should restore auth from localStorage', () => {
    const mockUser = { 
      id: 1, 
      username: 'testuser', 
      role: 'operator' as const,
      created_at: Date.now(),
      is_active: true
    };
    const mockToken = 'stored-token';

    localStorage.setItem('user', JSON.stringify(mockUser));
    localStorage.setItem('token', mockToken);

    const { result } = renderHook(() => useAuth());
    
    act(() => {
      result.current.initializeAuth();
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe(mockToken);
  });
});
