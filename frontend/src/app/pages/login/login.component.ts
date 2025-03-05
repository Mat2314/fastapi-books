import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatTabsModule,
    MatIconModule,
    MatSnackBarModule,
    MatSelectModule
  ],
  templateUrl: './login.component.html',
  // styleUrl: './login.component.scss'
  styleUrl: './login-animation.scss'  // Alternative: Professional Color Animation

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
      password: ['', [Validators.required]]
    });

    this.registerForm = this.fb.group({
      first_name: ['', [Validators.required]],
      last_name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      account_type: ['reader', [Validators.required]]
    });
  }
  
  ngOnInit(): void {
    // You could load a random background image here if desired
    // this.loadRandomBackground();
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
            duration: 5000
          });
          // Switch to login tab and prefill email
          this.loginForm.patchValue({ email });
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

  // Optional method to load a random background
  // private loadRandomBackground(): void {
  //   const backgrounds = [
  //     '/assets/images/background1.jpg',
  //     '/assets/images/background2.jpg',
  //     '/assets/images/background3.jpg'
  //   ];
  //   this.backgroundImageUrl = backgrounds[Math.floor(Math.random() * backgrounds.length)];
  // }
}
