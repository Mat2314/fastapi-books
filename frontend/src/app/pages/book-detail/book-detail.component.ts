import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { finalize } from 'rxjs/operators';
import { BookService, Book } from '../../services/book.service';

@Component({
  selector: 'app-book-detail',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatDividerModule
  ],
  templateUrl: './book-detail.component.html',
  styleUrl: './book-detail.component.scss'
})
export class BookDetailComponent implements OnInit {
  book: Book | null = null;
  loading = true;
  error = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private bookService: BookService
  ) {}

  ngOnInit(): void {
    this.loadBook();
  }

  loadBook(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.navigateToBooks();
      return;
    }

    this.loading = true;
    this.error = false;
    
    this.bookService.getBook(id)
      .pipe(
        finalize(() => this.loading = false)
      )
      .subscribe({
        next: (book) => {
          this.book = book;
        },
        error: () => {
          this.error = true;
        }
      });
  }

  navigateToBooks(): void {
    this.router.navigate(['/books']);
  }
}
