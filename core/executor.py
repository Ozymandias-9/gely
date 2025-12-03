from core.handlers import handle_create_folder, handle_create_file, handle_append_to_file

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

    # Process explicit inputs
    inputs = action_def.get("inputs", {})
    for input_name, input_def in inputs.items():
        if input_name not in context:
            prompt = input_def.get("prompt", f"Enter value for '{input_name}': ")
            val = input(f"{prompt} ")
            context[input_name] = val

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
            if isinstance(param, str):
                # User input required if not in context
                if param in context:
                    resolved_params[param] = context[param]
                else:
                    # Prompt user
                    val = input(f"    Enter value for '{param}': ")
                    resolved_params[param] = val
                    context[param] = val # Add to context for future use
            elif isinstance(param, dict):
                # Static or template param
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
            elif isinstance(produces, list):
                if len(produces) == 1 and not isinstance(result, (list, dict, tuple)):
                    context[produces[0]] = result
                    print(f"    Produced {produces[0]}: {result}")
                elif isinstance(result, dict):
                    for k in produces:
                        if k in result:
                            context[k] = result[k]
                            print(f"    Produced {k}: {result[k]}")
    
    print("Action completed successfully.")

import os
