#!/usr/bin/env node

const https = require('https');
const http = require('http');

// WordPress site configuration
const config = {
  url: 'http://localhost:8080',
  username: 'lisboetas',
  password: 'EUsourico82!'
};

function createApplicationPassword() {
  console.log('🔐 Creating Application Password for Claudeus WordPress MCP...\n');
  
  // First, let's try to get user info to see if we can authenticate
  const loginUrl = `${config.url}/wp-login.php`;
  const apiUrl = `${config.url}/wp-json/wp/v2/users/me/application-passwords`;
  
  // Create application password
  const postData = JSON.stringify({
    name: 'Claudeus WordPress MCP'
  });
  
  const auth = Buffer.from(`${config.username}:${config.password}`).toString('base64');
  
  const options = {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${auth}`,
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(postData)
    }
  };

  const client = config.url.startsWith('https') ? https : http;
  
  const req = client.request(apiUrl, options, (res) => {
    console.log(`📡 Status Code: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      try {
        if (res.statusCode === 201) {
          const response = JSON.parse(data);
          console.log(`✅ Application Password created successfully!`);
          console.log(`🔑 Password: ${response.password}`);
          console.log(`📝 Name: ${response.name}`);
          console.log(`🆔 App ID: ${response.app_id}`);
          console.log(`\n🎯 Update your wp-sites.json with this password:`);
          console.log(`"PASS": "${response.password}"`);
          
          // Update wp-sites.json automatically
          updateWpSitesConfig(response.password);
          
        } else if (res.statusCode === 401) {
          console.log(`❌ Authentication failed. Trying alternative method...`);
          console.log(`📄 Response:`, data);
          
          // Try to get existing application passwords
          listApplicationPasswords();
          
        } else {
          console.log(`❌ Failed to create application password with status ${res.statusCode}`);
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
    console.log(`💡 Make sure WordPress is running and you have admin access`);
  });
  
  req.write(postData);
  req.end();
}

function listApplicationPasswords() {
  console.log('\n📋 Listing existing Application Passwords...');
  
  const apiUrl = `${config.url}/wp-json/wp/v2/users/me/application-passwords`;
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
          const passwords = JSON.parse(data);
          console.log(`✅ Found ${passwords.length} existing application passwords`);
          passwords.forEach((pwd, index) => {
            console.log(`${index + 1}. ${pwd.name} (${pwd.app_id}) - Created: ${pwd.created}`);
          });
          
          if (passwords.length === 0) {
            console.log(`💡 No application passwords found. You may need to create one manually in WordPress admin.`);
            console.log(`🔗 Go to: ${config.url}/wp-admin/profile.php`);
          }
        } catch (error) {
          console.log(`❌ Error parsing passwords list:`, error.message);
        }
      } else {
        console.log(`❌ Failed to list application passwords: ${res.statusCode}`);
        console.log(`📄 Response:`, data);
      }
    });
  });
  
  req.on('error', (error) => {
    console.log(`❌ Request failed:`, error.message);
  });
  
  req.end();
}

function updateWpSitesConfig(password) {
  const fs = require('fs');
  const path = '/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wp-sites.json';
  
  try {
    const config = {
      "chapeus_lisboetas": {
        "URL": "http://localhost:8080",
        "USER": "lisboetas",
        "PASS": password,
        "authType": "basic"
      }
    };
    
    fs.writeFileSync(path, JSON.stringify(config, null, 2));
    console.log(`✅ Updated wp-sites.json with new application password`);
  } catch (error) {
    console.log(`❌ Failed to update wp-sites.json:`, error.message);
  }
}

// Run the script
createApplicationPassword();