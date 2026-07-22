package raft

import "raft-kv/kv"

type Role string

const (
	Follower  Role = "Follower"
	Candidate Role = "Candidate"
	Leader    Role = "Leader"
)

type Peer struct {
	ID       int    `json:"id"`
	APIAddr  string `json:"api_addr"`
	RaftAddr string `json:"raft_addr"`
	DataDir  string `json:"data_dir"`
}

type ClusterConfig struct {
	Nodes []Peer `json:"nodes"`
}

type LogEntry struct {
	Index   int        `json:"index"`
	Term    int        `json:"term"`
	Command kv.Command `json:"command"`
}

type Status struct {
	ID            int    `json:"id"`
	Role          Role   `json:"role"`
	Term          int    `json:"term"`
	LeaderID      int    `json:"leader_id"`
	LeaderAddr    string `json:"leader_addr,omitempty"`
	CommitIndex   int    `json:"commit_index"`
	LastApplied   int    `json:"last_applied"`
	LogLen        int    `json:"log_len"`
	LastLogIndex  int    `json:"last_log_index"`
	LastLogTerm   int    `json:"last_log_term"`
	SnapshotIndex int    `json:"snapshot_index"`
	SnapshotTerm  int    `json:"snapshot_term"`
	ClusterSize   int    `json:"cluster_size"`
	Member        bool   `json:"member"`
	ReadMode      string `json:"read_mode"`
}

type LeaderInfo struct {
	LeaderID   int    `json:"leader_id"`
	LeaderAddr string `json:"leader_addr"`
	IsLeader   bool   `json:"is_leader"`
}
