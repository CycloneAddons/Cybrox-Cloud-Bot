import os
import importlib.util

def load_commands(commands_path):
    commands = {}
    command_files = [f for f in os.listdir(commands_path) if f.endswith('.py')]
    for file in command_files:
        module_name = file[:-3]
        file_path = os.path.join(commands_path, file)

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        commands[f"/{module.name}"] = module
        print(f"Loaded command: {module.name}")
    return commands

def load_callbacks(callbacks_path):
    callbacks = {}
    callback_files = [f for f in os.listdir(callbacks_path) if f.endswith('.py')]
    for file in callback_files:
        module_name = file[:-3]
        file_path = os.path.join(callbacks_path, file)

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, 'callback_data'):
            callbacks[module.callback_data] = module
            print(f"Loaded callback: {module.callback_data}")
    return callbacks
