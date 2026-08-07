import os
import glob
import re

components_dir = r'C:\Users\DARREN\Downloads\BUILDS\Consentinel\frontend\src\components'

for file_path in glob.glob(os.path.join(components_dir, '*.tsx')):
    if 'Dashboard' in file_path or 'Navigation' in file_path:
        continue

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace <div style={{ padding: '20px' }}> with <div className="page-container">
    content = re.sub(r'<div style={{ padding: \'20px\' }}>', r'<div className="page-container">', content)
    
    # Remove inline styles from tables and rows
    content = re.sub(r' style={{ width: \'100%\', textAlign: \'left\', borderCollapse: \'collapse\' }}', '', content)
    content = re.sub(r' style={{ borderBottom: \'1px solid #ccc\' }}', '', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print('Updated components')
