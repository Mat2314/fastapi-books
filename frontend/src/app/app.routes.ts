import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { BooksComponent } from './pages/books/books.component';
import { MyBooksComponent } from './pages/my-books/my-books.component';
import { BookDetailComponent } from './pages/book-detail/book-detail.component';
import { BookEditorComponent } from './pages/book-editor/book-editor.component';
import { LayoutComponent } from './components/layout/layout.component';
import { authGuard } from './guards/auth.guard';
import { authorGuard } from './guards/author.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'books', component: BooksComponent },
      { path: 'books/:id', component: BookDetailComponent },
      { path: 'my-books', component: MyBooksComponent, canActivate: [authorGuard] },
      { path: 'book/new', component: BookEditorComponent, canActivate: [authorGuard] },
      { path: 'book/edit/:id', component: BookEditorComponent, canActivate: [authorGuard] }
    ]
  },
  { path: '**', redirectTo: '/login' }
];
