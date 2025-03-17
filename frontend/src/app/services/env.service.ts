import { Injectable } from '@angular/core';

// Define the interface for the window.env object
interface Environment {
  API_URL: string;
  ENVIRONMENT: string;
  [key: string]: string;
}

// Extend the Window interface to include our env property
declare global {
  interface Window {
    env: Environment;
  }
}

@Injectable({
  providedIn: 'root'
})
export class EnvService {
  // Default values in case the env.js file isn't loaded
  private environment: Environment = {
    API_URL: 'http://localhost:8000',
    ENVIRONMENT: 'development'
  };

  constructor() {
    // Use the window.env values if they exist
    if (window.env) {
      this.environment = { ...this.environment, ...window.env };
    }
  }

  get(key: string): string {
    return this.environment[key];
  }

  get apiUrl(): string {
    return this.environment.API_URL;
  }

  get isProduction(): boolean {
    return this.environment.ENVIRONMENT === 'production';
  }
} 