"""
NetSuite REST API Client for direct integration
Supports both SuiteTalk REST API and SOAP Web Services
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
from urllib.parse import quote
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
        import math
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
            f"{k}={quote(str(v), safe='~')}" 
            for k, v in sorted_params
        ])
        
        # Create signature base string
        base_string = (
            method.upper() + '&' +
            quote(url, safe='~') + '&' +
            quote(param_string, safe='~')
        )
        
        # Create signing key
        signing_key = (
            quote(self.consumer_secret, safe='~') + '&' +
            quote(self.token_secret, safe='~')
        )
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            signing_key.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha256
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
            f'{k}="{quote(str(v), safe="~")}"' 
            for k, v in sorted(oauth_params.items())
        ])
        
        return auth_header
    
    def search_items(self, query: str = None, item_type: str = None) -> List[Dict[str, Any]]:
        """Search for items in NetSuite using REST Record API"""
        if not self.is_configured:
            return []
        
        items = []
        
        # Try different item types since 'item' is generic
        item_types = ['inventoryitem', 'noninventoryitem', 'assemblyitem', 'kititem', 'serviceitem']
        
        for record_type in item_types:
            try:
                url = f"{self.base_url}/services/rest/record/v1/{record_type}"
                
                # Build query parameters
                params = {
                    'limit': 20  # Limit per type
                }
                
                if query:
                    # Use q parameter for search
                    params['q'] = query
                
                headers = {
                    'Authorization': self._generate_oauth_header('GET', url),
                    'Accept': 'application/json'
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        # Extract relevant fields
                        items.append({
                            'id': item.get('id'),
                            'itemid': item.get('itemId', item.get('itemid', '')),
                            'displayname': item.get('displayName', item.get('salesdescription', '')),
                            'description': item.get('description', ''),
                            'itemtype': record_type
                        })
                elif response.status_code != 404:  # 404 means the record type doesn't exist
                    print(f"Error accessing {record_type}: {response.status_code}")
                    
            except Exception as e:
                print(f"Error searching {record_type}: {e}")
                
        return items
    
    def search_items_suiteql(self, query: str = None) -> List[Dict[str, Any]]:
        """Search for items using SuiteQL"""
        if not self.is_configured:
            return []
        
        url = f"{self.base_url}/services/rest/query/v1/suiteql"
        
        # Build SuiteQL query - use starts with for better filtering and exclude inactive
        if query:
            suiteql = f"SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE LOWER('{query}%') AND isinactive = 'F' ORDER BY itemid"
        else:
            suiteql = "SELECT id, itemid, displayname FROM item WHERE isinactive = 'F' ORDER BY itemid FETCH FIRST 100 ROWS ONLY"
        
        body = {"q": suiteql}
        
        headers = {
            'Authorization': self._generate_oauth_header('POST', url),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Prefer': 'transient'
        }
        
        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            if response.status_code == 200:
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
                print(f"SuiteQL search error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"SuiteQL search exception: {e}")
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
            
            url = f"{self.base_url}/services/rest/query/v1/suiteql"
            
            # Use SuiteQL to search for different product types with "starts with" patterns
            queries = {
                'vessels': [
                    # Items starting with VES only - exclude inactive items
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'ves%' AND isinactive = 'F' ORDER BY itemid",
                ],
                'waxes': [
                    # Items starting with WAX - exclude inactive items
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'wax%' AND isinactive = 'F' ORDER BY itemid",
                ],
                'fragrances': [
                    # Items starting with OIL, FO, or FRAG - exclude inactive items
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'oil%' AND isinactive = 'F' ORDER BY itemid",
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'fo-%' AND isinactive = 'F' ORDER BY itemid",
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'frag%' AND isinactive = 'F' ORDER BY itemid",
                ],
                'wicks': [
                    # Items starting with WICK or specific wick types - exclude inactive items
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'wick%' AND isinactive = 'F' ORDER BY itemid",
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'cd-%' AND isinactive = 'F' ORDER BY itemid",
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'eco-%' AND isinactive = 'F' ORDER BY itemid",
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'lx-%' AND isinactive = 'F' ORDER BY itemid",
                    "SELECT id, itemid, displayname FROM item WHERE LOWER(itemid) LIKE 'htp-%' AND isinactive = 'F' ORDER BY itemid",
                ]
            }
            
            for category, category_queries in queries.items():
                for query in category_queries:
                    headers = {
                        'Authorization': self._generate_oauth_header('POST', url),
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'Prefer': 'transient'
                    }
                    
                    response = requests.post(url, headers=headers, json={"q": query}, timeout=30)
                    
                    if response.status_code == 200:
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


# Alternative SOAP client for NetSuite (if REST API is not available)
class NetSuiteSoapClient:
    """NetSuite SOAP Web Services client using Zeep"""
    
    def __init__(self, account_id: str = None, email: str = None,
                 password: str = None, role: str = None):
        """Initialize SOAP client"""
        self.account_id = account_id or os.environ.get('NETSUITE_ACCOUNT_ID')
        self.email = email or os.environ.get('NETSUITE_EMAIL')
        self.password = password or os.environ.get('NETSUITE_PASSWORD')
        self.role = role or os.environ.get('NETSUITE_ROLE', '3')  # Default role ID
        
        self.is_configured = all([self.account_id, self.email, self.password])
        
        if self.is_configured:
            try:
                from zeep import Client
                from zeep.transports import Transport
                
                # WSDL URL for NetSuite
                wsdl_url = f"https://webservices.netsuite.com/wsdl/v2022_2_0/netsuite.wsdl"
                
                # Create client
                transport = Transport(timeout=30)
                self.client = Client(wsdl_url, transport=transport)
                
                # Set up passport for authentication
                self._setup_passport()
                
            except Exception as e:
                print(f"Error initializing SOAP client: {e}")
                self.is_configured = False
    
    def _setup_passport(self):
        """Set up NetSuite passport for SOAP authentication"""
        if not self.client:
            return
            
        passport = {
            'account': self.account_id,
            'email': self.email,
            'password': self.password,
            'role': {'internalId': self.role}
        }
        
        self.client.set_default_soapheaders([passport])
    
    def search_items(self, keyword: str) -> List[Dict[str, Any]]:
        """Search items using SOAP API"""
        if not self.is_configured:
            return []
            
        try:
            # Create search criteria
            search = self.client.get_type('ns5:ItemSearchBasic')()
            search.itemId = self.client.get_type('ns0:SearchStringField')(
                searchValue=f'%{keyword}%',
                operator='contains'
            )
            
            # Perform search
            response = self.client.service.search(searchRecord=search)
            
            items = []
            if response.body.searchResult.status.isSuccess:
                for record in response.body.searchResult.recordList.record:
                    items.append({
                        'id': record.internalId,
                        'itemid': record.itemId,
                        'displayname': getattr(record, 'displayName', ''),
                        'description': getattr(record, 'purchaseDescription', '')
                    })
            
            return items
            
        except Exception as e:
            print(f"SOAP search error: {e}")
            return []