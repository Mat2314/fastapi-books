import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Observable, catchError, switchMap, throwError, BehaviorSubject, filter, take } from 'rxjs';
import { Router } from '@angular/router';

// Subject to track token refresh status
const refreshTokenInProgress = new BehaviorSubject<boolean>(false);

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  // Skip token refresh for auth endpoints to avoid infinite loops
  const isAuthRequest = req.url.includes('/api/v1/auth/');
  
  // Add token to requests if available
  const token = authService.getToken();
  if (token) {
    req = addTokenToRequest(req, token);
  }
  
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Handle 401 Unauthorized errors
      if (error.status === 401 && !isAuthRequest) {
        // If we're already refreshing the token, wait until it's done
        if (refreshTokenInProgress.value) {
          return waitForTokenRefresh(req, next);
        }
        
        // Start token refresh process
        return handleTokenRefresh(req, next, authService, router);
      }
      
      return throwError(() => error);
    })
  );
};

function addTokenToRequest(req: any, token: string): any {
  return req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`
    }
  });
}

function waitForTokenRefresh(req: any, next: any): Observable<any> {
  const authService = inject(AuthService);
  
  return refreshTokenInProgress.pipe(
    filter(inProgress => !inProgress),
    take(1),
    switchMap(() => {
      const newToken = authService.getToken();
      if (newToken) {
        return next(addTokenToRequest(req, newToken));
      }
      return throwError(() => new Error('No token available after refresh'));
    })
  );
}

function handleTokenRefresh(req: any, next: any, authService: AuthService, router: Router): Observable<any> {
  refreshTokenInProgress.next(true);
  
  return authService.refreshToken().pipe(
    switchMap(response => {
      refreshTokenInProgress.next(false);
      return next(addTokenToRequest(req, authService.getToken()!));
    }),
    catchError(error => {
      refreshTokenInProgress.next(false);
      
      // If refresh token fails, log the user out
      authService.logout();
      router.navigate(['/login']);
      
      return throwError(() => new Error('Session expired. Please log in again.'));
    })
  );
} 