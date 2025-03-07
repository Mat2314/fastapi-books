import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatDividerModule } from '@angular/material/divider';
import { finalize } from 'rxjs/operators';
import { BookService, Book } from '../../services/book.service';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-book-editor',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatSlideToggleModule,
    MatDividerModule
  ],
  templateUrl: './book-editor.component.html',
  styleUrl: './book-editor.component.scss'
})
export class BookEditorComponent implements OnInit {
  bookForm: FormGroup;
  isEditMode = false;
  bookId: string | null = null;
  loading = false;
  saving = false;
  error = false;
  unauthorized = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private bookService: BookService,
    private userService: UserService,
    private snackBar: MatSnackBar
  ) {
    this.bookForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      content: ['', [Validators.required, Validators.minLength(10)]],
      published: [false]
    });
  }

  ngOnInit(): void {
    this.bookId = this.route.snapshot.paramMap.get('id');
    this.isEditMode = !!this.bookId;
    
    if (this.isEditMode && this.bookId) {
      this.loadBook(this.bookId);
    }
  }

  loadBook(id: string): void {
    this.loading = true;
    this.error = false;
    this.unauthorized = false;
    
    this.bookService.getBook(id)
      .pipe(
        finalize(() => this.loading = false)
      )
      .subscribe({
        next: (book) => {
          // Check if the current user is the author of the book
          this.userService.getCurrentUser().subscribe(user => {
            if (user && user.id === book.author_id) {
              this.bookForm.patchValue({
                title: book.title,
                content: book.content,
                published: book.published || false
              });
            } else {
              this.unauthorized = true;
            }
          });
        },
        error: () => {
          this.error = true;
        }
      });
  }

  onSubmit(): void {
    if (this.bookForm.invalid) {
      return;
    }

    this.saving = true;
    const bookData = this.bookForm.value;

    const saveOperation = this.isEditMode && this.bookId
      ? this.bookService.updateBook(this.bookId, bookData)
      : this.bookService.createBook(bookData);

    saveOperation
      .pipe(
        finalize(() => this.saving = false)
      )
      .subscribe({
        next: () => {
          const message = this.isEditMode ? 'Book updated successfully' : 'Book created successfully';
          this.snackBar.open(message, 'Close', { duration: 3000 });
          this.router.navigate(['/my-books']);
        },
        error: (error) => {
          console.error('Error saving book:', error);
          this.snackBar.open('Error saving book. Please try again.', 'Close', { duration: 3000 });
        }
      });
  }

  cancel(): void {
    this.router.navigate(['/my-books']);
  }
}
