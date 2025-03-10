import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LoginComponent } from './login.component';
import { ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';
import { NO_ERRORS_SCHEMA } from '@angular/core';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let snackBar: jasmine.SpyObj<MatSnackBar>;

  beforeEach(async () => {
    // Create spies for the dependencies
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['login', 'register']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    authServiceSpy.login.and.returnValue(of({
      access_token: 'test_token',
      refresh_token: 'test_refresh_token',
      token_type: 'bearer'
    }));
    
    // Add isAuthenticated$ property
    authServiceSpy.isAuthenticated$ = of(false);

    await TestBed.configureTestingModule({
      imports: [
        LoginComponent,
        ReactiveFormsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatTabsModule,
        MatIconModule,
        MatSelectModule,
        BrowserAnimationsModule // Important for Material animations
      ],
      providers: [
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy },
        { provide: MatSnackBar, useValue: snackBarSpy }
      ],
      schemas: [NO_ERRORS_SCHEMA] // Ignore unknown elements
    }).compileComponents();
    
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // Form Validation Tests
  describe('Form Validation', () => {
    it('should initialize login form with empty fields', () => {
      expect(component.loginForm.get('email')?.value).toBe('');
      expect(component.loginForm.get('password')?.value).toBe('');
      expect(component.loginForm.valid).toBeFalsy();
    });

    it('should initialize register form with empty fields except account_type', () => {
      expect(component.registerForm.get('first_name')?.value).toBe('');
      expect(component.registerForm.get('last_name')?.value).toBe('');
      expect(component.registerForm.get('email')?.value).toBe('');
      expect(component.registerForm.get('password')?.value).toBe('');
      expect(component.registerForm.get('account_type')?.value).toBe('reader');
      expect(component.registerForm.valid).toBeFalsy();
    });

    it('should validate email format in login form', () => {
      const emailControl = component.loginForm.get('email');
      
      emailControl?.setValue('invalid-email');
      expect(emailControl?.valid).toBeFalsy();
      expect(emailControl?.hasError('email')).toBeTruthy();
      
      emailControl?.setValue('valid@example.com');
      expect(emailControl?.valid).toBeTruthy();
      expect(emailControl?.hasError('email')).toBeFalsy();
    });

    it('should validate password length in register form', () => {
      const passwordControl = component.registerForm.get('password');
      
      passwordControl?.setValue('short');
      expect(passwordControl?.valid).toBeFalsy();
      expect(passwordControl?.hasError('minlength')).toBeTruthy();
      
      passwordControl?.setValue('password123');
      expect(passwordControl?.valid).toBeTruthy();
      expect(passwordControl?.hasError('minlength')).toBeFalsy();
    });

    it('should mark login form as valid when all fields are filled correctly', () => {
      component.loginForm.setValue({
        email: 'test@example.com',
        password: 'password123'
      });
      
      expect(component.loginForm.valid).toBeTruthy();
    });

    it('should mark register form as valid when all fields are filled correctly', () => {
      component.registerForm.setValue({
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        password: 'password123',
        account_type: 'reader'
      });
      
      expect(component.registerForm.valid).toBeTruthy();
    });
  });

  // Login Functionality Tests
  describe('Login Functionality', () => {
    it('should not call login service if form is invalid', () => {
      // Form is initially invalid
      component.onLogin();
      expect(authService.login).not.toHaveBeenCalled();
    });

    it('should call login service with correct credentials when form is valid', () => {
      const testEmail = 'test@example.com';
      const testPassword = 'password123';
      
      authService.login.and.returnValue(of({ access_token: 'fake-token', refresh_token: 'fake-refresh-token', token_type: 'bearer' }));
      
      component.loginForm.setValue({
        email: testEmail,
        password: testPassword
      });
      
      component.onLogin();
      
      expect(authService.login).toHaveBeenCalledWith(testEmail, testPassword);
    });
  });

  // Registration Functionality Tests
  describe('Registration Functionality', () => {
    it('should not call register service if form is invalid', () => {
      // Form is initially invalid
      component.onRegister();
      expect(authService.register).not.toHaveBeenCalled();
    });

    it('should call register service with correct data when form is valid', () => {
      const userData = {
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        password: 'password123',
        account_type: 'reader'
      };
      
      authService.register.and.returnValue(of(userData));
      
      component.registerForm.setValue(userData);
      
      component.onRegister();
      
      expect(authService.register).toHaveBeenCalledWith(
        userData.first_name,
        userData.last_name,
        userData.email,
        userData.password,
        userData.account_type
      );
    });
  });

  // UI Interaction Tests
  describe('UI Interactions', () => {
    it('should toggle password visibility', () => {
      expect(component.hideLoginPassword).toBeTruthy();
      component.hideLoginPassword = !component.hideLoginPassword;
      expect(component.hideLoginPassword).toBeFalsy();
    });
  });
});
