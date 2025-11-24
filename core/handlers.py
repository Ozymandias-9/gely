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
    # Params is a list in the config example: ["name", {"template": "reducer.tpl"}, {"output": "..."}]
    # But the executor should probably normalize this before calling handler, 
    # OR the handler handles the raw list/dict. 
    # The user said: "params incluyen todos los parámetros necesarios... algunos params ya tienen una definición, mientras que otros params son simplemente strings"
    
    # Wait, the executor should have already prompted for the "string" params (user input) 
    # and merged them into the context/params before calling this?
    # Or does the handler do it? 
    # The plan said "ParamResolver (handle static vs user input)". 
    # So the executor should resolve params first.
    
    # So here 'params' should be a clean dict of resolved values?
    # Actually, looking at the config:
    # "params": [ "name", { "template": "reducer.tpl" }, { "output": "{reducer_folder}/{name}.reducer.js" } ]
    # The executor will iterate this list. If it's a string, it asks user (or checks context). 
    # If it's a dict, it merges it.
    # So by the time we get here, we should have a single dict of resolved parameters?
    # Let's assume the executor passes a merged dict of all resolved params.
    
    template_name = params.get("template")
    output_template = params.get("output")
    
    if not template_name or not output_template:
        raise ValueError("create-file requires 'template' and 'output' parameters")

    # We need to find the template file. 
    # Assuming templates are in a 'templates' folder relative to the project root or config?
    # For now, let's assume a 'templates' dir exists.
    # The user config has "template": "reducer.tpl".
    
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
    target_template = params.get("target")
    delimiter = params.get("delimiter")
    input_content = params.get("input") # This can be a variable name OR raw content?
    # Config says: { "input": "service_path"} (variable) OR { "input": "{name}Service" } (template string)
    
    if not target_template:
        raise ValueError("append-to-file requires 'target'")
        
    target_path = render_filename(target_template, context)
    
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target file for append not found: {target_path}")
        
    # Resolve input content
    # If input looks like a variable in context, use it? 
    # Or just render it as a template?
    # "{name}Service" -> Render
    # "service_path" -> If it's in context, use that value? 
    # But wait, "service_path" is a path. Do we want to append the PATH string or the CONTENT of that file?
    # The user example:
    # { "uses": ["service_path"], "action": "append-to-file", "params": [ { "input": "service_path"}, ... ] }
    # "service_path" was produced by create-file. So it's a filepath string.
    # The user probably wants to append the *import statement* or something?
    # Ah, looking at the config:
    # { "input": "service_path"}, { "target": "main/services/index.js" }, { "delimiter": "@imports" }
    # If I append "main/user/User.service.js", that's just a path. 
    # Maybe the user implies that `input` should be treated as a string to be appended.
    # If they want `import ...`, they should probably specify that in the input string or use a template.
    # But here they just put "service_path". 
    # Maybe they expect me to generate an import statement? 
    # "la idea es que esos params que vienen 'sin definición' puedan ser definidos al momento de usar la terminal y que eso valores pudieran dar pie a otros valores"
    # Maybe "service_path" is just the string value of the path.
    # Let's assume we just append the resolved string.
    
    # Try to resolve input as a variable first
    if input_content in context:
        content_to_append = str(context[input_content])
    else:
        # Render as config string
        content_to_append = render_config_string(input_content, context)
    
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
