import os
import re

PLACEHOLDER_REGEX = re.compile(r"{{\s*(\w+)\s*}}")
CONFIG_PLACEHOLDER_REGEX = re.compile(r"{\s*(\w+)\s*}")

def replacer(match, params):
    key = match.group(1)
    return str(params.get(key, match.group(0)))

def render_template(template_str: str, params: dict) -> str:
    """
    Replace {{ placeholders }} in template_str using params dict.
    Missing params remain untouched.
    """
    return PLACEHOLDER_REGEX.sub(lambda match: replacer(match, params), template_str)


def render_vars(template_str: str, params: dict) -> str:
    """
    Replace { placeholders } in config strings using params dict.
    """
    return CONFIG_PLACEHOLDER_REGEX.sub(lambda match: replacer(match, params), template_str)


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
    output_filename = render_vars(output_filename_template, params)

    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write output
    out_path = os.path.join(output_dir, output_filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_str)

    return out_path