$current_version = Get-Content .\VERSION -Raw
Write-Output "Current Version: $current_version"

Write-Output "Bumping Versions..."
pipenv run bumpversion --allow-dirty --current-version $current_version patch VERSION
pipenv run bumpversion --allow-dirty --current-version $current_version patch .\src\ESnake\app.py

$new_version = Get-Content .\VERSION -Raw
Write-Output "New Version: $new_version"

# sets Github Action variables
Write-Output "::set-output name=previous_version::$current_version"
Write-Output "::set-output name=new_version::$new_version"