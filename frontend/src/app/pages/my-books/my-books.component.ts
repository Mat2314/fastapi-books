import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { BookService, Book } from '../../services/book.service';
import { finalize } from 'rxjs/operators';
import { BookDialogComponent, BookDialogData } from '../../components/book-dialog/book-dialog.component';
import { RouterLink, Router } from '@angular/router';

interface MyBook extends Book {
  published: boolean;
}

@Component({
  selector: 'app-my-books',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    MatTooltipModule,
    MatSnackBarModule,
    MatDialogModule,
    RouterLink
  ],
  templateUrl: './my-books.component.html',
  styleUrl: './my-books.component.scss'
})
export class MyBooksComponent implements OnInit {
  myBooks: MyBook[] = [];
  loading = true;
  
  constructor(
    private bookService: BookService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}
  
  ngOnInit(): void {
    this.loadMyBooks();
  }
  
  loadMyBooks(): void {
    this.loading = true;
    this.bookService.getUserBooks()
      .pipe(
        finalize(() => this.loading = false)
      )
      .subscribe(books => {
        // Transform Book[] to MyBook[] with a published property
        // In a real app, this would come from the API
        this.myBooks = books.map(book => ({
          ...book,
          published: true // Default to published for now
        }));
      });
  }
  
  createNewBook(): void {
    this.router.navigate(['/book/new']);
  }
  
  editBook(bookId: string): void {
    this.router.navigate(['/book/edit', bookId]);
  }
  
  deleteBook(bookId: string): void {
    if (confirm('Are you sure you want to delete this book?')) {
      this.bookService.deleteBook(bookId).subscribe({
        next: () => {
          this.myBooks = this.myBooks.filter(book => book.id !== bookId);
          this.snackBar.open('Book deleted successfully', 'Close', {
            duration: 3000
          });
        },
        error: (error) => {
          console.error('Error deleting book:', error);
          this.snackBar.open('Failed to delete book', 'Close', {
            duration: 3000
          });
        }
      });
    }
  }
  
  togglePublishStatus(bookId: string, currentStatus: boolean): void {
    const book = this.myBooks.find(b => b.id === bookId);
    if (book) {
      // In a real app, this would call an API endpoint
      book.published = !currentStatus;
      this.snackBar.open(
        `Book ${book.published ? 'published' : 'unpublished'} successfully`, 
        'Close', 
        { duration: 3000 }
      );
    }
  }
} 