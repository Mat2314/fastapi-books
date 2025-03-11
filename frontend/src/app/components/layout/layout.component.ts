import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { AuthService } from '../../services/auth.service';
import { UserService } from '../../services/user.service';
import { Observable, of } from 'rxjs';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatDividerModule
  ],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss'
})
export class LayoutComponent implements OnInit {
  // Initialize with a default value of false
  isAuthor$: Observable<boolean> = of(false);
  
  constructor(
    private authService: AuthService,
    private userService: UserService
  ) {}
  
  ngOnInit(): void {
    // Load user data when component initializes
    this.userService.loadCurrentUser();
    
    // Initialize isAuthor$ after loading user data
    this.isAuthor$ = this.userService.isAuthor();
  }
  
  logout(): void {
    this.userService.clearCurrentUser();
    this.authService.logout();
  }
} 