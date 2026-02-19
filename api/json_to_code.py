# Developer: محمود عادل الغريب
# JSON → Python / PHP Code Generator
# OUTPUT: RAW CODE
# Use ?lang=python|php

from flask import Flask, request, Response
import json
import requests

app = Flask(__name__)

# =======================
# Helpers
# =======================

def is_list_array(value):
    if not isinstance(value, list):
        return False
    return True

# =======================
# Convert Python value → Python literal
# =======================

def py_to_python(value, indent=0):
    sp = "    " * indent

    if isinstance(value, list):
        items = [py_to_python(v, indent + 1) for v in value]
        return "[\n" + sp + "    " + (",\n" + sp + "    ").join(items) + "\n" + sp + "]"

    if isinstance(value, dict):
        items = [
            f"'{k}': {py_to_python(v, indent + 1)}"
            for k, v in value.items()
        ]
        return "{\n" + sp + "    " + (",\n" + sp + "    ").join(items) + "\n" + sp + "}"

    if isinstance(value, bool):
        return "True" if value else "False"
    if value is None:
        return "None"
    if isinstance(value, (int, float)):
        return str(value)

    return "'" + str(value).replace("'", "\\'") + "'"

# =======================
# Convert Python value → PHP literal
# =======================

def py_to_php(value, indent=0):
    sp = "    " * indent

    if isinstance(value, list):
        items = [py_to_php(v, indent + 1) for v in value]
        return "[\n" + sp + "    " + (",\n" + sp + "    ").join(items) + "\n" + sp + "]"

    if isinstance(value, dict):
        items = [
            f"'{k}' => {py_to_php(v, indent + 1)}"
            for k, v in value.items()
        ]
        return "[\n" + sp + "    " + (",\n" + sp + "    ").join(items) + "\n" + sp + "]"

    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)

    return "'" + str(value).replace("'", "\\'") + "'"

# =======================
# Generate Python print lines
# =======================

def generate_python_prints(data, path="data"):
    lines = []

    if isinstance(data, dict):
        for k, v in data.items():
            lines += generate_python_prints(v, f"{path}['{k}']")
    elif isinstance(data, list):
        for i, v in enumerate(data):
            lines += generate_python_prints(v, f"{path}[{i}]")
    else:
        comment = py_to_python(data)
        lines.append(f"print({path})  # {comment}")

    return lines

# =======================
# Generate PHP print lines
# =======================

def generate_php_prints(data, path="$data"):
    lines = []

    if isinstance(data, dict):
        for k, v in data.items():
            lines += generate_php_prints(v, f"{path}['{k}']")
    elif isinstance(data, list):
        for i, v in enumerate(data):
            lines += generate_php_prints(v, f"{path}[{i}]")
    else:
        comment = py_to_php(data)
        lines.append(f"echo {path}; // {comment}")

    return lines

# =======================
# Main Route
# =======================

@app.route("/", methods=["GET", "POST"])
def generate():

    lang = request.args.get("lang")
    json_data = request.form.get("data")
    url = request.args.get("url")

    if url:
        try:
            r = requests.get(url, timeout=5)
            json_data = r.text
        except:
            return Response("ERROR: Failed to fetch URL\n", mimetype="text/plain")

    if not json_data:
        return Response("ERROR: No JSON provided\n", mimetype="text/plain")

    try:
        data = json.loads(json_data)
    except:
        return Response("ERROR: Invalid JSON\n", mimetype="text/plain")

    output = ""

    if lang == "python":
        output += "# Auto-generated Python file\n\n"
        output += "data = " + py_to_python(data) + "\n\n"
        output += "# Print all values with comments\n"
        output += "\n".join(generate_python_prints(data))

    elif lang == "php":
        output += "<?php\n"
        output += "// Auto-generated PHP file\n\n"
        output += "$data = " + py_to_php(data) + ";\n\n"
        output += "// Print all values with comments\n"
        output += "\n".join(generate_php_prints(data))

    else:
        return Response("ERROR: lang must be 'python' or 'php'\n", mimetype="text/plain")

    return Response(output, mimetype="text/plain")
