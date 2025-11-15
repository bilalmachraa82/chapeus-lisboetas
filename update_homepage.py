#!/usr/bin/env python3
"""Update homepage with Swiper carousel content"""

import subprocess
import sys

# Read the new content from file
with open('homepage_with_swiper.txt', 'r', encoding='utf-8') as f:
    new_content = f.read()

# Escape single quotes for SQL
new_content_escaped = new_content.replace("'", "''")
new_content_escaped = new_content_escaped.replace("\\", "\\\\")

# Create SQL command
sql_command = f"UPDATE lx_posts SET post_content = '{new_content_escaped}' WHERE ID = 22;"

# Write to SQL file
with open('update_homepage_final.sql', 'w', encoding='utf-8') as f:
    f.write(sql_command)

print("SQL file created: update_homepage_final.sql")

# Execute the update using docker
try:
    result = subprocess.run(
        ['docker', 'exec', 'chapeus_mysql', 'mysql', '-u', 'root', '-prootpassword', 'lisboetas_web'],
        input=sql_command.encode('utf-8'),
        capture_output=True,
        text=False
    )

    if result.returncode == 0:
        print("✓ Homepage updated successfully!")

        # Verify the update
        verify_sql = "SELECT CASE WHEN post_content LIKE '%featured-collections-carousel swiper%' THEN 'SUCCESS: Swiper carousel found' ELSE 'ERROR: Swiper not found' END as status FROM lx_posts WHERE ID = 22;"
        verify_result = subprocess.run(
            ['docker', 'exec', 'chapeus_mysql', 'mysql', '-u', 'root', '-prootpassword', 'lisboetas_web', '-e', verify_sql],
            capture_output=True,
            text=True
        )
        print(verify_result.stdout)
    else:
        print(f"Error updating homepage: {result.stderr}")
        sys.exit(1)

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)