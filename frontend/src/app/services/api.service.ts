import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { EnvService } from './env.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl: string;

  constructor(
    private http: HttpClient,
    private envService: EnvService
  ) {
    // Get the API URL from the environment variables
    this.apiUrl = this.envService.apiUrl;
  }

  // Example method to get books
  getBooks(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/books`);
  }

  // Example method to get a book by ID
  getBook(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/books/${id}`);
  }

  // Add more API methods as needed
} 