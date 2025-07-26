"""
Populate Wick-onomics Sample Data
This script populates the Supabase database with sample data for the wick-onomics system
"""

import os
from datetime import datetime, timedelta
import random
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def populate_vessels():
    """Populate vessel data"""
    print("🏺 Populating vessels...")
    
    vessels = [
        {
            'id': 'v001',
            'itemid': 'VES-2.5OZ-TIN',
            'name': '2.5oz Tin Container',
            'shape': 'tin',
            'diameter_mm': 50,
            'height_mm': 35,
            'volume_ml': 74,
            'material': 'metal',
            'double_wick': False,
            'heat_dissipation_factor': 1.2
        },
        {
            'id': 'v002',
            'itemid': 'VES-8OZ-TUMBLER',
            'name': '8oz Clear Glass Tumbler',
            'shape': 'tumbler',
            'diameter_mm': 75,
            'height_mm': 90,
            'volume_ml': 237,
            'material': 'glass',
            'double_wick': False,
            'heat_dissipation_factor': 1.0
        },
        {
            'id': 'v003',
            'itemid': 'VES-10OZ-JAR',
            'name': '10oz Mason Jar',
            'shape': 'jar',
            'diameter_mm': 80,
            'height_mm': 100,
            'volume_ml': 296,
            'material': 'glass',
            'double_wick': False,
            'heat_dissipation_factor': 0.95
        },
        {
            'id': 'v004',
            'itemid': 'VES-12OZ-CERAMIC',
            'name': '12oz Black Ceramic',
            'shape': 'tumbler',
            'diameter_mm': 85,
            'height_mm': 105,
            'volume_ml': 355,
            'material': 'ceramic',
            'double_wick': False,
            'heat_dissipation_factor': 0.85
        },
        {
            'id': 'v005',
            'itemid': 'VES-16OZ-LARGE',
            'name': '16oz Large Glass Jar',
            'shape': 'jar',
            'diameter_mm': 95,
            'height_mm': 120,
            'volume_ml': 473,
            'material': 'glass',
            'double_wick': True,
            'heat_dissipation_factor': 0.9
        }
    ]
    
    for vessel in vessels:
        try:
            supabase.table('vessels').upsert(vessel).execute()
            print(f"  ✅ {vessel['name']}")
        except Exception as e:
            print(f"  ❌ Error with {vessel['name']}: {e}")

def populate_wax_types():
    """Populate wax type data"""
    print("\n🕯️ Populating wax types...")
    
    wax_types = [
        {
            'id': 'w001',
            'itemid': 'WAX-SOY-C3',
            'name': 'Soy Wax C3 (Current)',
            'melt_point_celsius': 51,
            'viscosity_index': 0.7,
            'manufacturer': 'CandleScience',
            'manufacturer_notes': 'Standard soy wax, good scent throw',
            'base_type': 'soy'
        },
        {
            'id': 'w002',
            'itemid': 'WAX-COCO-APR',
            'name': 'Coco-Apricot Creme (New)',
            'melt_point_celsius': 48,
            'viscosity_index': 0.8,
            'manufacturer': 'CandleScience',
            'manufacturer_notes': 'Premium blend, excellent hot throw, softer wax',
            'base_type': 'blend'
        },
        {
            'id': 'w003',
            'itemid': 'WAX-PARASOY',
            'name': 'Parasoy Blend',
            'melt_point_celsius': 54,
            'viscosity_index': 0.6,
            'manufacturer': 'IGI',
            'manufacturer_notes': 'Paraffin-soy blend, harder finish',
            'base_type': 'blend'
        },
        {
            'id': 'w004',
            'itemid': 'WAX-COCONUT',
            'name': 'Pure Coconut Wax',
            'melt_point_celsius': 45,
            'viscosity_index': 0.9,
            'manufacturer': 'Cargill',
            'manufacturer_notes': 'Clean burning, requires larger wick',
            'base_type': 'coconut'
        }
    ]
    
    for wax in wax_types:
        try:
            supabase.table('wax_types').upsert(wax).execute()
            print(f"  ✅ {wax['name']}")
        except Exception as e:
            print(f"  ❌ Error with {wax['name']}: {e}")

