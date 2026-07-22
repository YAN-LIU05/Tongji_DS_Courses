package raft

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
)

func LoadClusterConfig(path string) (ClusterConfig, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return ClusterConfig{}, err
	}
	data = bytes.TrimPrefix(data, []byte{0xEF, 0xBB, 0xBF})

	var cfg ClusterConfig
	if err := json.Unmarshal(data, &cfg); err != nil {
		return ClusterConfig{}, err
	}
	if len(cfg.Nodes) == 0 {
		return ClusterConfig{}, fmt.Errorf("cluster config has no nodes")
	}
	return cfg, nil
}
