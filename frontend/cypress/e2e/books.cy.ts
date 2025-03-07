describe('Books', () => {
  beforeEach(() => {
    // Load test users from fixtures
    cy.fixture('users').as('users');
  });

  it('should redirect to login when accessing books page without authentication', () => {
    // Try to access books page without login
    cy.visit('/books');
    
    // Should be redirected to login page
    cy.url().should('include', '/login');
  });

  it('should display books after login', function() {
    const author = this['users'].author;
    
    // Login first
    cy.log(`Logging in with ${author.email}`);
    cy.visit('/login');
    cy.get('input[formControlName="email"]').should('be.visible').clear().type(author.email);
    cy.get('input[formControlName="password"]').should('be.visible').clear().type(author.password);
    
    // Intercept the login request
    cy.intercept('POST', '/api/v1/auth/login').as('loginRequest');
    cy.get('button').contains('Login').click();
    
    // Wait for login response and log it
    cy.wait('@loginRequest').then((interception) => {
      if (interception.response?.statusCode !== 200) {
        cy.log(`Login failed with status: ${interception.response?.statusCode}`);
        cy.log(`Response body: ${JSON.stringify(interception.response?.body)}`);
      } else {
        cy.log('Login successful!');
      }
    });
    
    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard', { timeout: 10000 });
    
    // Navigate to books page
    cy.contains('Browse Books').click();
    
    // Verify we're on the books page
    cy.url().should('include', '/books');
    
    // Check if books page elements are visible
    cy.get('.page-title').contains('Browse Books').should('be.visible');
    
    // If there are books, check for book cards, otherwise check for "No books found" message
    cy.get('body').then(($body) => {
      if ($body.find('.book-card').length > 0) {
        cy.get('.book-card').should('be.visible');
      } else {
        cy.get('.no-books').should('be.visible');
      }
    });
  });
});