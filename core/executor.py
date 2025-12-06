from core.handlers import handle_create_folder, handle_create_file, handle_append_to_file
from core.store_manager import StoreManager
from core.input_handler import InputHandler
from core.engine import render_vars

HANDLERS = {
    "create-folder": handle_create_folder,
    "create-file": handle_create_file,
    "append-to-file": handle_append_to_file
}

def execute_action(config: dict, action_name: str, cli_args: dict = None, config_dir: str = "."):
    """
    Execute a named action from the config.
    """
    if cli_args is None:
        cli_args = {}

    actions = config.get("actions", {})
    if action_name not in actions:
        print(f"Action '{action_name}' not found in config.")
        return

    action_def = actions[action_name]
    print(f"Executing action: {action_def.get('title', action_name)}")
    
    layers = action_def.get("layers", [])
    context = cli_args.copy()
    
    # Global/Project context
    context["project_root"] = os.getcwd()
    context["config_dir"] = config_dir

    # Initialize StoreManager
    settings = config.get("settings", {})
    store_file = settings.get("store_file", "gely/store.json")
    store_manager = StoreManager(store_file)
    
    # Initialize InputHandler
    input_handler = InputHandler(store_manager)

    # Process explicit inputs
    inputs = action_def.get("inputs", {})
    input_handler.handle_inputs(inputs, context)

    for i, layer in enumerate(layers):
        action_type = layer.get("action")
        if action_type not in HANDLERS:
            print(f"Unknown action type: {action_type} in layer {i}")
            continue
            
        print(f"  Running layer {i+1}: {action_type}")
        
        # Resolve Params
        layer_params = layer.get("params", [])
        resolved_params = {}
        
        # Handle list of params (mixed strings and dicts)
        for param in layer_params:
            for k, v in param.items():
                resolved_params[k] = v
        
        # Execute Handler
        handler = HANDLERS[action_type]
        try:
            result = handler(resolved_params, context)
        except Exception as e:
            print(f"    Error executing layer {i+1}: {e}")
            return

        # Handle Produces
        produces = layer.get("produces")
        if produces:
            if isinstance(produces, str):
                context[produces] = result
                print(f"    Produced {produces}: {result}")
    
    # Handle Store Directive
    store_def = action_def.get("store")
    if store_def:
        print("  Updating store...")
        collection = store_def.get("in")
        key_template = store_def.get("key")
        data_template = store_def.get("data", {})
        
        if collection and key_template:
            # Resolve key
            key = render_vars(key_template, context)
            
            # Resolve data
            data = {}
            for k, v in data_template.items():
                data[k] = render_vars(v, context)
            
            store_manager.add_item(collection, key, data)
            print(f"    Stored item '{key}' in '{collection}'")

    print("Action completed successfully.")

import os
