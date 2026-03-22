import os
import json

sessions_path = r'C:\Users\drago\AppData\Roaming\Code\User\workspaceStorage\b7547eba30884d8a5a98562b7c243dac\chatSessions'
output_file = r'C:\Genesis_Bridge\ALL_CONVERATIONS_DUMP.txt'

with open(output_file, 'w', encoding='utf-8') as outfile:
    files = [f for f in os.listdir(sessions_path) if f.endswith('.json')]
    for filename in files:
        filepath = os.path.join(sessions_path, filename)
        outfile.write(f"\n{'='*60}\n")
        outfile.write(f"SESSION ID: {filename}\n")
        outfile.write(f"{'='*60}\n\n")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if 'requests' in data:
                    for req in data['requests']:
                        # USER MESSAGE
                        if 'message' in req and 'text' in req['message']:
                            outfile.write(f"USER: {req['message']['text']}\n\n")
                        
                        # COPILOT RESPONSE
                        if 'response' in req:
                            for part in req['response']:
                                if isinstance(part, dict):
                                    if 'value' in part:
                                        outfile.write(f"COPILOT: {part['value']}\n")
                                    elif 'content' in part and isinstance(part['content'], dict) and 'value' in part['content']:
                                        outfile.write(f"COPILOT: {part['content']['value']}\n")
                                    elif 'content' in part and isinstance(part['content'], str):
                                        outfile.write(f"COPILOT: {part['content']}\n")
                        outfile.write("\n")
        except Exception as e:
            outfile.write(f"[ERROR PARSING SESSION {filename}: {e}]\n")

print(f"Dump complete: {output_file}")
