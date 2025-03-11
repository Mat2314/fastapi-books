import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { Book } from '../../services/book.service';

export interface BookDialogData {
  book?: Book;
  isEdit: boolean;
}

@Component({
  selector: 'app-book-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule
  ],
  templateUrl: './book-dialog.component.html',
  styleUrl: './book-dialog.component.scss'
})
export class BookDialogComponent implements OnInit {
  bookForm: FormGroup;
  dialogTitle: string;
  
  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<BookDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: BookDialogData
  ) {
    this.dialogTitle = data.isEdit ? 'Edit Book' : 'Create New Book';
    
    this.bookForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      content: ['', [Validators.required, Validators.minLength(10)]]
    });
  }
  
  ngOnInit(): void {
    if (this.data.isEdit && this.data.book) {
      this.bookForm.patchValue({
        title: this.data.book.title,
        content: this.data.book.content
      });
    }
  }
  
  onSubmit(): void {
    if (this.bookForm.valid) {
      this.dialogRef.close(this.bookForm.value);
    }
  }
  
  onCancel(): void {
    this.dialogRef.close();
  }
} 