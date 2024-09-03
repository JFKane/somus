import os
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import json
from json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bool):
            return str(obj)
        return JSONEncoder.default(self, obj)

def format_json(data):
    return json.dumps(data, indent=2, sort_keys=True, cls=CustomJSONEncoder)


def generate_html_report(task_id: str, results: Dict[str, Any]) -> str:
    """
    Generate an HTML report for the audio analysis results.
    
    :param task_id: The ID of the analysis task
    :param results: The results of the audio analysis
    :return: The path to the generated HTML report
    """
    # Create a directory for reports if it doesn't exist
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('core/templates'))
    
    # Add the custom function to the environment
    env.filters['format_json'] = format_json
    
    template = env.get_template('report_template.html')
    
    # Prepare data for the template
    report_data = {
        'task_id': task_id,
        'config': results.get('config', {}),
        'status': results.get('status', 'Unknown'),
        'results': results.get('results', [])
    }
    
    html_content = template.render(report_data)
    
    report_filename = f"report_{task_id}.html"
    report_path = os.path.join(report_dir, report_filename)
    
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    return report_path