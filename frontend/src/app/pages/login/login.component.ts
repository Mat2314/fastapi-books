import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MaterialModule } from '../../shared/material.module';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MaterialModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login-animation.scss'  // Using the optimized animation file
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  registerForm: FormGroup;
  hideLoginPassword = true;
  hideRegisterPassword = true;
  
  // Add a background image URL that can be dynamically changed
  backgroundImageUrl = '/assets/images/background.jpg';
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
    
    this.registerForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      account_type: ['reader', Validators.required]
    });
  }
  
  ngOnInit(): void {
    // Check if user is already logged in
    this.authService.isAuthenticated$.subscribe(isAuthenticated => {
      if (isAuthenticated) {
        this.router.navigate(['/dashboard']);
      }
    });
  }
  
  onLogin() {
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;
      this.authService.login(email, password).subscribe({
        next: () => {
          this.snackBar.open('Login successful!', 'Close', {
            duration: 3000
          });
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          console.error('Login error:', error);
          this.snackBar.open('Login failed: ' + (error.error?.detail || 'Unknown error'), 'Close', {
            duration: 5000
          });
        }
      });
    }
  }
  
  onRegister() {
    if (this.registerForm.valid) {
      const { first_name, last_name, email, password, account_type } = this.registerForm.value;
      this.authService.register(first_name, last_name, email, password, account_type).subscribe({
        next: () => {
          this.snackBar.open('Registration successful! Please login.', 'Close', {
            duration: 3000
          });
          this.loginForm.patchValue({ email });
          // Switch to login tab
          // Note: You would need to add logic to switch tabs here
        },
        error: (error) => {
          console.error('Registration error:', error);
          this.snackBar.open('Registration failed: ' + (error.error?.detail || 'Unknown error'), 'Close', {
            duration: 5000
          });
        }
      });
    }
  }
}
