import os
import json
import glob

def consolidate():
    output_path = r"C:\SarahCore\Genlex\ALL_CONVERATIONS_CONSOLIDATED.txt"
    sources = []
    
    # 1. Add the existing dump (it's already massive)
    dump_path = r"C:\Genesis_Bridge\ALL_CONVERATIONS_DUMP.txt"
    if os.path.exists(dump_path):
        sources.append(dump_path)
        print(f"Adding source: {dump_path}")

    # 2. VS Code Chat Sessions
    vscode_chat_path = os.path.join(os.environ['APPDATA'], r"Code\User\workspaceStorage\b7547eba30884d8a5a98562b7c243dac\chatSessions\*.json")
    vscode_files = glob.glob(vscode_chat_path)
    print(f"Found {len(vscode_files)} VS Code chat session files.")

    # 3. Brain Artifacts
    brain_path = r"C:\Users\drago\.gemini\antigravity\brain\**\*.md"
    brain_files = glob.glob(brain_path, recursive=True)
    print(f"Found {len(brain_files)} brain artifacts.")

    with open(output_path, 'w', encoding='utf-8') as outfile:
        # Process existing dump
        if os.path.exists(dump_path):
            with open(dump_path, 'r', encoding='utf-8', errors='ignore') as infile:
                outfile.write("\n=== SOURCE: GENESIS BRIDGE DUMP ===\n")
                outfile.write(infile.read())
                outfile.write("\n")

        # Process VS Code Chats
        outfile.write("\n=== SOURCE: VS CODE CHAT SESSIONS ===\n")
        for f in vscode_files:
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as infile:
                    data = json.load(infile)
                    # Extract text from copilot sessions
                    if isinstance(data, dict) and 'requests' in data:
                        for req in data['requests']:
                            if 'message' in req: outfile.write(f"USER: {req['message']}\n")
                            if 'response' in req: 
                                if isinstance(req['response'], list):
                                    for res in req['response']:
                                        if isinstance(res, dict) and 'value' in res:
                                            outfile.write(f"SARAH: {res['value']}\n")
            except Exception as e:
                print(f"Error parsing {f}: {e}")

        # Process Brain Artifacts
        outfile.write("\n=== SOURCE: BRAIN ARTIFACTS ===\n")
        for f in brain_files:
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as infile:
                    outfile.write(f"\n--- ARTIFACT: {os.path.basename(f)} ---\n")
                    outfile.write(infile.read())
            except Exception as e:
                print(f"Error reading artifact {f}: {e}")

    print(f"Consolidation complete. Output: {output_path}")

if __name__ == "__main__":
    consolidate()
