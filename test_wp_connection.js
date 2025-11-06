#!/usr/bin/env node

const https = require('https');
const http = require('http');

// WordPress site configuration
const config = {
  url: 'http://localhost:8080',
  username: 'lisboetas',
  password: 'EUsourico82!'
};

function testWordPressConnection() {
  console.log('🔍 Testing WordPress REST API connection...\n');
  
  // Test basic connectivity first
  const apiUrl = `${config.url}/wp-json/wp/v2/posts?per_page=1`;
  const auth = Buffer.from(`${config.username}:${config.password}`).toString('base64');
  
  const options = {
    method: 'GET',
    headers: {
      'Authorization': `Basic ${auth}`,
      'Content-Type': 'application/json'
    }
  };

  const client = config.url.startsWith('https') ? https : http;
  
  const req = client.request(apiUrl, options, (res) => {
    console.log(`📡 Status Code: ${res.statusCode}`);
    console.log(`📋 Headers:`, res.headers);
    
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      try {
        if (res.statusCode === 200) {
          const posts = JSON.parse(data);
          console.log(`✅ Connection successful! Found ${posts.length} posts`);
          console.log(`🎯 WordPress REST API is working correctly`);
          
          // Test if Application Passwords are supported
          testApplicationPasswords();
        } else {
          console.log(`❌ Connection failed with status ${res.statusCode}`);
          console.log(`📄 Response:`, data);
        }
      } catch (error) {
        console.log(`❌ Error parsing response:`, error.message);
        console.log(`📄 Raw response:`, data);
      }
    });
  });
  
  req.on('error', (error) => {
    console.log(`❌ Request failed:`, error.message);
    console.log(`💡 Make sure WordPress is running on ${config.url}`);
  });
  
  req.end();
}

function testApplicationPasswords() {
  console.log('\n🔐 Testing Application Passwords support...');
  
  const apiUrl = `${config.url}/wp-json/wp/v2/users/me`;
  const auth = Buffer.from(`${config.username}:${config.password}`).toString('base64');
  
  const options = {
    method: 'GET',
    headers: {
      'Authorization': `Basic ${auth}`,
      'Content-Type': 'application/json'
    }
  };

  const client = config.url.startsWith('https') ? https : http;
  
  const req = client.request(apiUrl, options, (res) => {
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      if (res.statusCode === 200) {
        try {
          const user = JSON.parse(data);
          console.log(`✅ User authentication successful for: ${user.name}`);
          console.log(`👤 User ID: ${user.id}, Role: ${user.roles.join(', ')}`);
          console.log(`🎯 Ready for Claudeus WordPress MCP!`);
        } catch (error) {
          console.log(`❌ Error parsing user data:`, error.message);
        }
      } else {
        console.log(`❌ User authentication failed with status ${res.statusCode}`);
        console.log(`📄 Response:`, data);
      }
    });
  });
  
  req.on('error', (error) => {
    console.log(`❌ User request failed:`, error.message);
  });
  
  req.end();
}

// Run the test
testWordPressConnection();