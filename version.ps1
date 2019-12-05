$current_version = Get-Content .\VERSION -Raw
Write-Output "Current Version: $current_version"

Write-Output "Bumping Versions..."
pipenv run bumpversion --allow-dirty --current-version $current_version patch VERSION
pipenv run bumpversion --allow-dirty --current-version $current_version patch esnake.spec

$new_version = Get-Content .\VERSION -Raw
Write-Output "New Version: $new_version"

git add VERSION
git add esnake.spec

Write-Output "Committing"
git commit -m "v$new_version"

Write-Output "Tagging"
git tag -a v$new_version -m "Automated Release v$new_version"

Write-Output "Pushing"
git push origin --tags