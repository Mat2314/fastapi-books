import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, of, shareReplay, tap } from 'rxjs';

export interface AppConfig {
  apiUrl: string;
}

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private config: AppConfig | null = null;
  private configUrl = 'assets/config.json';
  private configLoaded$: Observable<AppConfig> | null = null;

  constructor(private http: HttpClient) {}

  /**
   * Load the configuration from the assets/config.json file
   * This gets called during app initialization
   */
  loadConfig(): Observable<AppConfig> {
    if (this.configLoaded$) {
      return this.configLoaded$;
    }

    this.configLoaded$ = this.http.get<AppConfig>(this.configUrl).pipe(
      tap(config => {
        console.log('Runtime config loaded:', config);
        this.config = config;
      }),
      catchError(error => {
        console.error('Could not load config file:', error);
        // Fallback to default config
        this.config = { apiUrl: 'http://localhost:8000' };
        return of(this.config);
      }),
      shareReplay(1)
    );

    return this.configLoaded$;
  }

  /**
   * Get the API URL from the loaded configuration
   */
  get apiUrl(): string {
    if (!this.config) {
      console.warn('Config not loaded yet, using default API URL');
      return 'http://localhost:8000';
    }
    return this.config.apiUrl;
  }
} 