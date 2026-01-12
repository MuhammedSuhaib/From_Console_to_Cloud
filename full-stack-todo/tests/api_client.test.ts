/**
 * Frontend API Integration Tests
 * Testing the lib/api.ts client that handles JWT communication with backend
 */

// Mock localStorage for testing
const mockLocalStorage = (() => {
  let store: any = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: any) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});


// Mock fetch for API testing
let mockFetchResponse: any = {};
global.fetch = jest.fn(() => 
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve(mockFetchResponse),
    text: () => Promise.resolve(JSON.stringify(mockFetchResponse))
  } as Response)
) as jest.Mock;

// Import the API client
import { api } from '../lib/api';

describe('API Client Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
  });

  test('should include JWT token in requests when available', async () => {
    // Set a mock JWT token in localStorage
    mockLocalStorage.setItem('auth_token', 'mock.jwt.token');

    // Mock the fetch response
    mockFetchResponse = { data: [{ id: 1, title: 'Test Task' }] };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockFetchResponse),
    });

    // Call the API
    const tasks = await api.getTasks();

    // Verify that fetch was called with the proper authorization header
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/tasks$/),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer mock.jwt.token'
        })
      })
    );

    expect(tasks).toEqual(mockFetchResponse.data);
  });

  test('should work without JWT token when not available', async () => {
    // Ensure no token is in localStorage
    mockLocalStorage.removeItem('auth_token');

    // Mock the fetch response
    mockFetchResponse = { data: [] };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockFetchResponse),
    });

    // Call the API
    const tasks = await api.getTasks();

    // Verify that fetch was called without authorization header
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/tasks$/),
      expect.not.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.any(String)
        })
      })
    );

    expect(tasks).toEqual(mockFetchResponse.data);
  });

  test('should handle API errors correctly', async () => {
    // Set a mock JWT token in localStorage
    mockLocalStorage.setItem('auth_token', 'mock.jwt.token');

    // Mock an error response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      text: () => Promise.resolve('Unauthorized'),
    });

    // Call the API and expect an error
    await expect(api.getTasks()).rejects.toThrow('API error');

    // Verify that fetch was called with the proper authorization header
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/tasks$/),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer mock.jwt.token'
        })
      })
    );
  });

  test('should redirect on 401 errors', async () => {
    // Set a mock JWT token in localStorage
    mockLocalStorage.setItem('auth_token', 'mock.jwt.token');

    // Mock a 401 response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      text: () => Promise.resolve('Unauthorized'),
    });

    // Create a mock for window.location
    const mockLocation = { href: '' };
    Object.defineProperty(window, 'location', {
      value: mockLocation,
      writable: true,
    });

    // Call the API and expect an error that triggers redirect
    await expect(api.getTasks()).rejects.toThrow('API error');

    // Check that the token was removed from localStorage
    expect(mockLocalStorage.getItem('auth_token')).toBeNull();
  });
});