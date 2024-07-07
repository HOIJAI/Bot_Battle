import os

###############
# Update this #
###############
# List of files to combine
files_to_combine = [
    'data_structures/bot_state.py',
    'handlers/handle_attack/sample.py',
    'handlers/handle_claim_territory/sample.py',
    'handlers/handle_place_initial_troop/sample.py',
    'handlers/handle_redeem_cards/sample.py',
    'handlers/handle_distribute_troops/sample.py',
    'handlers/handle_troops_after_attack/sample.py',
    'handlers/handle_defend/sample.py',
    'handlers/handle_fortify/sample.py'
]

###############
# Update this #
###############
# List of dev imports to exclude
dev_imports = [
    'from data_structures.bot_state import BotState',
    'from handlers.handle_attack.sample import handle_attack',
    'from handlers.handle_claim_territory.sample import handle_claim_territory',
    'from handlers.handle_place_initial_troop.sample import handle_place_initial_troop',
    'from handlers.handle_redeem_cards.sample import handle_redeem_cards',
    'from handlers.handle_distribute_troops.sample import handle_distribute_troops',
    'from handlers.handle_troops_after_attack.sample import handle_troops_after_attack',
    'from handlers.handle_defend.sample import handle_defend',
    'from handlers.handle_fortify.sample import handle_fortify'
]

# The output combined file
output_file = 'out.py'

def remove_imports(file_content):
    """Removes import statements from the given file content."""
    lines = file_content.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith(('import', 'from'))]
    return '\n'.join(filtered_lines)

with open(output_file, 'w') as outfile:
    # Copy content of main.py while retaining imports
    with open('bot.py', 'r') as mainfile:
        lines = mainfile.readlines()
        import_lines = []
        code_lines = []
        is_import = True

        for line in lines:
            if is_import and not line.strip().startswith(('import', 'from')):
                is_import = False
            if is_import:
                import_lines.append(line)
            else:
                if line.strip() not in dev_imports:
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
