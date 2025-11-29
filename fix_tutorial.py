
file_path = r'c:\Users\ASHWIN\Downloads\Pho-vite-main\Pho-vite-main\templates\tutorial.html'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Keep lines before the first occurrence (index 299) and from the second occurrence (index 491) onwards
new_lines = lines[:299] + lines[491:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Fixed file. New line count: {len(new_lines)}")
