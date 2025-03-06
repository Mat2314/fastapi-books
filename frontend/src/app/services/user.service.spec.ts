import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { UserService, User } from './user.service';
import { environment } from '../../environments/environment';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;

  const mockUser: User = {
    id: '1',
    email: 'test@example.com',
    first_name: 'Test',
    last_name: 'User',
    account_type: 'author'
  };

  const mockRegularUser: User = {
    id: '2',
    email: 'regular@example.com',
    first_name: 'Regular',
    last_name: 'User',
    account_type: 'user'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [UserService]
    });
    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
    
    // Handle the initial HTTP request made in the constructor
    const req = httpMock.expectOne(request => 
      request.url === `${environment.apiUrl}/api/v1/users/me` && 
      request.method === 'GET'
    );
    req.flush(mockUser);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('loadCurrentUser', () => {
    it('should load the current user and update the currentUserSubject', () => {
      service.loadCurrentUser();

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/api/v1/users/me` && 
        request.method === 'GET'
      );
      req.flush(mockUser);

      service.currentUser$.subscribe(user => {
        expect(user).toEqual(mockUser);
      });
    });

    it('should handle errors when loading the current user', () => {
      spyOn(console, 'error');
      
      // Clear the current user first
      service.clearCurrentUser();
      
      service.loadCurrentUser();

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/api/v1/users/me` && 
        request.method === 'GET'
      );
      req.error(new ErrorEvent('Network error'));

      service.currentUser$.subscribe(user => {
        expect(user).toBeNull();
      });
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('getCurrentUser', () => {
    it('should return the current user if it exists', () => {
      // The current user is already set in beforeEach
      
      // Test getCurrentUser
      service.getCurrentUser().subscribe(user => {
        expect(user).toEqual(mockUser);
      });
      
      // No additional HTTP request should be made
      httpMock.expectNone(`${environment.apiUrl}/api/v1/users/me`);
    });

    it('should load the current user if it does not exist', () => {
      // Clear the current user
      service.clearCurrentUser();

      // Call getCurrentUser
      service.getCurrentUser();

      // Verify that loadCurrentUser was called
      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/api/v1/users/me` && 
        request.method === 'GET'
      );
      req.flush(mockUser);

      service.currentUser$.subscribe(user => {
        expect(user).toEqual(mockUser);
      });
    });
  });

  describe('isAuthor', () => {
    it('should return true if the user is an author', () => {
      // The current user is already set as an author in beforeEach
      
      service.isAuthor().subscribe(isAuthor => {
        expect(isAuthor).toBeTrue();
      });
      
      // No additional HTTP request should be made
      httpMock.expectNone(`${environment.apiUrl}/api/v1/users/me`);
    });

    it('should return false if the user is not an author', () => {
      // Override the current user as a regular user
      service.clearCurrentUser();
      
      // Mock the loadCurrentUser call that will happen in getCurrentUser
      service.getCurrentUser();
      
      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/api/v1/users/me` && 
        request.method === 'GET'
      );
      req.flush(mockRegularUser); // mockRegularUser has account_type: 'user'

      service.isAuthor().subscribe(isAuthor => {
        expect(isAuthor).toBeFalse();
      });
    });

    it('should return false if there is no current user', () => {
      // Clear the current user
      service.clearCurrentUser();

      // Call isAuthor which will trigger getCurrentUser and loadCurrentUser
      let isAuthorResult: boolean | undefined;
      service.isAuthor().subscribe(result => {
        isAuthorResult = result;
      });
      
      // Handle the HTTP request triggered by getCurrentUser
      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/api/v1/users/me` && 
        request.method === 'GET'
      );
      req.error(new ErrorEvent('Network error'));
      
      expect(isAuthorResult).toBeFalse();
    });
  });

  describe('clearCurrentUser', () => {
    it('should clear the current user', () => {
      // The current user is already set in beforeEach
      
      // Clear the current user
      service.clearCurrentUser();

      service.currentUser$.subscribe(user => {
        expect(user).toBeNull();
      });
    });
  });
}); 