def populate_fragrances():
    """Populate fragrance oil data"""
    print("\n🌸 Populating fragrance oils...")
    
    fragrances = [
        # Vanilla/Bakery (typically need larger wicks)
        {
            'id': 'f001',
            'itemid': 'FO-VANILLA-BEAN',
            'name': 'Vanilla Bean',
            'flash_point_celsius': 93,
            'specific_gravity': 1.05,
            'max_load_percentage': 10,
            'heat_index': -0.8,  # Cool burning
            'fragrance_category': 'vanilla',
            'density_rating': 'heavy'
        },
        {
            'id': 'f002',
            'itemid': 'FO-CINNAMON-ROLL',
            'name': 'Cinnamon Roll',
            'flash_point_celsius': 88,
            'specific_gravity': 1.08,
            'max_load_percentage': 8,
            'heat_index': -1.2,  # Very cool burning
            'fragrance_category': 'bakery',
            'density_rating': 'heavy'
        },
        # Citrus (typically burn easier)
        {
            'id': 'f003',
            'itemid': 'FO-LEMON-CITRUS',
            'name': 'Lemon Citrus Burst',
            'flash_point_celsius': 71,
            'specific_gravity': 0.85,
            'max_load_percentage': 12,
            'heat_index': 0.9,  # Hot burning
            'fragrance_category': 'citrus',
            'density_rating': 'light'
        },
        {
            'id': 'f004',
            'itemid': 'FO-GRAPEFRUIT',
            'name': 'Pink Grapefruit',
            'flash_point_celsius': 68,
            'specific_gravity': 0.87,
            'max_load_percentage': 12,
            'heat_index': 1.1,  # Hot burning
            'fragrance_category': 'citrus',
            'density_rating': 'light'
        },
        # Floral (medium)
        {
            'id': 'f005',
            'itemid': 'FO-LAVENDER',
            'name': 'Lavender Fields',
            'flash_point_celsius': 82,
            'specific_gravity': 0.95,
            'max_load_percentage': 10,
            'heat_index': 0.1,  # Neutral
            'fragrance_category': 'floral',
            'density_rating': 'medium'
        },
        {
            'id': 'f006',
            'itemid': 'FO-ROSE-GARDEN',
            'name': 'Rose Garden',
            'flash_point_celsius': 85,
            'specific_gravity': 0.98,
            'max_load_percentage': 10,
            'heat_index': -0.2,  # Slightly cool
            'fragrance_category': 'floral',
            'density_rating': 'medium'
        },
        # Fresh/Clean
        {
            'id': 'f007',
            'itemid': 'FO-OCEAN-BREEZE',
            'name': 'Ocean Breeze',
            'flash_point_celsius': 76,
            'specific_gravity': 0.90,
            'max_load_percentage': 12,
            'heat_index': 0.5,  # Slightly hot
            'fragrance_category': 'fresh',
            'density_rating': 'light'
        },
        # Woody/Spice
        {
            'id': 'f008',
            'itemid': 'FO-SANDALWOOD',
            'name': 'Sandalwood Musk',
            'flash_point_celsius': 91,
            'specific_gravity': 1.02,
            'max_load_percentage': 9,
            'heat_index': -0.6,  # Cool burning
            'fragrance_category': 'woody',
            'density_rating': 'heavy'
        }
    ]
    
    for fragrance in fragrances:
        try:
            supabase.table('fragrance_oils').upsert(fragrance).execute()
            print(f"  ✅ {fragrance['name']}")
        except Exception as e:
            print(f"  ❌ Error with {fragrance['name']}: {e}")

