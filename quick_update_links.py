#!/usr/bin/env python3
import os
import re
from datetime import datetime

def get_md_files(root_dir):
    """Get all markdown files in the directory tree, excluding .git directory."""
    md_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            if file.endswith('.md') and file != 'README.md':
                md_files.append(os.path.join(root, file))
    return md_files

def get_parent_folder(file_path):
    """Get the immediate parent folder of a file."""
    # Get the directory containing the file
    file_dir = os.path.dirname(file_path)
    if file_dir == '.':
        return None
    
    # Get the file name without extension
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Get the immediate parent folder name
    parent_folder = os.path.basename(file_dir)
    
    # If the file name matches the parent folder name, get the grandparent
    if file_name == parent_folder:
        parent_dir = os.path.dirname(file_dir)
        if parent_dir == '.':
            return None
        
        grandparent_folder = os.path.basename(parent_dir)
        
        # Check if the grandparent folder has a corresponding .md file
        grandparent_md_file = os.path.join(parent_dir, f"{grandparent_folder}.md")
        if os.path.exists(grandparent_md_file):
            return grandparent_folder
        else:
            return None
    else:
        # Check if the parent folder has a corresponding .md file
        parent_md_file = os.path.join(file_dir, f"{parent_folder}.md")
        if os.path.exists(parent_md_file):
            return parent_folder
        else:
            return None

def get_child_folders(file_path):
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

def update_links_section(file_path):
    """Update the Links section in a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    # Get parent and child folders
    parent_folder = get_parent_folder(file_path)
    child_folders = get_child_folders(file_path)
    
    # Create links list
    links = []
    if parent_folder:
        links.append(f"- [[{parent_folder}]]")
    
    for child in child_folders:
        links.append(f"- [[{child}]]")
    
    # Find the Links section
    links_pattern = r'(### Links\n)(.*?)(?=\n###|\n$|$)'
    match = re.search(links_pattern, content, re.DOTALL)
    
    if match:
        # Replace existing links section
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
        print(f"Updated {file_path}")
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False

def main():
    root_dir = "/home/user/PycharmProjects/Big-Data-Knowledge-Base"
    
    if not os.path.exists(root_dir):
        print(f"Root directory {root_dir} does not exist!")
        return
    
    print("Quick Link Update Tool")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    
    md_files = get_md_files(root_dir)
    print(f"Found {len(md_files)} markdown files")
    
    updated_count = 0
    for file_path in md_files:
        if update_links_section(file_path):
            updated_count += 1
    
    print(f"\n{'='*40}")
    print(f"Update complete!")
    print(f"Files processed: {len(md_files)}")
    print(f"Files updated: {updated_count}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 