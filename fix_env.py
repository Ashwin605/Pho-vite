import os

env_path = '.env'
new_lines = []

# Read existing
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Keep line if it doesn't start with MAIL_
            if not line.strip().startswith('MAIL_') and line.strip():
                new_lines.append(line.strip())

# Add Mail Config
new_lines.append("MAIL_SERVER=smtp.gmail.com")
new_lines.append("MAIL_PORT=587")
new_lines.append("MAIL_USE_TLS=True")
new_lines.append("MAIL_USERNAME=ashwinsrichandra2008@gmail.com")
new_lines.append("MAIL_PASSWORD=przh gigp dqjy izjz")

# Write back
with open(env_path, 'w') as f:
    f.write('\n'.join(new_lines))
    f.write('\n')

print("✅ .env updated successfully")
