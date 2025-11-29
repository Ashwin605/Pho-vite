
with open(r'c:\Users\ASHWIN\Downloads\Pho-vite-main\Pho-vite-main\templates\tutorial.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '<!-- FAQ Section -->' in line:
        print(f'Found at line {i+1}')
