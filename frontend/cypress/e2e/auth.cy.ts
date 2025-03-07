describe('Authentication', () => {
  beforeEach(() => {
    // Load test users from fixtures
    cy.fixture('users').as('users');
  });

  it('should load the login page', () => {
    cy.visit('/login');
    cy.get('mat-card-title').contains('Welcome to Fabulous Books').should('be.visible');
    cy.get('input[formControlName="email"]').should('be.visible');
    cy.get('input[formControlName="password"]').should('be.visible');
    cy.get('button').contains('Login').should('be.visible');
  });

  it('should login with valid credentials', function() {
    const author = this['users'].author;
    
    cy.log(`Attempting to login with ${author.email}`);
    cy.visit('/login');
    
    // Fill in the login form
    cy.get('input[formControlName="email"]').should('be.visible').clear().type(author.email);
    cy.get('input[formControlName="password"]').should('be.visible').clear().type(author.password);
    
    // Intercept the login request to check the response
    cy.intercept('POST', '/api/v1/auth/login').as('loginRequest');
    
    // Click the login button
    cy.get('button').contains('Login').should('be.visible').click();
    
    // Wait for the login request and check the response
    cy.wait('@loginRequest').then((interception) => {
      if (interception.response?.statusCode !== 200) {
        cy.log(`Login failed with status: ${interception.response?.statusCode}`);
        cy.log(`Response body: ${JSON.stringify(interception.response?.body)}`);
      } else {
        cy.log('Login successful!');
      }
    });
    
    // Check if we're redirected to the dashboard
    cy.url().should('include', '/dashboard', { timeout: 10000 });
    
    // Verify we're logged in by checking for dashboard elements
    cy.get('.page-title').contains('Welcome to Fabulous Books').should('be.visible');
  });
}); 