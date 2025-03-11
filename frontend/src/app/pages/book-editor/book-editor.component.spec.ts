import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { of, throwError } from 'rxjs';

import { BookEditorComponent } from './book-editor.component';
import { BookService } from '../../services/book.service';
import { UserService } from '../../services/user.service';

describe('BookEditorComponent', () => {
  let component: BookEditorComponent;
  let fixture: ComponentFixture<BookEditorComponent>;
  let bookServiceSpy: jasmine.SpyObj<BookService>;
  let userServiceSpy: jasmine.SpyObj<UserService>;
  let routerSpy: jasmine.SpyObj<Router>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;
  
  const mockBook = {
    id: '1',
    title: 'Test Book',
    content: 'Test Content',
    author_id: 'user1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    published: true
  };
  
  const mockUser = {
    id: 'user1',
    email: 'test@example.com',
    first_name: 'Test',
    last_name: 'User',
    account_type: 'author'
  };

  beforeEach(async () => {
    bookServiceSpy = jasmine.createSpyObj('BookService', ['getBook', 'createBook', 'updateBook']);
    userServiceSpy = jasmine.createSpyObj('UserService', ['getCurrentUser']);
    routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    
    await TestBed.configureTestingModule({
      imports: [
        BookEditorComponent,
        ReactiveFormsModule,
        HttpClientTestingModule,
        BrowserAnimationsModule
      ],
      providers: [
        { provide: BookService, useValue: bookServiceSpy },
        { provide: UserService, useValue: userServiceSpy },
        { provide: Router, useValue: routerSpy },
        { provide: MatSnackBar, useValue: snackBarSpy },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: convertToParamMap({})
            }
          }
        }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();

    fixture = TestBed.createComponent(BookEditorComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    userServiceSpy.getCurrentUser.and.returnValue(of(mockUser));
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should initialize in create mode when no id is provided', () => {
    userServiceSpy.getCurrentUser.and.returnValue(of(mockUser));
    fixture.detectChanges();
    
    expect(component.isEditMode).toBeFalse();
    expect(component.bookId).toBeNull();
  });

  it('should load book data in edit mode', () => {
    // Setup route with book id
    const route = TestBed.inject(ActivatedRoute);
    Object.defineProperty(route, 'snapshot', {
      get: () => ({
        paramMap: convertToParamMap({ id: '1' })
      })
    });
    
    bookServiceSpy.getBook.and.returnValue(of(mockBook));
    userServiceSpy.getCurrentUser.and.returnValue(of(mockUser));
    
    fixture.detectChanges();
    
    expect(component.isEditMode).toBeTrue();
    expect(component.bookId).toBe('1');
    expect(bookServiceSpy.getBook).toHaveBeenCalledWith('1');
    
    // Form should be populated with book data
    expect(component.bookForm.get('title')?.value).toBe(mockBook.title);
    expect(component.bookForm.get('content')?.value).toBe(mockBook.content);
    expect(component.bookForm.get('published')?.value).toBe(mockBook.published);
  });

  it('should handle unauthorized access to edit book', () => {
    // Setup route with book id
    const route = TestBed.inject(ActivatedRoute);
    Object.defineProperty(route, 'snapshot', {
      get: () => ({
        paramMap: convertToParamMap({ id: '1' })
      })
    });
    
    const differentUser = { ...mockUser, id: 'user2' };
    
    bookServiceSpy.getBook.and.returnValue(of(mockBook));
    userServiceSpy.getCurrentUser.and.returnValue(of(differentUser));
    
    fixture.detectChanges();
    
    expect(component.unauthorized).toBeTrue();
  });

  it('should handle error when loading book', () => {
    // Setup route with book id
    const route = TestBed.inject(ActivatedRoute);
    Object.defineProperty(route, 'snapshot', {
      get: () => ({
        paramMap: convertToParamMap({ id: '1' })
      })
    });
    
    bookServiceSpy.getBook.and.returnValue(throwError(() => new Error('Book not found')));
    
    fixture.detectChanges();
    
    expect(component.error).toBeTrue();
  });

  it('should navigate back to my books on cancel', () => {
    userServiceSpy.getCurrentUser.and.returnValue(of(mockUser));
    fixture.detectChanges();
    
    component.cancel();
    
    expect(routerSpy.navigate).toHaveBeenCalledWith(['/my-books']);
  });
});
