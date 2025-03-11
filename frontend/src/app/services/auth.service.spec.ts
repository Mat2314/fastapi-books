import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let routerSpy: jasmine.SpyObj<Router>;
  let localStorageSpy: any;

  const mockToken = 'mock-jwt-token';
  const mockLoginResponse = {
    access_token: mockToken,
    refresh_token: 'mock-refresh-token',
    token_type: 'bearer'
  };
  const mockUser = {
    email: 'test@example.com',
    first_name: 'John',
    last_name: 'Doe',
    account_type: 'reader'
  };

  beforeEach(() => {
    // Create a spy for the Router
    const routerSpyObj = jasmine.createSpyObj('Router', ['navigate']);
    
    // Create spies for localStorage methods
    localStorageSpy = {};
    spyOn(localStorage, 'getItem').and.callFake((key: string) => {
      return localStorageSpy[key] || null;
    });
    spyOn(localStorage, 'setItem').and.callFake((key: string, value: string) => {
      localStorageSpy[key] = value;
    });
    spyOn(localStorage, 'removeItem').and.callFake((key: string) => {
      delete localStorageSpy[key];
    });

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, RouterTestingModule],
      providers: [
        AuthService,
        { provide: Router, useValue: routerSpyObj }
      ]
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    
    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    // Verify that there are no outstanding requests
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    it('should send correct login request and store token', () => {
      const email = 'test@example.com';
      const password = 'password123';

      service.login(email, password).subscribe(response => {
        expect(response).toEqual(mockLoginResponse);
        expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', mockToken);
      });

      const req = httpMock.expectOne(request => 
        request.url === '/api/v1/auth/login' && 
        request.method === 'POST'
      );
      
      // Check that FormData was used correctly
      const formData = req.request.body as FormData;
      expect(formData.get('username')).toBe(email);
      expect(formData.get('password')).toBe(password);
      
      req.flush(mockLoginResponse);
    });

    it('should update authentication status after successful login', () => {
      // Spy on the BehaviorSubject's next method
      spyOn(service['isAuthenticatedSubject'], 'next');

      service.login('test@example.com', 'password123').subscribe();

      const req = httpMock.expectOne(request => 
        request.url === '/api/v1/auth/login' && 
        request.method === 'POST'
      );
      req.flush(mockLoginResponse);

      expect(service['isAuthenticatedSubject'].next).toHaveBeenCalledWith(true);
    });

    it('should store tokens in localStorage after successful login', () => {
      const mockResponse = {
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
        token_type: 'bearer'
      };

      service.login('test@example.com', 'password').subscribe();

      const req = httpMock.expectOne('/api/v1/auth/login');
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);

      expect(localStorage.getItem('auth_token')).toBe('test-access-token');
      expect(localStorage.getItem('refresh_token')).toBe('test-refresh-token');
    });
  });

  describe('register', () => {
    it('should send correct registration request', () => {
      const userData = {
        first_name: 'John',
        last_name: 'Doe',
        email: 'test@example.com',
        password: 'password123',
        account_type: 'reader'
      };

      service.register(
        userData.first_name,
        userData.last_name,
        userData.email,
        userData.password,
        userData.account_type
      ).subscribe(response => {
        expect(response).toEqual(mockUser);
      });

      const req = httpMock.expectOne(request => 
        request.url === '/api/v1/auth/register' && 
        request.method === 'POST'
      );
      expect(req.request.body).toEqual(userData);
      
      req.flush(mockUser);
    });
  });

  describe('logout', () => {
    it('should remove token and update authentication status', () => {
      // Set a token first
      localStorageSpy['auth_token'] = mockToken;
      
      // Spy on the BehaviorSubject's next method
      spyOn(service['isAuthenticatedSubject'], 'next');
      
      service.logout();
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token');
      expect(service['isAuthenticatedSubject'].next).toHaveBeenCalledWith(false);
      expect(routerSpy.navigate).toHaveBeenCalledWith(['/login']);
    });

    it('should remove tokens from localStorage', () => {
      // Set up initial tokens
      localStorage.setItem('auth_token', 'test-access-token');
      localStorage.setItem('refresh_token', 'test-refresh-token');
      
      service.logout();
      
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });
  });

  describe('getToken', () => {
    it('should return token from localStorage', () => {
      // No token initially
      expect(service.getToken()).toBeNull();
      
      // Set a token
      localStorageSpy['auth_token'] = mockToken;
      
      expect(service.getToken()).toBe(mockToken);
    });
  });

  describe('hasToken', () => {
    it('should return true when token exists', () => {
      // No token initially
      expect(service['hasToken']()).toBeFalsy();
      
      // Set a token
      localStorageSpy['auth_token'] = mockToken;
      
      expect(service['hasToken']()).toBeTruthy();
    });
  });

  describe('isAuthenticated$', () => {
    it('should emit current authentication status', (done) => {
      // Initially not authenticated
      service.isAuthenticated$.subscribe(isAuthenticated => {
        expect(isAuthenticated).toBeFalsy();
        done();
      });
    });

    it('should emit updated authentication status after login', () => {
      service.login('test@example.com', 'password123').subscribe();

      const req = httpMock.expectOne(request => 
        request.url === '/api/v1/auth/login' && 
        request.method === 'POST'
      );
      req.flush(mockLoginResponse);

      service.isAuthenticated$.subscribe(isAuthenticated => {
        expect(isAuthenticated).toBeTruthy();
      });
    });

    it('should emit updated authentication status after logout', () => {
      // Set a token first to simulate being logged in
      localStorageSpy['auth_token'] = mockToken;
      
      // Force the BehaviorSubject to emit true
      service['isAuthenticatedSubject'].next(true);
      
      service.logout();
      
      service.isAuthenticated$.subscribe(isAuthenticated => {
        expect(isAuthenticated).toBeFalsy();
      });
    });
  });

  describe('refreshToken', () => {
    it('should update the access token after successful refresh', () => {
      // Set up initial tokens
      localStorage.setItem('auth_token', 'old-access-token');
      localStorage.setItem('refresh_token', 'test-refresh-token');
      
      const mockResponse = {
        access_token: 'new-access-token',
        token_type: 'bearer'
      };

      service.refreshToken().subscribe();

      const req = httpMock.expectOne('/api/v1/auth/refresh');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({ refresh_token: 'test-refresh-token' });
      req.flush(mockResponse);

      expect(localStorage.getItem('auth_token')).toBe('new-access-token');
      expect(localStorage.getItem('refresh_token')).toBe('test-refresh-token'); // Refresh token should remain the same
    });

    it('should return an error when no refresh token is available', (done) => {
      // Ensure no refresh token is set
      localStorage.removeItem('refresh_token');
      
      service.refreshToken().subscribe({
        error: (error) => {
          expect(error.message).toBe('No refresh token available');
          done();
        }
      });
    });
  });

  describe('token management', () => {
    it('should correctly check for token existence', () => {
      expect(service['hasToken']()).toBeFalse();
      expect(service.hasRefreshToken()).toBeFalse();
      
      localStorage.setItem('auth_token', 'test-access-token');
      expect(service['hasToken']()).toBeTrue();
      expect(service.hasRefreshToken()).toBeFalse();
      
      localStorage.setItem('refresh_token', 'test-refresh-token');
      expect(service['hasToken']()).toBeTrue();
      expect(service.hasRefreshToken()).toBeTrue();
    });
    
    it('should track token refreshing status', () => {
      expect(service.isRefreshingToken()).toBeFalse();
      
      service.setRefreshingToken(true);
      expect(service.isRefreshingToken()).toBeTrue();
      
      service.setRefreshingToken(false);
      expect(service.isRefreshingToken()).toBeFalse();
    });
  });
});
