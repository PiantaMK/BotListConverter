import importlib.util
import os

def fetch_modules(formats_dir, filter_func=lambda module: hasattr(module, '_main')):
    format_files = [f for f in os.listdir(formats_dir) if f.endswith('.py') and not f.startswith('_')]
    list_formats = []

    for format_file in format_files:
        module_name = os.path.splitext(format_file)[0]
        module_path = os.path.join(formats_dir, format_file)
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if filter_func(module):
            list_formats.append((module_name, module))

    return list_formats