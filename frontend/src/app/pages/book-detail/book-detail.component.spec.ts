import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { of, throwError } from 'rxjs';
import { NO_ERRORS_SCHEMA } from '@angular/core';

import { BookDetailComponent } from './book-detail.component';
import { BookService } from '../../services/book.service';

describe('BookDetailComponent', () => {
  let component: BookDetailComponent;
  let fixture: ComponentFixture<BookDetailComponent>;
  let bookServiceSpy: jasmine.SpyObj<BookService>;
  let routerSpy: jasmine.SpyObj<Router>;
  
  const mockBook = {
    id: '1',
    title: 'Test Book',
    content: 'Test Content',
    author_id: '1',
    author_name: 'Test Author',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  beforeEach(async () => {
    bookServiceSpy = jasmine.createSpyObj('BookService', ['getBook']);
    routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    
    await TestBed.configureTestingModule({
      imports: [
        BookDetailComponent,
        HttpClientTestingModule
      ],
      providers: [
        { provide: BookService, useValue: bookServiceSpy },
        { provide: Router, useValue: routerSpy },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: convertToParamMap({ id: '1' })
            }
          }
        }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();

    fixture = TestBed.createComponent(BookDetailComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    bookServiceSpy.getBook.and.returnValue(of(mockBook));
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should load book on init', () => {
    bookServiceSpy.getBook.and.returnValue(of(mockBook));
    fixture.detectChanges();
    
    expect(bookServiceSpy.getBook).toHaveBeenCalledWith('1');
    expect(component.book).toEqual(mockBook);
    expect(component.loading).toBeFalse();
    expect(component.error).toBeFalse();
  });

  it('should handle error when book not found', () => {
    bookServiceSpy.getBook.and.returnValue(throwError(() => new Error('Book not found')));
    fixture.detectChanges();
    
    expect(bookServiceSpy.getBook).toHaveBeenCalledWith('1');
    expect(component.book).toBeNull();
    expect(component.loading).toBeFalse();
    expect(component.error).toBeTrue();
  });

  it('should navigate back to books', () => {
    bookServiceSpy.getBook.and.returnValue(of(mockBook));
    fixture.detectChanges();
    
    component.navigateToBooks();
    expect(routerSpy.navigate).toHaveBeenCalledWith(['/books']);
  });
});
