import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { catchError, tap, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  account_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  
  currentUser$ = this.currentUserSubject.asObservable();
  
  constructor(private http: HttpClient) {
    this.loadCurrentUser();
  }
  
  loadCurrentUser(): void {
    this.http.get<User>(`${this.apiUrl}/api/v1/users/me`)
      .pipe(
        tap(user => this.currentUserSubject.next(user)),
        catchError(error => {
          console.error('Error loading user:', error);
          return of(null);
        })
      )
      .subscribe();
  }
  
  getCurrentUser(): Observable<User | null> {
    if (!this.currentUserSubject.value) {
      this.loadCurrentUser();
    }
    return this.currentUser$;
  }
  
  isAuthor(): Observable<boolean> {
    // Ensure we have the latest user data
    if (!this.currentUserSubject.value) {
      this.loadCurrentUser();
    }
    
    // Derive isAuthor directly from the currentUser$ observable
    return this.currentUser$.pipe(
      map(user => {
        const isAuthor = user?.account_type === 'author';
        return isAuthor;
      })
    );
  }
  
  clearCurrentUser(): void {
    this.currentUserSubject.next(null);
  }
} 