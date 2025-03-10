import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { LayoutComponent } from './components/layout/layout.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { 
        path: 'dashboard', 
        loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      { 
        path: 'books', 
        loadComponent: () => import('./pages/books/books.component').then(m => m.BooksComponent)
      },
      { 
        path: 'books/:id', 
        loadComponent: () => import('./pages/book-detail/book-detail.component').then(m => m.BookDetailComponent)
      },
      { 
        path: 'my-books', 
        loadComponent: () => import('./pages/my-books/my-books.component').then(m => m.MyBooksComponent),
        canActivate: [authGuard]
      },
      { 
        path: 'book/new', 
        loadComponent: () => import('./pages/book-editor/book-editor.component').then(m => m.BookEditorComponent),
        canActivate: [authGuard]
      },
      { 
        path: 'book/edit/:id', 
        loadComponent: () => import('./pages/book-editor/book-editor.component').then(m => m.BookEditorComponent),
        canActivate: [authGuard]
      }
    ]
  },
  { path: '**', redirectTo: '/login' }
];
