import json
import os

class StoreManager:
    def __init__(self, store_path: str):
        self.store_path = store_path
        self.data = self.load()

    def load(self) -> dict:
        """Load data from the store file."""
        if not os.path.exists(self.store_path):
            return {}
        
        try:
            with open(self.store_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode {self.store_path}. Starting with empty store.")
            return {}

    def save(self):
        """Save data to the store file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.store_path)), exist_ok=True)
        
        with open(self.store_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def add_item(self, collection: str, key: str, item_data: dict):
        """Add or update an item in a collection."""        
        if collection not in self.data:
            self.data[collection] = {}
            
        self.data[collection][key] = item_data
        self.save()

    def get_collection(self, collection: str) -> list:
        """Return a list of items in the collection."""
        col = self.data.get(collection, {})
        if isinstance(col, dict):
            return list(col.values())
        return {}
