import os
from core.engine import render_template, render_filename, render_config_string

def handle_create_folder(params: dict, context: dict):
    """
    Handle 'create-folder' action.
    """
    # Resolve target
    target_raw = params.get("target")
    if not target_raw:
        raise ValueError("create-folder requires a 'target' parameter")
    
    # Render target with context
    target_dir = render_filename(target_raw, context)
    
    # Create directory
    os.makedirs(target_dir, exist_ok=True)
    
    # Return produced value (the path created)
    return target_dir

def handle_create_file(params: dict, context: dict):
    """
    Handle 'create-file' action.
    """
    
    template_name = params.get("template")
    output_template = params.get("output")
    
    if not template_name or not output_template:
        raise ValueError("create-file requires 'template' and 'output' parameters")
    
    config_dir = context.get("config_dir", ".")
    template_path = os.path.join(config_dir, "templates", template_name)
    
    if not os.path.exists(template_path):
        # Fallback to local templates dir if not found (optional)
        fallback_path = os.path.join("templates", template_name)
        if os.path.exists(fallback_path):
            template_path = fallback_path
        else:
            raise FileNotFoundError(f"Template not found: {template_path}")
        
    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()
        
    # Render content
    content = render_template(template_str, context)
    
    # Render output filename/path
    output_path = render_filename(output_template, context)
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return output_path

def handle_append_to_file(params: dict, context: dict):
    """
    Handle 'append-to-file' action.
    """
    target_file = params.get("target")
    delimiter = params.get("delimiter")
    template_name = params.get("template", "")
    input_content = params.get("input", "")
    config_dir = context.get("config_dir", ".")
    
    if not target_file:
        raise ValueError("append-to-file requires 'target'")
        
    target_path = render_filename(target_file, context)
    
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target file for append not found: {target_path}")
    
    content_to_append = ""

    if len(template_name) > 0:
        template_path = os.path.join(config_dir, "templates", template_name)
        
        if not os.path.exists(template_path):
            # Fallback to local templates dir if not found (optional)
            fallback_path = os.path.join("templates", template_name)
            if os.path.exists(fallback_path):
                template_path = fallback_path
            else:
                raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_str = f.read()
            
        # Render content
        content_to_append = render_template(template_str, context)
    # Try to resolve input as a variable first
    elif len(input_content) > 0:
        if input_content in context:
            content_to_append = str(context[input_content])
        else:
            # Render as config string
            content_to_append = render_config_string(input_content, context)
    else:
        raise ValueError("append-to-file requires 'input' or 'template'")
    
    with open(target_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find delimiter
    insert_index = -1
    for i, line in enumerate(lines):
        if delimiter in line:
            insert_index = i
            break
            
    if insert_index == -1:
        print(f"Warning: Delimiter '{delimiter}' not found in {target_path}. Appending to end.")
        lines.append(content_to_append + "\n")
    else:
        # Append BEFORE the delimiter line
        lines.insert(insert_index, content_to_append + "\n")
        
    with open(target_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    return None
