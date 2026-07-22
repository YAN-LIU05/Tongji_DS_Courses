package raft

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type RequestVoteArgs struct {
	Term         int `json:"term"`
	CandidateID  int `json:"candidate_id"`
	LastLogIndex int `json:"last_log_index"`
	LastLogTerm  int `json:"last_log_term"`
}

type RequestVoteReply struct {
	Term        int  `json:"term"`
	VoteGranted bool `json:"vote_granted"`
}

type AppendEntriesArgs struct {
	Term         int        `json:"term"`
	LeaderID     int        `json:"leader_id"`
	PrevLogIndex int        `json:"prev_log_index"`
	PrevLogTerm  int        `json:"prev_log_term"`
	Entries      []LogEntry `json:"entries"`
	LeaderCommit int        `json:"leader_commit"`
}

type AppendEntriesReply struct {
	Term       int  `json:"term"`
	Success    bool `json:"success"`
	MatchIndex int  `json:"match_index"`
}

type InstallSnapshotArgs struct {
	Term              int               `json:"term"`
	LeaderID          int               `json:"leader_id"`
	LastIncludedIndex int               `json:"last_included_index"`
	LastIncludedTerm  int               `json:"last_included_term"`
	Snapshot          map[string]string `json:"snapshot"`
	Peers             []Peer            `json:"peers"`
	LeaderCommit      int               `json:"leader_commit"`
}

type InstallSnapshotReply struct {
	Term       int  `json:"term"`
	Success    bool `json:"success"`
	MatchIndex int  `json:"match_index"`
}

func (n *RaftNode) sendRequestVote(peer Peer, args RequestVoteArgs) (RequestVoteReply, bool) {
	var reply RequestVoteReply
	ok := n.postJSON(peer.RaftAddr, "/raft/request_vote", args, &reply)
	return reply, ok
}

func (n *RaftNode) sendAppendEntries(peer Peer, args AppendEntriesArgs) (AppendEntriesReply, bool) {
	var reply AppendEntriesReply
	ok := n.postJSON(peer.RaftAddr, "/raft/append_entries", args, &reply)
	return reply, ok
}

func (n *RaftNode) sendInstallSnapshot(peer Peer, args InstallSnapshotArgs) (InstallSnapshotReply, bool) {
	var reply InstallSnapshotReply
	ok := n.postJSON(peer.RaftAddr, "/raft/install_snapshot", args, &reply)
	return reply, ok
}

func (n *RaftNode) postJSON(addr, path string, request any, response any) bool {
	body, err := json.Marshal(request)
	if err != nil {
		return false
	}

	url := fmt.Sprintf("http://%s%s", addr, path)
	resp, err := n.client.Post(url, "application/json", bytes.NewReader(body))
	if err != nil {
		return false
	}
	defer resp.Body.Close()

	if resp.StatusCode < http.StatusOK || resp.StatusCode >= http.StatusMultipleChoices {
		return false
	}
	return json.NewDecoder(resp.Body).Decode(response) == nil
}
