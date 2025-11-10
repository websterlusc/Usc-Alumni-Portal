#!/usr/bin/env python3
"""
USC Brand Migration Script
Automated tool to help migrate existing files to new brand guidelines
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

class USCBrandMigrator:
    """Automated migration tool for USC brand guidelines"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "brand_migration_backup"
        
        # Color mapping: old -> new
        self.color_mapping = {
            # Primary greens
            '#1B5E20': '#10633C',  # Old primary -> USC Green Dark
            '#4CAF50': '#139B49',  # Old secondary -> USC Mid Green
            '#2E7D32': '#10633C',  # Another old green -> USC Green Dark
            '#388E3C': '#139B49',  # Another variant -> USC Mid Green
            
            # Yellows
            '#FDD835': '#FCCA18',  # Old yellow -> USC Yellow
            '#FFD600': '#FCCA18',  # Bright yellow -> USC Yellow
            '#FFC107': '#FCCA18',  # Bootstrap yellow -> USC Yellow
            
            # Greys and backgrounds
            '#F8F9FA': '#F2F2F2',  # Light gray -> USC Grey95
            '#E9ECEF': '#EFEFEF',  # Medium gray -> USC Light Grey
            '#495057': '#2E2E2E',  # Dark gray -> USC Dark Grey
            '#212529': '#2E2E2E',  # Text dark -> USC Dark Grey
            '#666666': '#2E2E2E',  # Text gray -> USC Dark Grey
            '#424242': '#2E2E2E',  # Another gray -> USC Dark Grey
        }
        
        # Font mapping: old -> new
        self.font_mapping = {
            'Inter': 'Source Sans 3',
            '"Inter"': '"Source Sans 3"',
            "'Inter'": "'Source Sans 3'",
            'font-family: Inter': 'font-family: Source Sans 3',
            'fontFamily: "Inter"': 'fontFamily: "Source Sans 3"',
            'fontFamily: \'Inter\'': 'fontFamily: \'Source Sans 3\'',
        }
        
        # Typography updates
        self.typography_updates = {
            'fontSize: \'1.25rem\'': 'fontSize: \'28.13px\'',  # H3 size
            'fontSize: "1.25rem"': 'fontSize: "28.13px"',
            'font-size: 1.25rem': 'font-size: 28.13px',
            'fontSize: \'2rem\'': 'fontSize: \'43.95px\'',    # H2 size  
            'fontSize: "2rem"': 'fontSize: "43.95px"',
            'font-size: 2rem': 'font-size: 43.95px',
        }
        
        self.files_processed = []
        self.changes_made = []
    
    def create_backup(self):
        """Create backup of project before migration"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print(f"Creating backup at {self.backup_dir}")
        
        # Copy key files to backup
        key_files = [
            "app.py",
            "components/navbar.py", 
            "pages/factbook_landing.py",
        ]
        
        self.backup_dir.mkdir(exist_ok=True)
        
        for file_path in key_files:
            if Path(file_path).exists():
                dest = self.backup_dir / Path(file_path).name
                shutil.copy2(file_path, dest)
                print(f"  Backed up: {file_path}")
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        
        for pattern in ["*.py", "**/*.py"]:
            python_files.extend(self.project_root.glob(pattern))
        
        # Filter out backup directory and common excludes
        excluded_patterns = [
            'brand_migration_backup',
            '__pycache__',
            '.git',
            'venv',
            'env',
            'node_modules'
        ]
        
        filtered_files = []
        for file_path in python_files:
            if not any(excluded in str(file_path) for excluded in excluded_patterns):
                filtered_files.append(file_path)
        
        return filtered_files
    
    def update_colors_in_file(self, file_path: Path) -> int:
        """Update color values in a single file"""
        changes_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update color hex codes
            for old_color, new_color in self.color_mapping.items():
                if old_color in content:
                    content = content.replace(old_color, new_color)
                    changes_count += 1
                    print(f"    Updated {old_color} -> {new_color}")
            
            # Update font families
            for old_font, new_font in self.font_mapping.items():
                if old_font in content:
                    content = content.replace(old_font, new_font)
                    changes_count += 1
                    print(f"    Updated font {old_font} -> {new_font}")
            
            # Update typography sizes
            for old_size, new_size in self.typography_updates.items():
                if old_size in content:
                    content = content.replace(old_size, new_size)
                    changes_count += 1
                    print(f"    Updated size {old_size} -> {new_size}")
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"    ✅ Updated {file_path}")
            
        except Exception as e:
            print(f"    ❌ Error updating {file_path}: {e}")
        
        return changes_count
    
    def update_usc_colors_dict(self, file_path: Path) -> bool:
        """Update USC_COLORS dictionary specifically"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for USC_COLORS dictionary pattern
            usc_colors_pattern = r"USC_COLORS\s*=\s*\{[^}]+\}"
            
            if re.search(usc_colors_pattern, content, re.DOTALL):
                # Replace the entire USC_COLORS dictionary
                new_usc_colors = """USC_COLORS = {
    # Primary USC Colors (Updated to Official Guidelines)
    'primary_green': '#10633C',      # USC Green Dark
    'mid_green': '#139B49',          # USC Mid Green  
    'wash_green': '#67A288',         # USC Wash Green
    'accent_yellow': '#FCCA18',      # USC Yellow
    
    # Custom USC Colors
    'black': '#000000',              # USC Black
    'dark_grey': '#2E2E2E',          # USC Dark Grey
    'mid_grey': '#CECECE',           # USC Mid Grey  
    'light_grey': '#EFEFEF',         # USC Light Grey
    'grey_95': '#F2F2F2',            # USC Grey95
    'off_white': '#FDFDFD',          # USC Off White
    'white': '#FFFFFF',              # Pure White
    
    # Legacy/Compatibility (for gradual migration)
    'secondary_green': '#139B49',    # Maps to mid_green
    'success_green': '#139B49',      # Maps to mid_green
    'light_gray': '#F2F2F2',         # Bootstrap compatible
    'medium_gray': '#EFEFEF',        # Bootstrap compatible  
    'text_dark': '#2E2E2E',          # Bootstrap compatible
    'text_gray': '#2E2E2E'           # Legacy compatibility
}"""
                
                content = re.sub(usc_colors_pattern, new_usc_colors, content, flags=re.DOTALL)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"    ✅ Updated USC_COLORS dictionary in {file_path}")
                return True
                
        except Exception as e:
            print(f"    ❌ Error updating USC_COLORS in {file_path}: {e}")
        
        return False
    
    def generate_migration_report(self):
        """Generate a detailed migration report"""
        report_path = self.project_root / "brand_migration_report.md"
        
        report_content = f"""# USC Brand Migration Report

## Migration Summary
- **Files Processed**: {len(self.files_processed)}
- **Total Changes**: {len(self.changes_made)}
- **Backup Location**: {self.backup_dir}

## Files Updated
"""
        
        for file_path in self.files_processed:
            report_content += f"- {file_path}\n"
        
        report_content += """
## Changes Made
"""
        
        for change in self.changes_made:
            report_content += f"- {change}\n"
        
        report_content += """
## Next Steps

### 1. Manual Review Required
- [ ] Check all heading typography uses Source Sans 3
- [ ] Verify body text uses Public Sans  
- [ ] Review component styling consistency
- [ ] Test responsive typography scaling

### 2. Component Updates
- [ ] Update button components with new colors
- [ ] Refresh card styling with USC brand
- [ ] Update navigation pills styling
- [ ] Review form components

### 3. Page-by-Page Review
- [ ] Homepage hero section
- [ ] Factbook landing page
- [ ] About USC pages
- [ ] Contact and info pages
- [ ] Admin dashboard

### 4. Testing Checklist
- [ ] Desktop typography scaling
- [ ] Mobile responsive behavior
- [ ] Color contrast accessibility
- [ ] Cross-browser compatibility
- [ ] Print stylesheet compatibility

## Brand Compliance Verification

### Typography ✓
- [ ] H1: 68.66px desktop, 54.93px mobile
- [ ] H2: 43.95px desktop, 35.16px mobile
- [ ] H3: 28.13px desktop, 22.5px mobile
- [ ] Body: 18px base size
- [ ] Small: 14.4px, Extra Small: 11.52px

### Colors ✓
- [ ] Primary Green: #10633C
- [ ] Mid Green: #139B49  
- [ ] Wash Green: #67A288
- [ ] USC Yellow: #FCCA18
- [ ] Dark Grey: #2E2E2E
- [ ] Light Grey: #EFEFEF
- [ ] Off White: #FDFDFD

---
Generated on migration completion
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📋 Migration report saved to: {report_path}")
    
    def run_migration(self, dry_run: bool = False):
        """Run the complete migration process"""
        print("🚀 Starting USC Brand Migration")
        print("=" * 50)
        
        if not dry_run:
            self.create_backup()
        
        # Find all Python files
        python_files = self.find_python_files()
        print(f"\n📁 Found {len(python_files)} Python files to process")
        
        total_changes = 0
        
        for file_path in python_files:
            print(f"\n🔍 Processing: {file_path}")
            
            if dry_run:
                print("    [DRY RUN - No changes made]")
                continue
            
            changes_in_file = 0
            
            # Update colors
            changes_in_file += self.update_colors_in_file(file_path)
            
            # Update USC_COLORS dictionary if present
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if 'USC_COLORS' in content:
                    if self.update_usc_colors_dict(file_path):
                        changes_in_file += 1
            except:
                pass
            
            if changes_in_file > 0:
                self.files_processed.append(str(file_path))
                self.changes_made.append(f"{file_path}: {changes_in_file} changes")
                total_changes += changes_in_file
            
        print(f"\n✅ Migration Complete!")
        print(f"📊 Total Changes Made: {total_changes}")
        print(f"📁 Files Updated: {len(self.files_processed)}")
        
        if not dry_run:
            self.generate_migration_report()
        
        print("\n⚠️  Important: Manual review required for:")
        print("   - Typography font assignments (heading vs body)")
        print("   - Component styling consistency") 
        print("   - Responsive behavior testing")
        print("   - Accessibility compliance")


def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='USC Brand Guidelines Migration Tool')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without modifying files')
    parser.add_argument('--project-root', default='.', 
                       help='Path to project root directory')
    
    args = parser.parse_args()
    
    migrator = USCBrandMigrator(args.project_root)
    migrator.run_migration(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
