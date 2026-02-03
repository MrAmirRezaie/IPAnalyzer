"""Example plugin showing plugin contract."""

def register():
    return {
        'name': 'example_plugin',
        'version': '0.1',
        'description': 'Example plugin that does nothing useful.'
    }
