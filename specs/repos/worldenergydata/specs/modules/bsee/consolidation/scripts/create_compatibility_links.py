#!/usr/bin/env python
"""
Create symbolic links for backward compatibility during BSEE data migration
This ensures existing code continues to work while we update references
"""

import os
from pathlib import Path
import json

class CompatibilityLinker:
    def __init__(self, data_dir: str = "data/modules/bsee"):
        self.data_dir = Path(data_dir)
        self.links_created = []
        
    def create_symlink(self, target: Path, link: Path):
        """Create a symbolic link for compatibility"""
        try:
            # Ensure parent directory exists
            link.parent.mkdir(parents=True, exist_ok=True)
            
            # Remove existing link if present
            if link.exists() or link.is_symlink():
                os.unlink(link)
            
            # Create relative symlink
            rel_target = os.path.relpath(target, link.parent)
            os.symlink(rel_target, link)
            
            self.links_created.append({
                'link': str(link),
                'target': str(target)
            })
            print(f"✓ Created symlink: {link} -> {rel_target}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to create symlink {link}: {e}")
            return False
    
    def create_compatibility_links(self):
        """Create all necessary compatibility links"""
        print("\n" + "="*50)
        print("CREATING COMPATIBILITY SYMBOLIC LINKS")
        print("="*50)
        
        # Map old paths to new paths
        compatibility_map = [
            # Link analysis_data to current for backward compatibility
            {
                'old': 'analysis_data/combined_data_for_analysis',
                'new': 'current'
            },
            # Specific file mappings
            {
                'old': 'analysis_data/combined_data_for_analysis/production.csv',
                'new': 'current/production/production.csv'
            },
            {
                'old': 'analysis_data/combined_data_for_analysis/well_data.csv',
                'new': 'current/wells/well_data.csv'
            },
            {
                'old': 'analysis_data/combined_data_for_analysis/well_directional_surveys.csv',
                'new': 'current/wells/well_directional_surveys.csv'
            },
            # Keep legacy references working temporarily
            {
                'old': 'legacy/data_for_analysis',
                'new': 'current'
            }
        ]
        
        for mapping in compatibility_map:
            old_path = self.data_dir / mapping['old']
            new_path = self.data_dir / mapping['new']
            
            if new_path.exists():
                self.create_symlink(new_path, old_path)
            else:
                print(f"⚠ Target doesn't exist yet: {new_path}")
        
        # Save link registry for later cleanup
        self.save_link_registry()
        
    def save_link_registry(self):
        """Save registry of created links for later cleanup"""
        registry_file = Path("specs/modules/bsee/consolidation/compatibility_links.json")
        
        with open(registry_file, 'w') as f:
            json.dump({
                'created': self.links_created,
                'note': 'These symlinks can be removed after code is updated',
                'cleanup_command': 'python remove_compatibility_links.py'
            }, f, indent=2)
        
        print(f"\n✓ Link registry saved to {registry_file}")
        print(f"  Total links created: {len(self.links_created)}")
    
    def verify_links(self):
        """Verify all links are working"""
        print("\n" + "="*50)
        print("VERIFYING SYMBOLIC LINKS")
        print("="*50)
        
        all_valid = True
        for link_info in self.links_created:
            link = Path(link_info['link'])
            if link.is_symlink() and link.exists():
                print(f"✓ Valid: {link}")
            else:
                print(f"✗ Invalid: {link}")
                all_valid = False
        
        return all_valid
    
    def generate_update_script(self):
        """Generate script to update code references"""
        script_lines = [
            "#!/usr/bin/env python",
            "# Script to update BSEE data path references in code",
            "",
            "import os",
            "import re",
            "from pathlib import Path",
            "",
            "# Path mappings",
            "path_updates = {",
            "    'analysis_data/combined_data_for_analysis': 'current',",
            "    'legacy/data_for_analysis': 'current',",
            "}",
            "",
            "def update_file(filepath):",
            "    with open(filepath, 'r') as f:",
            "        content = f.read()",
            "    ",
            "    original = content",
            "    for old_path, new_path in path_updates.items():",
            "        content = content.replace(old_path, new_path)",
            "    ",
            "    if content != original:",
            "        with open(filepath, 'w') as f:",
            "            f.write(content)",
            "        print(f'Updated: {filepath}')",
            "",
            "# Find and update Python files",
            "for root, dirs, files in os.walk('src'):",
            "    for file in files:",
            "        if file.endswith('.py'):",
            "            update_file(Path(root) / file)",
        ]
        
        script_file = Path("specs/modules/bsee/consolidation/scripts/update_code_references.py")
        with open(script_file, 'w') as f:
            f.write('\n'.join(script_lines))
        
        print(f"\n✓ Code update script generated: {script_file}")
        print("  Run this after migration to update all code references")


if __name__ == "__main__":
    linker = CompatibilityLinker()
    
    print("\n" + "="*50)
    print("BSEE COMPATIBILITY LINK CREATOR")
    print("="*50)
    print("\nThis script creates symbolic links to maintain")
    print("backward compatibility during the migration.")
    print("\nNOTE: Run this AFTER the migration executor")
    print("to ensure old code paths continue to work.")
    
    # Create compatibility links
    linker.create_compatibility_links()
    
    # Verify they work
    if linker.verify_links():
        print("\n✅ All compatibility links created successfully")
    else:
        print("\n⚠️ Some links failed - review output above")
    
    # Generate update script
    linker.generate_update_script()
    
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("="*50)
    print("1. Run migration executor to move files")
    print("2. Run this script to create compatibility links")
    print("3. Test that existing code still works")
    print("4. Gradually update code references")
    print("5. Remove compatibility links when done")