def populate_wicks():
    """Populate wick data"""
    print("\n🔥 Populating wicks...")
    
    # Wick size index mapping for cross-series comparison
    # Smaller index = smaller wick
    wick_data = []
    
    # CD Series (Cotton Core)
    cd_sizes = [2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20]
    for i, size in enumerate(cd_sizes):
        wick_data.append({
            'id': f'wick_cd_{size}',
            'itemid': f'WICK-CD-{size}',
            'name': f'CD-{size}',
            'series': 'CD',
            'size_number': size,
            'size_index': i + 1,  # 1-12
            'diameter_mm': 1.5 + (i * 0.2),
            'core_material': 'cotton',
            'coating': 'none',
            'certified_for': ['soy', 'paraffin', 'blend']
        })
    
    # ECO Series (Coreless Cotton)
    eco_sizes = [1, 2, 4, 6, 8, 10, 12, 14]
    for i, size in enumerate(eco_sizes):
        wick_data.append({
            'id': f'wick_eco_{size}',
            'itemid': f'WICK-ECO-{size}',
            'name': f'ECO-{size}',
            'series': 'ECO',
            'size_number': size,
            'size_index': i + 2,  # 2-9 (ECO runs slightly larger)
            'diameter_mm': 1.8 + (i * 0.25),
            'core_material': 'cotton',
            'coating': 'none',
            'certified_for': ['soy', 'coconut', 'blend']
        })
    
    # LX Series (Flat braided)
    lx_sizes = [8, 10, 12, 14, 16, 18, 20, 22]
    for i, size in enumerate(lx_sizes):
        wick_data.append({
            'id': f'wick_lx_{size}',
            'itemid': f'WICK-LX-{size}',
            'name': f'LX-{size}',
            'series': 'LX',
            'size_number': size,
            'size_index': i + 4,  # 4-11
            'diameter_mm': 2.0 + (i * 0.3),
            'core_material': 'cotton',
            'coating': 'none',
            'certified_for': ['soy', 'paraffin']
        })
    
    # HTP Series (Paper core)
    htp_sizes = [31, 41, 52, 62, 73, 83, 93, 104]
    for i, size in enumerate(htp_sizes):
        wick_data.append({
            'id': f'wick_htp_{size}',
            'itemid': f'WICK-HTP-{size}',
            'name': f'HTP-{size}',
            'series': 'HTP',
            'size_number': size,
            'size_index': i + 3,  # 3-10
            'diameter_mm': 1.7 + (i * 0.2),
            'core_material': 'paper',
            'coating': 'none',
            'certified_for': ['soy', 'paraffin', 'beeswax']
        })
    
    for wick in wick_data:
        try:
            supabase.table('wicks').upsert(wick).execute()
            print(f"  ✅ {wick['name']}")
        except Exception as e:
            print(f"  ❌ Error with {wick['name']}: {e}")

def populate_sample_assemblies():
    """Populate sample assembly data with known good combinations"""
    print("\n📦 Populating sample assemblies...")
    
    # Known good combinations for Soy C3 (current wax)
    assemblies = [
        # 2.5oz tins
        {'vessel': 'v001', 'wax': 'w001', 'fragrance': 'f001', 'load': 8.5, 'wick': 'wick_cd_4'},  # Vanilla
        {'vessel': 'v001', 'wax': 'w001', 'fragrance': 'f003', 'load': 10.0, 'wick': 'wick_cd_3'},  # Citrus
        {'vessel': 'v001', 'wax': 'w001', 'fragrance': 'f005', 'load': 9.0, 'wick': 'wick_eco_2'},  # Lavender
        
        # 8oz tumblers
        {'vessel': 'v002', 'wax': 'w001', 'fragrance': 'f001', 'load': 8.5, 'wick': 'wick_cd_8'},  # Vanilla
        {'vessel': 'v002', 'wax': 'w001', 'fragrance': 'f002', 'load': 8.0, 'wick': 'wick_cd_10'},  # Cinnamon
        {'vessel': 'v002', 'wax': 'w001', 'fragrance': 'f003', 'load': 10.0, 'wick': 'wick_cd_6'},  # Citrus
        {'vessel': 'v002', 'wax': 'w001', 'fragrance': 'f007', 'load': 9.5, 'wick': 'wick_eco_6'},  # Ocean
        
        # 10oz jars
        {'vessel': 'v003', 'wax': 'w001', 'fragrance': 'f001', 'load': 8.5, 'wick': 'wick_cd_10'},  # Vanilla
        {'vessel': 'v003', 'wax': 'w001', 'fragrance': 'f005', 'load': 9.0, 'wick': 'wick_eco_8'},  # Lavender
        {'vessel': 'v003', 'wax': 'w001', 'fragrance': 'f008', 'load': 8.0, 'wick': 'wick_lx_12'},  # Sandalwood
        
        # 12oz ceramic
        {'vessel': 'v004', 'wax': 'w001', 'fragrance': 'f002', 'load': 8.0, 'wick': 'wick_cd_14'},  # Cinnamon
        {'vessel': 'v004', 'wax': 'w001', 'fragrance': 'f006', 'load': 9.0, 'wick': 'wick_eco_10'},  # Rose
        
        # Some test results for the new wax (Coco-Apricot)
        {'vessel': 'v001', 'wax': 'w002', 'fragrance': 'f001', 'load': 8.5, 'wick': 'wick_cd_5'},  # +1 size
        {'vessel': 'v002', 'wax': 'w002', 'fragrance': 'f003', 'load': 10.0, 'wick': 'wick_cd_8'},  # +2 sizes
    ]
    
    for i, assembly in enumerate(assemblies):
        assembly_data = {
            'id': f'asm_{i+1:03d}',
            'itemid': f'CANDLE-{i+1:03d}',
            'name': f'Test Candle {i+1}',
            'vessel_id': assembly['vessel'],
            'wax_type_id': assembly['wax'],
            'fragrance_oil_id': assembly['fragrance'],
            'fragrance_load_percentage': assembly['load'],
            'wick_id_1': assembly['wick'],
            'approved_date': (datetime.now() - timedelta(days=random.randint(30, 365))).date().isoformat(),
            'status': 'approved'
        }
        
        try:
            supabase.table('assemblies').upsert(assembly_data).execute()
            print(f"  ✅ Assembly {i+1}")
        except Exception as e:
            print(f"  ❌ Error with assembly {i+1}: {e}")

