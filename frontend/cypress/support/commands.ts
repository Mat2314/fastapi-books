/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

// Declare global Cypress namespace to add custom commands
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      logout(): Chainable<void>;
    }
  }
}

// Login command
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/login');
  
  // Wait for the login form to be visible
  cy.get('form').should('be.visible');
  
  // Fill in the login form
  cy.get('input[formControlName="email"]').should('be.visible').type(email);
  cy.get('input[formControlName="password"]').should('be.visible').type(password);
  
  // Click the login button
  cy.get('button').contains('Login').should('be.visible').click();
  
  // Wait for navigation to complete - increase timeout to 10s
  cy.url().should('include', '/dashboard', { timeout: 10000 });
});

// Logout command
Cypress.Commands.add('logout', () => {
  // Click the logout button in the toolbar
  cy.get('button[aria-label="Logout"]').should('be.visible').click();
  
  // Wait for navigation to complete
  cy.url().should('include', '/login', { timeout: 10000 });
});

export {};