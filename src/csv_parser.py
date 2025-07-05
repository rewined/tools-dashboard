import csv
from typing import List, Dict, Any


class CSVParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = []
        self.columns = []
    
    def parse(self) -> List[Dict[str, Any]]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.columns = reader.fieldnames or []
                self.data = list(reader)
            return self.data
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {str(e)}")
    
    def get_columns(self) -> List[str]:
        if not self.columns:
            self.parse()
        return self.columns
    
    def validate_required_columns(self, required_columns: List[str]) -> bool:
        columns = self.get_columns()
        return all(col in columns for col in required_columns)