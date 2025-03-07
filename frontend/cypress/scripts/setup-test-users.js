const axios = require('axios');
const users = require('../fixtures/users.json');

// API base URL - should match your backend
const API_URL = 'http://localhost:8000/api/v1';

async function setupTestUsers() {
  console.log('Setting up test users for Cypress tests...');
  
  try {
    // Try to create the author user
    await createUser(users.author);
    console.log(`✅ Author user (${users.author.email}) created or already exists`);
    
    // Try to create the reader user
    await createUser(users.reader);
    console.log(`✅ Reader user (${users.reader.email}) created or already exists`);
    
    console.log('Test users setup complete!');
  } catch (error) {
    console.error('❌ Error setting up test users:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    process.exit(1);
  }
}

async function createUser(userData) {
  try {
    // Try to register the user with query parameters
    const response = await axios.post(`${API_URL}/auth/register`, null, {
      params: {
        email: userData.email,
        password: userData.password,
        first_name: userData.first_name,
        last_name: userData.last_name,
        account_type: userData.account_type
      }
    });
    
    console.log(`User created: ${userData.email}`);
    return response.data;
  } catch (error) {
    // If error is 400, user might already exist, which is fine
    if (error.response && error.response.status === 400) {
      console.log(`User ${userData.email} already exists, skipping creation`);
    } else {
      // For other errors, propagate them
      throw error;
    }
  }
}

// Run the setup
setupTestUsers(); 