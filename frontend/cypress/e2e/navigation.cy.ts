describe('Navigation', () => {
  it('should redirect to login when accessing protected routes without authentication', () => {
    // Try to access dashboard without login
    cy.visit('/dashboard');
    cy.url().should('include', '/login');
    
    // Try to access books without login
    cy.visit('/books');
    cy.url().should('include', '/login');
    
    // Try to access my-books without login
    cy.visit('/my-books');
    cy.url().should('include', '/login');
  });
});