def populate_test_results():
    """Populate sample test results"""
    print("\n🧪 Populating test results...")
    
    # Get assemblies
    assemblies = supabase.table('assemblies').select('*').execute()
    
    for assembly in assemblies.data[:10]:  # Just first 10 for sample data
        # Generate a passing test result
        test_result = {
            'assembly_id': assembly['id'],
            'test_date': (datetime.now() - timedelta(days=random.randint(1, 30))).date().isoformat(),
            'wax_type_id_tested': assembly['wax_type_id'],
            'wick_id_tested': assembly['wick_id_1'],
            'test_type': 'initial',
            'flame_height_mm': random.uniform(30, 40),
            'melt_pool_mm_at_1h': random.uniform(15, 25),
            'melt_pool_mm_at_2h': random.uniform(35, 50),
            'melt_pool_mm_at_4h': random.uniform(60, 80),
            'container_temp_celsius': random.uniform(45, 55),
            'mushrooming': False,
            'tunneling': False,
            'smoking': False,
            'extinguish_time_hours': random.uniform(40, 60),
            'pass': True,
            'notes': 'Good burn characteristics',
            'tested_by': 'Lab Tech 1'
        }
        
        try:
            supabase.table('test_results').insert(test_result).execute()
            print(f"  ✅ Test result for {assembly['name']}")
        except Exception as e:
            print(f"  ❌ Error with test result: {e}")

def populate_wax_conversion_samples():
    """Populate some wax conversion delta data"""
    print("\n🔄 Populating wax conversion patterns...")
    
    # Based on the assemblies we created, add conversion patterns
    conversions = [
        {
            'vessel_id': 'v001',  # 2.5oz tin
            'old_wax_type_id': 'w001',  # Soy C3
            'new_wax_type_id': 'w002',  # Coco-Apricot
            'wick_size_delta': 1,  # Need 1 size larger
            'confidence_score': 0.8,
            'sample_count': 5
        },
        {
            'vessel_id': 'v002',  # 8oz tumbler
            'old_wax_type_id': 'w001',
            'new_wax_type_id': 'w002',
            'wick_size_delta': 2,  # Need 2 sizes larger
            'confidence_score': 0.7,
            'sample_count': 3
        }
    ]
    
    for conv in conversions:
        try:
            supabase.table('wax_conversion_deltas').upsert(conv).execute()
            print(f"  ✅ Conversion pattern for {conv['vessel_id']}")
        except Exception as e:
            print(f"  ❌ Error with conversion pattern: {e}")

def main():
    """Run all population functions"""
    print("🚀 Starting Wick-onomics data population...\n")
    
    # Run in order of dependencies
    populate_vessels()
    populate_wax_types()
    populate_fragrances()
    populate_wicks()
    populate_sample_assemblies()
    populate_test_results()
    populate_wax_conversion_samples()
    
    print("\n✅ Data population complete!")
    print("\n📊 Summary:")
    print("- Vessels: 5 different sizes")
    print("- Wax Types: 4 (including new Coco-Apricot)")
    print("- Fragrances: 8 across different categories")
    print("- Wicks: 40+ across CD, ECO, LX, and HTP series")
    print("- Sample Assemblies: 14 approved combinations")
    print("- Test Results: Generated for training")
    print("- Wax Conversion Patterns: 2 initial patterns")
    
    print("\n🎯 Next steps:")
    print("1. Visit /wick-analytics to see the dashboard")
    print("2. Try the 'Quick Check' feature")
    print("3. Use 'Predict Wick' for new combinations")
    print("4. Log real test results to improve predictions")

if __name__ == "__main__":
    main()