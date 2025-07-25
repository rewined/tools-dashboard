"""
NetSuite REST API Client with corrected OAuth 1.0a implementation
Based on official NetSuite documentation and working examples
"""

import os
import requests
import json
import time
import hashlib
import hmac
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
import urllib.parse
import random
import math


class NetSuiteClient:
    """NetSuite REST API Client with OAuth 1.0a authentication"""
    
    def __init__(self, account_id: str = None, consumer_key: str = None, 
                 consumer_secret: str = None, token_id: str = None, 
                 token_secret: str = None):
        """Initialize NetSuite client with credentials"""
        self.account_id = account_id or os.environ.get('NETSUITE_ACCOUNT_ID')
        self.consumer_key = consumer_key or os.environ.get('NETSUITE_CONSUMER_KEY')
        self.consumer_secret = consumer_secret or os.environ.get('NETSUITE_CONSUMER_SECRET')
        self.token_id = token_id or os.environ.get('NETSUITE_TOKEN_ID')
        self.token_secret = token_secret or os.environ.get('NETSUITE_TOKEN_SECRET')
        
        # Determine NetSuite data center URL
        self.base_url = self._get_base_url()
        
        # Check if credentials are available
        self.is_configured = all([
            self.account_id, self.consumer_key, self.consumer_secret,
            self.token_id, self.token_secret
        ])
    
    def _get_base_url(self) -> str:
        """Determine NetSuite REST API base URL based on account ID"""
        if not self.account_id:
            return None
            
        # NetSuite URL format: https://{accountId}.suitetalk.api.netsuite.com
        # For sandbox: https://{accountId}-sb1.suitetalk.api.netsuite.com
        
        # Check if this is a sandbox account
        if '_SB' in self.account_id.upper() or os.environ.get('NETSUITE_SANDBOX', '').lower() == 'true':
            return f"https://{self.account_id.lower()}-sb1.suitetalk.api.netsuite.com"
        else:
            return f"https://{self.account_id.lower()}.suitetalk.api.netsuite.com"
    
    def _generate_nonce(self) -> str:
        """Generate 11-character alphanumeric nonce as per NetSuite requirements"""
        nonce_text = ""
        length = 11
        possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        for i in range(length):
            nonce_text += possible[math.floor(random.uniform(0, 1) * len(possible))]
        return nonce_text
    
    def _create_signature(self, method: str, url: str, oauth_params: Dict[str, str]) -> str:
        """Create OAuth 1.0a signature with HMAC-SHA256"""
        
        # Sort parameters alphabetically
        sorted_params = sorted(oauth_params.items())
        
        # Create parameter string with proper encoding
        param_string = '&'.join([
            f"{k}={urllib.parse.quote(str(v), safe='~')}" 
            for k, v in sorted_params
        ])
        
        # Create signature base string
        base_string = (
            method.upper() + '&' +
            urllib.parse.quote(url, safe='~') + '&' +
            urllib.parse.quote(param_string, safe='~')
        )
        
        # Create signing key
        signing_key = (
            urllib.parse.quote(self.consumer_secret, safe='~') + '&' +
            urllib.parse.quote(self.token_secret, safe='~')
        )
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            signing_key.encode('utf-8'),
            base_string.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        # Base64 encode
        return base64.b64encode(signature).decode('utf-8')
    
    def _generate_oauth_header(self, method: str, url: str) -> str:
        """Generate OAuth 1.0a authorization header"""
        
        # Generate OAuth parameters
        oauth_params = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_token': self.token_id,
            'oauth_signature_method': 'HMAC-SHA256',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': self._generate_nonce(),
            'oauth_version': '1.0'
        }
        
        # Generate signature
        oauth_params['oauth_signature'] = self._create_signature(method, url, oauth_params)
        
        # Build authorization header
        # NetSuite expects realm to be the account ID
        auth_header = f'OAuth realm="{self.account_id}", '
        auth_header += ', '.join([
            f'{k}="{urllib.parse.quote(str(v), safe="~")}"' 
            for k, v in sorted(oauth_params.items())
        ])
        
        return auth_header
    
    def _make_request(self, method: str, url: str, params: Dict = None, 
                     json_body: Any = None) -> Optional[requests.Response]:
        """Make authenticated request to NetSuite API"""
        
        headers = {
            'Authorization': self._generate_oauth_header(method, url),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add required headers for specific endpoints
        if 'suiteql' in url:
            headers['Prefer'] = 'transient'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=json_body, timeout=30)
            else:
                response = requests.request(method, url, headers=headers, 
                                          params=params, json=json_body, timeout=30)
            
            return response
            
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test NetSuite connection"""
        if not self.is_configured:
            return False
            
        # Try to access metadata catalog
        url = f"{self.base_url}/services/rest/record/v1/metadata-catalog/"
        response = self._make_request('GET', url)
        
        if response and response.status_code == 200:
            return True
        else:
            if response:
                print(f"Connection test failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
            return False
    
    def search_items_suiteql(self, query: str = None) -> List[Dict[str, Any]]:
        """Search for items using SuiteQL"""
        if not self.is_configured:
            return []
        
        url = f"{self.base_url}/services/rest/query/v1/suiteql"
        
        # Build SuiteQL query
        if query:
            suiteql = f"SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE LOWER('%{query}%') AND ROWNUM <= 100"
        else:
            suiteql = "SELECT id, itemid, displayname FROM item WHERE ROWNUM <= 100"
        
        body = {"q": suiteql}
        
        response = self._make_request('POST', url, json_body=body)
        
        if response and response.status_code == 200:
            data = response.json()
            items = []
            for row in data.get('items', []):
                items.append({
                    'id': row.get('id'),
                    'itemid': row.get('itemid'),
                    'displayname': row.get('displayname'),
                    'description': row.get('displayname', '')
                })
            return items
        else:
            return []
    
    def get_candle_products(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get products specifically for candle testing using SuiteQL"""
        if not self.is_configured:
            return self._get_fallback_products()
        
        try:
            products = {
                'vessels': [],
                'waxes': [],
                'fragrances': [],
                'wicks': []
            }
            
            # Use SuiteQL to search for different product types
            queries = {
                'vessels': [
                    "SELECT id, itemid, displayname FROM item WHERE (LOWER(itemid) LIKE '%ves%' OR LOWER(itemid) LIKE '%jar%' OR LOWER(displayname) LIKE '%vessel%') AND ROWNUM <= 50",
                ],
                'waxes': [
                    "SELECT id, itemid, displayname FROM item WHERE (LOWER(itemid) LIKE '%wax%' OR LOWER(displayname) LIKE '%wax%') AND ROWNUM <= 50",
                ],
                'fragrances': [
                    "SELECT id, itemid, displayname FROM item WHERE (LOWER(itemid) LIKE '%oil%' OR LOWER(itemid) LIKE '%fragrance%' OR LOWER(displayname) LIKE '%fragrance%') AND ROWNUM <= 50",
                ],
                'wicks': [
                    "SELECT id, itemid, displayname FROM item WHERE (LOWER(itemid) LIKE '%wick%' OR LOWER(displayname) LIKE '%wick%') AND ROWNUM <= 50",
                ]
            }
            
            url = f"{self.base_url}/services/rest/query/v1/suiteql"
            
            for category, category_queries in queries.items():
                for query in category_queries:
                    response = self._make_request('POST', url, json_body={"q": query})
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        for row in data.get('items', []):
                            item_id = str(row.get('id', ''))
                            item_name = f"{row.get('itemid', '')} - {row.get('displayname', '')}"
                            
                            # Avoid duplicates
                            if not any(p['id'] == item_id for p in products[category]):
                                products[category].append({
                                    'id': item_id,
                                    'name': item_name
                                })
            
            # If no items found, use fallback
            if not any(products.values()):
                return self._get_fallback_products()
                
            return products
            
        except Exception as e:
            print(f"Error getting candle products from NetSuite: {e}")
            return self._get_fallback_products()
    
    def _get_fallback_products(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return fallback products when NetSuite is not available"""
        return {
            'vessels': [
                {'id': 'ves-001', 'name': 'VES-001 - 8oz Clear Glass Jar'},
                {'id': 'ves-002', 'name': 'VES-002 - 10oz Frosted Glass'},
                {'id': 'ves-003', 'name': 'VES-003 - 12oz Black Ceramic'},
                {'id': 'ves-004', 'name': 'VES-004 - 6oz Tin Container'}
            ],
            'waxes': [
                {'id': 'wax-001', 'name': 'WAX-001 - Soy Wax 464'},
                {'id': 'wax-002', 'name': 'WAX-002 - Coconut Soy Blend'},
                {'id': 'wax-003', 'name': 'WAX-003 - Paraffin Blend'},
                {'id': 'wax-004', 'name': 'WAX-004 - Beeswax Blend'}
            ],
            'fragrances': [
                {'id': 'oil-001', 'name': 'OIL-001 - Lavender Fields'},
                {'id': 'oil-002', 'name': 'OIL-002 - Vanilla Bean'},
                {'id': 'oil-003', 'name': 'OIL-003 - Ocean Breeze'},
                {'id': 'oil-004', 'name': 'OIL-004 - Citrus Burst'}
            ],
            'wicks': [
                {'id': 'wick-001', 'name': 'Wick.CD4 - Cotton Core 4'},
                {'id': 'wick-002', 'name': 'Wick.CD6 - Cotton Core 6'},
                {'id': 'wick-003', 'name': 'Wick.CD8 - Cotton Core 8'},
                {'id': 'wick-004', 'name': 'Wick.ECO4 - Eco Series 4'},
                {'id': 'wick-005', 'name': 'Wick.ECO6 - Eco Series 6'},
                {'id': 'wick-006', 'name': 'Wick.ECO8 - Eco Series 8'},
                {'id': 'wick-007', 'name': 'Wick.LX10 - LX Series 10'},
                {'id': 'wick-008', 'name': 'Wick.LX12 - LX Series 12'}
            ]
        }


# Test function
def test_client():
    """Test the NetSuite client"""
    client = NetSuiteClient()
    
    print(f"Client configured: {client.is_configured}")
    print(f"Account ID: {client.account_id}")
    print(f"Base URL: {client.base_url}")
    
    if client.is_configured:
        print("\nTesting connection...")
        if client.test_connection():
            print("✅ Connection successful!")
            
            print("\nFetching candle products...")
            products = client.get_candle_products()
            
            for category, items in products.items():
                print(f"\n{category.title()}: {len(items)} items")
                for item in items[:3]:
                    print(f"  - {item['name']}")
        else:
            print("❌ Connection failed")
    else:
        print("\n⚠️  NetSuite not configured - using fallback data")
        products = client.get_candle_products()
        print(f"Fallback vessels: {len(products['vessels'])}")


if __name__ == "__main__":
    test_client()