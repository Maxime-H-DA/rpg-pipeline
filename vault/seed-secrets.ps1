$env = @{}
Get-Content .env | Where-Object { $_ -match "=" } | ForEach-Object {
    $key, $value = $_ -split "=", 2
    $env[$key] = $value
}

kubectl exec -n vault vault-0 -- vault kv put secret/rpg-api `
  ADMIN_USERNAME="$($env['ADMIN_USERNAME'])" `
  ADMIN_PASSWORD="$($env['ADMIN_PASSWORD'])" `
  API_SECRET_KEY="$($env['API_SECRET_KEY'])"
