import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BookService, Book } from '../../services/book.service';
import { finalize } from 'rxjs/operators';
import { TruncatePipe } from '../../pipes/truncate.pipe';

@Component({
  selector: 'app-books',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    TruncatePipe
  ],
  templateUrl: './books.component.html',
  styleUrl: './books.component.scss'
})
export class BooksComponent implements OnInit {
  books: Book[] = [];
  loading = true;
  
  constructor(private bookService: BookService) {}
  
  ngOnInit(): void {
    this.loadBooks();
  }
  
  loadBooks(): void {
    this.loading = true;
    this.bookService.getAllBooks()
      .pipe(
        finalize(() => this.loading = false)
      )
      .subscribe(books => {
        this.books = books;
      });
  }
} 