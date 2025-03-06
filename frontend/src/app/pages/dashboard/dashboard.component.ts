import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { UserService } from '../../services/user.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  isAuthor$: Observable<boolean>;
  
  constructor(private userService: UserService, private router: Router) {
    this.isAuthor$ = this.userService.isAuthor();
  }
  
  ngOnInit(): void {
    // Load user data when component initializes
    this.userService.loadCurrentUser();
  }
  
  navigateToBooks(): void {
    this.router.navigate(['/books']);
  }
  
  navigateToMyBooks(): void {
    this.router.navigate(['/my-books']);
  }
}
