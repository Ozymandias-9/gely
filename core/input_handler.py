import questionary
from core.store_manager import StoreManager

class InputHandler:
    def __init__(self, store_manager: StoreManager):
        self.store_manager = store_manager

    def handle_inputs(self, inputs_def: dict, context: dict):
        """
        Process inputs definition and update context.
        """
        for input_name, input_def in inputs_def.items():
            if input_name in context:
                continue

            prompt_text = input_def.get("prompt", f"Enter value for '{input_name}': ")
            input_type = input_def.get("type", "text")

            if input_type == "text":
                val = questionary.text(prompt_text).ask()
                context[input_name] = val
            
            elif input_type == "select":
                source = input_def.get("source", {})
                source_type = source.get("type")
                
                choices = []
                items_map = {} # Map display string to actual item object

                if source_type == "store":
                    collection_name = source.get("collection")
                    items = self.store_manager.get_collection(collection_name)
                    display_key = input_def.get("display_key", "name")
                    
                    for item in items:
                        label = item.get(display_key, "Unknown")
                        choices.append(label)
                        items_map[label] = item
                
                if not choices:
                    print(f"Warning: No choices found for {input_name}")
                    continue

                selection = questionary.select(prompt_text, choices=choices).ask()
                
                # Map selected item to context
                selected_item = items_map.get(selection)
                if selected_item:
                    mapping = input_def.get("map", {})
                    for context_key, item_key in mapping.items():
                        context[context_key] = selected_item.get(item_key)
                    
                    context[input_name] = selection
            
            else:
                # Fallback to text
                val = questionary.text(f"{prompt_text} (Unknown type '{input_type}')").ask()
                context[input_name] = val
