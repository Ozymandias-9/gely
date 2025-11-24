import os
import re

PLACEHOLDER_REGEX = re.compile(r"{{\s*(\w+)\s*}}")
CONFIG_PLACEHOLDER_REGEX = re.compile(r"{\s*(\w+)\s*}")


def render_template(template_str: str, params: dict) -> str:
    """
    Replace {{ placeholders }} in template_str using params dict.
    Missing params remain untouched.
    """
    def replacer(match):
        key = match.group(1)
        return str(params.get(key, match.group(0)))  # keep original if missing

    return PLACEHOLDER_REGEX.sub(replacer, template_str)


def render_config_string(template_str: str, params: dict) -> str:
    """
    Replace { placeholders } in config strings using params dict.
    """
    def replacer(match):
        key = match.group(1)
        return str(params.get(key, match.group(0)))

    return CONFIG_PLACEHOLDER_REGEX.sub(replacer, template_str)


def render_filename(filename_template: str, params: dict) -> str:
    """Allow templated filenames like middleware_{{name}}.ts or {name}.js"""
    # Try config style first, then template style? 
    # Or just config style as filenames usually come from config.
    # The user config uses {name}.
    return render_config_string(filename_template, params)


def create_from_template(
    template_path: str,
    params: dict,
    output_dir: str,
    output_filename_template: str
):
    # Read template
    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()

    # Render contents and filename
    output_str = render_template(template_str, params)
    output_filename = render_filename(output_filename_template, params)

    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write output
    out_path = os.path.join(output_dir, output_filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_str)

    return out_path