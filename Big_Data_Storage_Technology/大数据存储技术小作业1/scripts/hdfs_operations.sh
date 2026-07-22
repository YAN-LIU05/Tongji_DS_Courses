#!/usr/bin/env bash

set -euo pipefail

readonly HDFS_DIR="/my_doc"
readonly HDFS_FILE="${HDFS_DIR}/sample.txt"
readonly LOCAL_FILE="/tmp/sample.txt"

upload_sample() {
  printf '%s\n' "hello hadoop" > "${LOCAL_FILE}"
  hdfs dfs -mkdir -p "${HDFS_DIR}"
  hdfs dfs -put -f "${LOCAL_FILE}" "${HDFS_FILE}"
}

inspect_sample() {
  hdfs dfs -ls "${HDFS_DIR}"
  hdfs dfs -stat "%n %b %o %r %y" "${HDFS_FILE}"
  hdfs dfs -cat "${HDFS_FILE}"
}

cleanup_sample() {
  if hdfs dfs -test -e "${HDFS_FILE}"; then
    hdfs dfs -rm "${HDFS_FILE}"
  fi

  if hdfs dfs -test -d "${HDFS_DIR}"; then
    hdfs dfs -rmdir "${HDFS_DIR}"
  fi

  rm -f "${LOCAL_FILE}"
}

case "${1:-all}" in
  upload)
    upload_sample
    ;;
  inspect)
    inspect_sample
    ;;
  cleanup)
    cleanup_sample
    ;;
  all)
    upload_sample
    inspect_sample
    ;;
  *)
    printf 'Usage: %s {upload|inspect|cleanup|all}\n' "$0" >&2
    exit 2
    ;;
esac
