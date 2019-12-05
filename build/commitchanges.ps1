$new_version = Get-Content .\VERSION -Raw
Write-Output "New Version: $new_version"

git add VERSION
git add .\build\esnake.spec

Write-Output "Committing"
git commit -m "v$new_version"

Write-Output "Tagging"
git tag -a v$new_version -m "Automated Release v$new_version"