$DOCKER_IMAGE_NAME = "crypto/telegram-crypto-alerts"

#Error handling utils
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['*:ErrorAction']='Stop'
function ThrowOnNativeFailure {
    if (-not $?)
    {
        throw 'Native Failure'
    }
}

# Read the file line by line
Get-Content ".\.env" | ForEach-Object {
    # Use regex to extract the key and value
    if ($_ -match "^\s*(DOCKER_REGISTRY)\s*=\s*(.+)\s*$") {
        # Set the environment variable
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

# Verify that the environment variable has been set
$DOCKER_REGISTRY = [System.Environment]::GetEnvironmentVariable("DOCKER_REGISTRY")
Write-Output "DOCKER_REGISTRY is set to: $DOCKER_REGISTRY"


$RegexMatches = Select-String -Path .\pyproject.toml -Pattern 'version\s*=\s*"(\d+\.\d+\.\d+)"'

$APP_VERSION = $RegexMatches.Matches.Groups[1].Value
Write-Host Releasing app with version: $APP_VERSION

$DOCKER_IMAGE_TAG = $DOCKER_IMAGE_NAME + "`:" + $APP_VERSION
$DOCKER_IMAGE_TAG_LATEST = $DOCKER_IMAGE_NAME + "`:latest"
$DOCKER_IMAGE_TAG_WITH_REGISTY = $DOCKER_REGISTRY + "/" + $DOCKER_IMAGE_TAG
Write-Host Building the image $DOCKER_IMAGE_TAG

docker build -t $DOCKER_IMAGE_TAG -t $DOCKER_IMAGE_TAG_LATEST -t $DOCKER_IMAGE_TAG_WITH_REGISTY .
ThrowOnNativeFailure

Write-Host Pushing the image $DOCKER_IMAGE_TAG to regisrty $DOCKER_IMAGE_TAG_WITH_REGISTY
docker push $DOCKER_IMAGE_TAG_WITH_REGISTY
ThrowOnNativeFailure

Write-Host Bumping the app version
poetry version patch

Write-Host The docker build was pushed. Use this commands to repull on the remote:
Write-Host docker pull $DOCKER_IMAGE_TAG_WITH_REGISTY
Write-Host docker tag $DOCKER_IMAGE_TAG_WITH_REGISTY $DOCKER_IMAGE_TAG_LATEST