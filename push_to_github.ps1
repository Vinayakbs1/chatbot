# PowerShell script to push the chatbot project to GitHub

# Create README.md file
echo "# chatbot" > README.md
Write-Host "Created README.md file"

# Initialize Git repository
git init
Write-Host "Initialized Git repository"

# Add README.md to staging area
git add README.md
Write-Host "Added README.md to staging area"

# Commit changes
git commit -m "first commit"
Write-Host "Committed changes with message 'first commit'"

# Rename default branch to main
git branch -M main
Write-Host "Renamed default branch to 'main'"

# Add remote repository
git remote add origin https://github.com/Vinayakbs1/chatbot.git
Write-Host "Added remote repository 'origin'"

# Push changes to remote repository
git push -u origin main
Write-Host "Pushed changes to remote repository"

Write-Host "All done! Your chatbot project is now on GitHub."
