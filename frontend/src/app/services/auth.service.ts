import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
// import { UserService } from './user.service';

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface RefreshResponse {
  access_token: string;
  token_type: string;
}

interface User {
  email: string;
  first_name: string;
  last_name: string;
  account_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'auth_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  private apiUrl = environment.production ? environment.apiUrl : '';
  private refreshingToken = false;
  
  isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private http: HttpClient, 
    private router: Router,
    // private userService: UserService
  ) { }

  login(email: string, password: string): Observable<LoginResponse> {
    const formData = new FormData();
    // FastAPI's OAuth2PasswordRequestForm expects 'username' field even though we're using email
    formData.append('username', email);
    formData.append('password', password);

    return this.http.post<LoginResponse>(`${this.apiUrl}/api/v1/auth/login`, formData).pipe(
      tap(response => {
        this.setToken(response.access_token);
        this.setRefreshToken(response.refresh_token);
        this.isAuthenticatedSubject.next(true);
        // this.userService.loadCurrentUser();
      })
    );
  }

  refreshToken(): Observable<RefreshResponse> {
    const refreshToken = this.getRefreshToken();
    
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }
    
    return this.http.post<RefreshResponse>(`${this.apiUrl}/api/v1/auth/refresh`, { refresh_token: refreshToken }).pipe(
      tap(response => {
        this.setToken(response.access_token);
      })
    );
  }

  register(first_name: string, last_name: string, email: string, password: string, account_type: string): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/api/v1/auth/register`, {
      first_name,
      last_name,
      email,
      password,
      account_type
    });
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    this.isAuthenticatedSubject.next(false);
    // this.userService.clearCurrentUser();
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  private setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  private setRefreshToken(token: string): void {
    localStorage.setItem(this.REFRESH_TOKEN_KEY, token);
  }

  private hasToken(): boolean {
    return !!this.getToken();
  }

  hasRefreshToken(): boolean {
    return !!this.getRefreshToken();
  }

  isRefreshingToken(): boolean {
    return this.refreshingToken;
  }

  setRefreshingToken(refreshing: boolean): void {
    this.refreshingToken = refreshing;
  }
}
