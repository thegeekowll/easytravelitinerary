
const axios = require('axios');

const API_URL = 'http://localhost:8001/api/v1';

async function verify() {
  console.log('Testing connectivity to:', API_URL);

  // 1. Check Root Health (outside prefix)
  try {
    const res = await axios.get('http://localhost:8001/health');
    console.log('✅ /health Check Passed:', res.data);
  } catch (error) {
    console.error('❌ /health Check Failed:', error.message);
  }

  // 2. Check Tour Types (inside API prefix)
  try {
    const res = await axios.get(`${API_URL}/tour-types`);
    console.log(`✅ ${API_URL}/tour-types Check Passed. Count:`, Array.isArray(res.data) ? res.data.length : res.data.items?.length);
  } catch (error) {
    console.error(`❌ ${API_URL}/tour-types Check Failed:`, error.message);
    if (error.response) {
      console.error('   Status:', error.response.status);
      console.error('   Data:', error.response.data);
    }
  }
}

verify();
