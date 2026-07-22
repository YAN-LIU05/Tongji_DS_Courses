$ErrorActionPreference = "Stop"

$Master = "hadoop-master"
$Workers = @("hadoop-worker-1", "hadoop-worker-2")
$Nodes = @($Master) + $Workers

docker compose up -d
if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose failed to start."
}

foreach ($Node in $Nodes) {
    Write-Host "Installing dependencies on $Node..."
    docker exec $Node bash /workspace/scripts/install_dependencies.sh
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed on $Node."
    }

    Write-Host "Installing Hadoop on $Node..."
    docker exec $Node bash /workspace/scripts/install_hadoop.sh
    if ($LASTEXITCODE -ne 0) {
        throw "Hadoop installation failed on $Node."
    }
}

docker exec $Master bash -lc @'
set -e
if [[ ! -f /root/.ssh/id_rsa ]]; then
  ssh-keygen -q -t rsa -N "" -f /root/.ssh/id_rsa
fi
'@
if ($LASTEXITCODE -ne 0) {
    throw "Failed to generate the SSH key."
}

$PublicKey = docker exec $Master cat /root/.ssh/id_rsa.pub
if ($LASTEXITCODE -ne 0 -or -not $PublicKey) {
    throw "Failed to read the SSH public key."
}

foreach ($Node in $Nodes) {
    $PublicKey | docker exec -i $Node bash -c "cat > /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to configure the SSH public key on $Node."
    }
}

docker exec $Master bash -lc @'
set -e
touch /root/.ssh/known_hosts
ssh-keyscan -H hadoop-master hadoop-worker-1 hadoop-worker-2 >> /root/.ssh/known_hosts 2>/dev/null
chmod 600 /root/.ssh/known_hosts
source /etc/profile.d/hadoop.sh
if [[ ! -f /usr/local/hadoop/tmp/dfs/name/current/VERSION ]]; then
  hdfs namenode -format -force -nonInteractive
fi
start-dfs.sh
'@
if ($LASTEXITCODE -ne 0) {
    throw "Failed to format or start HDFS."
}

Write-Host "`nHDFS cluster processes:"
foreach ($Node in $Nodes) {
    Write-Host "[$Node]"
    docker exec $Node jps
}

Write-Host "`nNameNode Web UI: http://localhost:18070"
