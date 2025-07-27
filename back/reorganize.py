import os
import shutil

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Created directory: {path}")

def move_file(src, dest):
    if os.path.exists(src):
        shutil.move(src, dest)
        print(f"✅ Moved {src} to {dest}")

def reorganize():
    # Create new directories
    create_directory('core')
    create_directory('ui')
    create_directory('ui/components')
    create_directory('ui/pages')
    
    # Move core files
    core_files = [
        'database.py',
        'technical_analysis.py',
        'telegram_notifier.py',
        'monitor.py',
        'gerenciar_sinais.py'
    ]
    
    for file in core_files:
        move_file(file, f'core/{file}')
    
    # Move UI files
    ui_files = [
        'signals_container.py',
        'projection_container.py',
        'ticker_component.py'
    ]
    
    for file in ui_files:
        move_file(file, f'ui/components/{file}')
        
    # Move page files
    page_files = [
        'dashboard.py',
        'login.py',
        'landing_page.py'
    ]
    
    for file in page_files:
        if os.path.exists(file):
            move_file(file, f'ui/pages/{file}')

if __name__ == '__main__':
    print("\n=== Reorganizando estrutura do projeto ===")
    reorganize()
    print("\n✅ Reorganização concluída!")