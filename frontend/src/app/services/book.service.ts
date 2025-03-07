import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface Book {
  id: string;
  title: string;
  content: string;
  author_id: string;
  author_name?: string;
  created_at: string;
  updated_at: string;
  published?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class BookService {
  private apiUrl = environment.apiUrl;
  
  constructor(private http: HttpClient) { }
  
  getAllBooks(): Observable<Book[]> {
    return this.http.get<Book[]>(`${this.apiUrl}/api/v1/books`).pipe(
      catchError(error => {
        console.error('Error fetching books:', error);
        return of([]);
      })
    );
  }
  
  getBook(id: string): Observable<Book> {
    return this.http.get<Book>(`${this.apiUrl}/api/v1/books/${id}`);
  }
  
  getUserBooks(): Observable<Book[]> {
    return this.http.get<Book[]>(`${this.apiUrl}/api/v1/books/user`).pipe(
      catchError(error => {
        console.error('Error fetching user books:', error);
        return of([]);
      })
    );
  }
  
  createBook(bookData: Partial<Book>): Observable<Book> {
    return this.http.post<Book>(`${this.apiUrl}/api/v1/books`, bookData);
  }
  
  updateBook(id: string, bookData: Partial<Book>): Observable<Book> {
    return this.http.put<Book>(`${this.apiUrl}/api/v1/books/${id}`, bookData);
  }
  
  deleteBook(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/api/v1/books/${id}`);
  }
} 