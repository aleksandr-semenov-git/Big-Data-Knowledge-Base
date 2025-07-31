#!/usr/bin/env python3
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime

class LinkUpdater:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.md_files = {}
        self.folder_structure = {}
        self.link_mapping = {}
        
    def scan_structure(self):
        """Scan the entire directory structure and build a mapping of files and folders."""
        print("Scanning directory structure...")
        
        for root, dirs, files in os.walk(self.root_dir):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            # Build folder structure
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                relative_path = os.path.relpath(dir_path, self.root_dir)
                self.folder_structure[relative_path] = dir_path
            
            # Build markdown files mapping
            for file in files:
                if file.endswith('.md') and file != 'README.md':
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.root_dir)
                    
                    # Get folder name from file path
                    folder_name = os.path.basename(os.path.dirname(file_path))
                    file_name_without_ext = os.path.splitext(file)[0]
                    
                    # Store file info
                    self.md_files[relative_path] = {
                        'full_path': file_path,
                        'folder_name': folder_name,
                        'file_name': file_name_without_ext,
                        'content_hash': self.get_file_hash(file_path)
                    }
        
        print(f"Found {len(self.md_files)} markdown files")
    
    def get_file_hash(self, file_path):
        """Get hash of file content for change detection."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def build_link_mapping(self):
        """Build a mapping of old names to new names for link updates."""
        print("Building link mapping...")
        
        for file_path, file_info in self.md_files.items():
            folder_name = file_info['folder_name']
            file_name = file_info['file_name']
            
            # Create mapping for folder-based links
            if folder_name == file_name:
                # This is a folder-level file (e.g., cloud_platforms/cloud_platforms.md)
                self.link_mapping[folder_name] = {
                    'type': 'folder',
                    'current_name': folder_name,
                    'file_path': file_path
                }
            else:
                # This is a subfolder file (e.g., cloud_platforms/aws/aws.md)
                self.link_mapping[file_name] = {
                    'type': 'file',
                    'current_name': file_name,
                    'file_path': file_path
                }
    
    def update_links_in_file(self, file_path):
        """Update links in a single markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
        
        original_content = content
        updated = False
        
        # Find all markdown links in the content
        link_pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(link_pattern, content)
        
        for link_name in matches:
            # Check if this link needs updating
            if link_name in self.link_mapping:
                new_name = self.link_mapping[link_name]['current_name']
                if new_name != link_name:
                    # Update the link
                    old_link = f'[[{link_name}]]'
                    new_link = f'[[{new_name}]]'
                    content = content.replace(old_link, new_link)
                    updated = True
                    print(f"  Updated link: {link_name} -> {new_name}")
        
        # Write updated content back
        if updated:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated links in {file_path}")
                return True
            except Exception as e:
                print(f"Error writing {file_path}: {e}")
                return False
        
        return False
    
    def regenerate_links_section(self, file_path):
        """Regenerate the entire Links section for a file based on current structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
        
        # Get parent and child folders
        parent_folder = self.get_parent_folder(file_path)
        child_folders = self.get_child_folders(file_path)
        
        # Create new links list
        links = []
        if parent_folder:
            links.append(f"- [[{parent_folder}]]")
        
        for child in child_folders:
            links.append(f"- [[{child}]]")
        
        # Find and replace the Links section
        links_pattern = r'(### Links\n)(.*?)(?=\n###|\n$|$)'
        match = re.search(links_pattern, content, re.DOTALL)
        
        if match:
            new_links_section = "### Links\n" + "\n".join(links) + "\n"
            new_content = re.sub(links_pattern, new_links_section, content, flags=re.DOTALL)
        else:
            # Add new links section after the frontmatter
            frontmatter_pattern = r'(---\n.*?\n---\n)'
            frontmatter_match = re.search(frontmatter_pattern, content, re.DOTALL)
            
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                rest_content = content[frontmatter_match.end():]
                new_links_section = "### Links\n" + "\n".join(links) + "\n"
                new_content = frontmatter + new_links_section + rest_content
            else:
                new_links_section = "### Links\n" + "\n".join(links) + "\n"
                new_content = new_links_section + content
        
        # Write the updated content back
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Regenerated links in {file_path}")
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    
    def get_parent_folder(self, file_path):
        """Get the immediate parent folder of a file."""
        file_dir = os.path.dirname(file_path)
        if file_dir == '.':
            return None
        
        parent_dir = os.path.dirname(file_dir)
        if parent_dir == '.':
            return None
        
        parent_folder = os.path.basename(parent_dir)
        
        # Check if the parent folder has a corresponding .md file
        parent_md_file = os.path.join(parent_dir, f"{parent_folder}.md")
        if os.path.exists(parent_md_file):
            return parent_folder
        else:
            return None
    
    def get_child_folders(self, file_path):
        """Get immediate child folders of a file's directory."""
        file_dir = os.path.dirname(file_path)
        if not os.path.exists(file_dir):
            return []
        
        child_folders = []
        try:
            for item in os.listdir(file_dir):
                item_path = os.path.join(file_dir, item)
                if os.path.isdir(item_path):
                    # Check if the directory has a corresponding .md file
                    md_file = os.path.join(item_path, f"{item}.md")
                    if os.path.exists(md_file):
                        child_folders.append(item)
        except PermissionError:
            pass
        
        return child_folders
    
    def run_update(self, regenerate_all=False):
        """Run the link update process."""
        print("Starting link update process...")
        print(f"Root directory: {self.root_dir}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # Scan current structure
        self.scan_structure()
        self.build_link_mapping()
        
        updated_files = 0
        
        # Update each markdown file
        for file_path, file_info in self.md_files.items():
            full_path = file_info['full_path']
            print(f"\nProcessing: {file_path}")
            
            if regenerate_all:
                # Regenerate entire links section
                if self.regenerate_links_section(full_path):
                    updated_files += 1
            else:
                # Update existing links
                if self.update_links_in_file(full_path):
                    updated_files += 1
        
        print(f"\n{'='*50}")
        print(f"Update complete!")
        print(f"Files processed: {len(self.md_files)}")
        print(f"Files updated: {updated_files}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    root_dir = "/home/user/PycharmProjects/Big-Data-Knowledge-Base"
    
    if not os.path.exists(root_dir):
        print(f"Root directory {root_dir} does not exist!")
        return
    
    updater = LinkUpdater(root_dir)
    
    # You can choose to either update existing links or regenerate all links
    # Set regenerate_all=True to completely regenerate all link sections
    # Set regenerate_all=False to only update existing links
    regenerate_all = True  # Change this based on your needs
    
    updater.run_update(regenerate_all=regenerate_all)

if __name__ == "__main__":
    main() 