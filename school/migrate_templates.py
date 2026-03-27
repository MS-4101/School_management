import os
import shutil
import re

SOURCE_LIBRARY = r"d:\VAIDITECH\School\library\templates"
SOURCE_BUS = r"d:\VAIDITECH\School\school_bus_tracker\templates"
DEST = r"d:\VAIDITECH\School\school\templates"

apps_to_copy = {
    SOURCE_LIBRARY: ['accounts', 'library_mgmt', 'lab_mgmt', 'inventory'],
    SOURCE_BUS: ['accounts', 'buses', 'notifications']
}

def migrate():
    if not os.path.exists(DEST):
        os.makedirs(DEST)
        
    for source_dir, apps in apps_to_copy.items():
        for app in apps:
            src_app_dir = os.path.join(source_dir, app)
            dest_app_dir = os.path.join(DEST, app)
            
            if not os.path.exists(src_app_dir):
                print(f"Skipping {src_app_dir}, not found.")
                continue
                
            if not os.path.exists(dest_app_dir):
                os.makedirs(dest_app_dir)
                
            for root, dirs, files in os.walk(src_app_dir):
                for file in files:
                    if not file.endswith('.html'):
                        continue
                        
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, src_app_dir)
                    dest_file = os.path.join(dest_app_dir, rel_path)
                    
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    
                    with open(src_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Applying Theme Standardization
                    # 1. Standardize extends
                    content = re.sub(r'{%\s*extends\s+[\'"][^\'"]+[\'"]\s*%}', "{% extends 'base.html' %}", content)
                    
                    # 2. Convert old library form classes to new theme classes
                    content = content.replace('form-input', 'form-control')
                    content = content.replace('btn btn-primary', 'btn-primary') 
                    # Note: in bustrack it's btn-primary, btn-primary-sm, etc. So btn btn-primary -> btn-primary is mostly fine
                    
                    # We might have conflicts in 'accounts' folder between library and bus. 
                    # If it's bus tracker accounts, we prefer it, so library overwrites bus? 
                    # Wait, our unified accounts app uses forms. We should be careful about accounts templates.
                    # Since SOURCE_LIBRARY is first, SOURCE_BUS will overwrite 'accounts' templates.
                    # That is actually preferred since BusTrack theme is better.
                    
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Migrated: {dest_file}")

if __name__ == "__main__":
    migrate()
    print("Migration complete.")
