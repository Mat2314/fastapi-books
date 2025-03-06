import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { UserService } from '../services/user.service';
import { map, take } from 'rxjs/operators';

export const authorGuard: CanActivateFn = (route, state) => {
  const userService = inject(UserService);
  const router = inject(Router);
  
  return userService.isAuthor().pipe(
    take(1),
    map(isAuthor => {
      if (isAuthor) {
        return true;
      } else {
        router.navigate(['/dashboard']);
        return false;
      }
    })
  );
}; 