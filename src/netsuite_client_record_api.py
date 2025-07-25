"""
Alternative NetSuite client using REST Record API instead of SuiteQL
"""

import os
import requests
import json
from typing import List, Dict, Any
from .netsuite_client import NetSuiteClient


class NetSuiteRecordClient(NetSuiteClient):
    """NetSuite client using REST Record API"""
    
    def search_items_record_api(self, query: str = None) -> List[Dict[str, Any]]:
        """Search items using REST Record API instead of SuiteQL"""
        if not self.is_configured:
            return []
        
        try:
            # Use the record API to get items
            url = f"{self.base_url}/services/rest/record/v1/item"
            
            # Add query parameters
            params = {
                'limit': 100,
                'fields': 'id,itemId,displayName,description,itemType'
            }
            
            if query:
                # Use q parameter for simple search
                params['q'] = query
            
            headers = {
                'Authorization': self._generate_oauth_header('GET', url),
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = []
                for item in data.get('items', []):
                    items.append({
                        'id': item.get('id'),
                        'itemid': item.get('itemId'),
                        'displayname': item.get('displayName'),
                        'description': item.get('description', ''),
                        'itemtype': item.get('itemType')
                    })
                return items
            else:
                print(f"Record API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error searching items via Record API: {e}")
            return []
    
    def get_item_by_id(self, item_id: str) -> Dict[str, Any]:
        """Get a specific item by ID"""
        if not self.is_configured:
            return {}
        
        try:
            url = f"{self.base_url}/services/rest/record/v1/item/{item_id}"
            
            headers = {
                'Authorization': self._generate_oauth_header('GET', url),
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Get item error: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"Error getting item: {e}")
            return {}
    
    def get_candle_products_record_api(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get candle products using Record API"""
        if not self.is_configured:
            return self._get_fallback_products()
        
        products = {
            'vessels': [],
            'waxes': [],
            'fragrances': [],
            'wicks': []
        }
        
        try:
            # Get all items first
            all_items = self.search_items_record_api()
            
            for item in all_items:
                item_name = (item.get('itemid') or '').lower()
                description = (item.get('description') or '').lower()
                display_name = (item.get('displayname') or '').lower()
                
                formatted_item = {
                    'id': str(item.get('id', '')),
                    'name': f"{item.get('itemid', '')} - {item.get('displayname', item.get('description', ''))}"
                }
                
                # Categorize items
                if (item_name.startswith('ves-') or 
                    'vessel' in description or 'vessel' in display_name or
                    'jar' in description or 'jar' in display_name or
                    'container' in description or 'container' in display_name):
                    products['vessels'].append(formatted_item)
                    
                elif (item_name.startswith('wax-') or 
                      'wax' in description or 'wax' in display_name):
                    products['waxes'].append(formatted_item)
                    
                elif (item_name.startswith('oil-') or 
                      'fragrance' in description or 'fragrance' in display_name or
                      'scent' in description or 'scent' in display_name):
                    products['fragrances'].append(formatted_item)
                    
                elif (item_name.startswith('wick') or 
                      'wick' in description or 'wick' in display_name):
                    products['wicks'].append(formatted_item)
            
            # If no products found, try specific searches
            if not any(products.values()):
                print("No products found in general search, trying specific searches...")
                
                # Search for specific prefixes
                for prefix in ['ves-', 'wax-', 'oil-', 'wick']:
                    items = self.search_items_record_api(prefix)
                    for item in items:
                        formatted_item = {
                            'id': str(item.get('id', '')),
                            'name': f"{item.get('itemid', '')} - {item.get('displayname', item.get('description', ''))}"
                        }
                        
                        if prefix == 'ves-':
                            products['vessels'].append(formatted_item)
                        elif prefix == 'wax-':
                            products['waxes'].append(formatted_item)
                        elif prefix == 'oil-':
                            products['fragrances'].append(formatted_item)
                        elif prefix == 'wick':
                            products['wicks'].append(formatted_item)
            
            return products
            
        except Exception as e:
            print(f"Error getting products via Record API: {e}")
            return self._get_fallback_products()