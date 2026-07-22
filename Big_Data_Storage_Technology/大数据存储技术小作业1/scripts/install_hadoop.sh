#!/usr/bin/env bash

set -euo pipefail

readonly HADOOP_VERSION="3.3.6"
readonly HADOOP_HOME="/usr/local/hadoop"
readonly ARCHIVE="/tmp/hadoop-${HADOOP_VERSION}.tar.gz"
readonly DOWNLOAD_URL="https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"

if [[ ! -d "${HADOOP_HOME}" ]]; then
  wget -O "${ARCHIVE}" "${DOWNLOAD_URL}"
  tar -xzf "${ARCHIVE}" -C /usr/local
  mv "/usr/local/hadoop-${HADOOP_VERSION}" "${HADOOP_HOME}"
  rm -f "${ARCHIVE}"
fi

install -m 0644 /workspace/config/core-site.xml "${HADOOP_HOME}/etc/hadoop/core-site.xml"
install -m 0644 /workspace/config/hdfs-site.xml "${HADOOP_HOME}/etc/hadoop/hdfs-site.xml"
install -m 0644 /workspace/config/workers "${HADOOP_HOME}/etc/hadoop/workers"
install -m 0644 /workspace/config/hadoop-env.sh "${HADOOP_HOME}/etc/hadoop/hadoop-env.sh"

mkdir -p \
  "${HADOOP_HOME}/tmp/dfs/name" \
  "${HADOOP_HOME}/tmp/dfs/data"

cat > /etc/profile.d/hadoop.sh <<'EOF'
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_HOME=/usr/local/hadoop
export PATH="${PATH}:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin"
EOF

