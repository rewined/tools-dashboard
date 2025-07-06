import os

print("Current working directory:", os.getcwd())
print("\nListing all files and directories:")

for root, dirs, files in os.walk('.'):
    level = root.replace('.', '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        print(f"{subindent}{file}")

print("\nChecking specific paths:")
print("data/ exists:", os.path.exists('data'))
print("data/products.csv exists:", os.path.exists('data/products.csv'))

if os.path.exists('data'):
    print("Files in data/:", os.listdir('data'))
else:
    print("data/ directory does not exist")