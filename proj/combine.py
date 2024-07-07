import os

# The output combined file
output_file = 'out.py'

def remove_imports(file_content):
    """Removes import statements from the given file content."""
    lines = file_content.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith(('import', 'from'))]
    return '\n'.join(filtered_lines)

try:
    os.remove(output_file)
except OSError:
    pass

with open(output_file, 'w') as outfile:
    # Copy content of main.py while retaining imports
    with open('bot.py', 'r') as mainfile:
        lines = mainfile.readlines()
        import_lines = []
        code_lines = []
        copy_import = True
        files_to_combine = []

        for line in lines:
            if copy_import and not line.strip().startswith(('import', 'from')):
                copy_import = False
            if copy_import:
                import_lines.append(line)
            else:
                if line.strip() == "## dev imports":
                    copy_import = False
                elif line.strip().startswith(('import', 'from')):
                    import_file_path = line.strip().split()[1] 
                    import_file_path = import_file_path.replace(".","/")
                    import_file_path = import_file_path + ".py"
                    files_to_combine.append(import_file_path)
                else:
                    code_lines.append(line)

        outfile.writelines(import_lines)
        outfile.write('\n\n# Appended content from other files\n\n')

        # Process each file and append their content excluding import statements
        for file_path in files_to_combine:
            with open(file_path, 'r') as infile:
                content = infile.read()
                filtered_content = remove_imports(content)
                outfile.write(f'# {file_path}\n')
                outfile.write(filtered_content)
                outfile.write('\n\n')

        outfile.writelines(code_lines)

print(f'Combined file created: {output_file}')
