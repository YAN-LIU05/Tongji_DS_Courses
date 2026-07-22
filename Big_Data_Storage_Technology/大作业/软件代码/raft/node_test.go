package raft

import (
	"encoding/json"
	"testing"

	"raft-kv/kv"
)

func newTestNode(t *testing.T, id int) (*RaftNode, []Peer) {
	t.Helper()

	peers := []Peer{
		{ID: 1, APIAddr: "127.0.0.1:18001", RaftAddr: "127.0.0.1:19001", DataDir: t.TempDir()},
		{ID: 2, APIAddr: "127.0.0.1:18002", RaftAddr: "127.0.0.1:19002", DataDir: t.TempDir()},
		{ID: 3, APIAddr: "127.0.0.1:18003", RaftAddr: "127.0.0.1:19003", DataDir: t.TempDir()},
	}
	node, err := NewRaftNode(id, peers)
	if err != nil {
		t.Fatalf("new node failed: %v", err)
	}
	return node, peers
}

func TestRequestVoteGrantsUpToDateCandidate(t *testing.T) {
	node, _ := newTestNode(t, 1)

	reply := node.HandleRequestVote(RequestVoteArgs{
		Term:         1,
		CandidateID:  2,
		LastLogIndex: 0,
		LastLogTerm:  0,
	})

	if !reply.VoteGranted {
		t.Fatal("expected vote granted")
	}
	status := node.Status()
	if status.Term != 1 || status.Role != Follower {
		t.Fatalf("unexpected status: %+v", status)
	}
}

func TestRequestVoteRejectsStaleCandidate(t *testing.T) {
	node, _ := newTestNode(t, 1)

	reply := node.HandleAppendEntries(AppendEntriesArgs{
		Term:         2,
		LeaderID:     2,
		PrevLogIndex: 0,
		PrevLogTerm:  0,
		Entries: []LogEntry{{
			Index:   1,
			Term:    2,
			Command: kv.Command{Op: kv.OpPut, Key: "a", Value: "1"},
		}},
		LeaderCommit: 0,
	})
	if !reply.Success {
		t.Fatalf("append failed: %+v", reply)
	}

	vote := node.HandleRequestVote(RequestVoteArgs{
		Term:         3,
		CandidateID:  3,
		LastLogIndex: 0,
		LastLogTerm:  0,
	})
	if vote.VoteGranted {
		t.Fatal("expected stale candidate to be rejected")
	}
}

func TestAppendEntriesCommitsAndApplies(t *testing.T) {
	node, _ := newTestNode(t, 2)

	reply := node.HandleAppendEntries(AppendEntriesArgs{
		Term:         1,
		LeaderID:     1,
		PrevLogIndex: 0,
		PrevLogTerm:  0,
		Entries: []LogEntry{{
			Index:   1,
			Term:    1,
			Command: kv.Command{Op: kv.OpPut, Key: "name", Value: "raft"},
		}},
		LeaderCommit: 1,
	})

	if !reply.Success || reply.MatchIndex != 1 {
		t.Fatalf("unexpected append reply: %+v", reply)
	}
	snapshot := node.Snapshot()
	if snapshot["name"] != "raft" {
		t.Fatalf("expected applied value raft, got snapshot=%v", snapshot)
	}
	status := node.Status()
	if status.CommitIndex != 1 || status.LastApplied != 1 || status.LogLen != 1 {
		t.Fatalf("unexpected status: %+v", status)
	}
}

func TestAppendEntriesTruncatesUncommittedConflict(t *testing.T) {
	node, _ := newTestNode(t, 2)

	first := node.HandleAppendEntries(AppendEntriesArgs{
		Term:         1,
		LeaderID:     1,
		PrevLogIndex: 0,
		PrevLogTerm:  0,
		Entries: []LogEntry{{
			Index:   1,
			Term:    1,
			Command: kv.Command{Op: kv.OpPut, Key: "name", Value: "old"},
		}},
		LeaderCommit: 0,
	})
	if !first.Success {
		t.Fatalf("first append failed: %+v", first)
	}

	second := node.HandleAppendEntries(AppendEntriesArgs{
		Term:         2,
		LeaderID:     1,
		PrevLogIndex: 0,
		PrevLogTerm:  0,
		Entries: []LogEntry{{
			Index:   1,
			Term:    2,
			Command: kv.Command{Op: kv.OpPut, Key: "name", Value: "new"},
		}},
		LeaderCommit: 1,
	})
	if !second.Success {
		t.Fatalf("second append failed: %+v", second)
	}

	snapshot := node.Snapshot()
	if snapshot["name"] != "new" {
		t.Fatalf("expected conflicting entry to be replaced and applied, got %v", snapshot)
	}
}

func TestSnapshotCompactsLogAndRestoresState(t *testing.T) {
	node, peers := newTestNode(t, 2)
	node.SetSnapshotThreshold(3)

	entries := []LogEntry{
		{Term: 1, Command: kv.Command{Op: kv.OpPut, Key: "k1", Value: "v1"}},
		{Term: 1, Command: kv.Command{Op: kv.OpPut, Key: "k2", Value: "v2"}},
		{Term: 1, Command: kv.Command{Op: kv.OpPut, Key: "k3", Value: "v3"}},
		{Term: 1, Command: kv.Command{Op: kv.OpPut, Key: "k4", Value: "v4"}},
	}
	reply := node.HandleAppendEntries(AppendEntriesArgs{
		Term:         1,
		LeaderID:     1,
		PrevLogIndex: 0,
		PrevLogTerm:  0,
		Entries:      entries,
		LeaderCommit: 4,
	})
	if !reply.Success {
		t.Fatalf("append failed: %+v", reply)
	}

	status := node.Status()
	if status.SnapshotIndex != 4 || status.LogLen != 0 {
		t.Fatalf("expected compacted snapshot at index 4, got %+v", status)
	}
	if node.log[0].Index != 4 || node.log[0].Term != 1 {
		t.Fatalf("unexpected compacted log base: %+v", node.log[0])
	}

	restored, err := NewRaftNode(2, peers)
	if err != nil {
		t.Fatalf("restore node failed: %v", err)
	}
	snapshot := restored.Snapshot()
	if snapshot["k4"] != "v4" {
		t.Fatalf("expected restored snapshot value v4, got %v", snapshot)
	}
	if restored.Status().SnapshotIndex != 4 {
		t.Fatalf("expected restored snapshot index 4, got %+v", restored.Status())
	}
}

func TestInstallSnapshotRestoresFollowerAndMembership(t *testing.T) {
	node, peers := newTestNode(t, 2)
	peers = append(peers, Peer{ID: 4, APIAddr: "127.0.0.1:18004", RaftAddr: "127.0.0.1:19004", DataDir: t.TempDir()})

	reply := node.HandleInstallSnapshot(InstallSnapshotArgs{
		Term:              2,
		LeaderID:          1,
		LastIncludedIndex: 8,
		LastIncludedTerm:  2,
		Snapshot:          map[string]string{"snap": "ok"},
		Peers:             peers,
		LeaderCommit:      8,
	})
	if !reply.Success || reply.MatchIndex != 8 {
		t.Fatalf("unexpected snapshot reply: %+v", reply)
	}
	status := node.Status()
	if status.SnapshotIndex != 8 || status.ClusterSize != 4 {
		t.Fatalf("unexpected status after install snapshot: %+v", status)
	}
	snapshot := node.Snapshot()
	if snapshot["snap"] != "ok" {
		t.Fatalf("expected restored snapshot value, got %v", snapshot)
	}
}

func TestCommittedMembershipCommandsUpdateCluster(t *testing.T) {
	node, _ := newTestNode(t, 2)
	newPeer := Peer{ID: 4, APIAddr: "127.0.0.1:18004", RaftAddr: "127.0.0.1:19004", DataDir: t.TempDir()}
	data, err := json.Marshal(newPeer)
	if err != nil {
		t.Fatalf("marshal peer failed: %v", err)
	}

	add := node.HandleAppendEntries(AppendEntriesArgs{
		Term:         1,
		LeaderID:     1,
		PrevLogIndex: 0,
		PrevLogTerm:  0,
		Entries: []LogEntry{{
			Term:    1,
			Command: kv.Command{Op: kv.OpAddNode, Key: "4", Value: string(data)},
		}},
		LeaderCommit: 1,
	})
	if !add.Success {
		t.Fatalf("add member append failed: %+v", add)
	}
	if got := node.Status().ClusterSize; got != 4 {
		t.Fatalf("expected cluster size 4 after add, got %d", got)
	}

	remove := node.HandleAppendEntries(AppendEntriesArgs{
		Term:         1,
		LeaderID:     1,
		PrevLogIndex: 1,
		PrevLogTerm:  1,
		Entries: []LogEntry{{
			Term:    1,
			Command: kv.Command{Op: kv.OpRemoveNode, Key: "3"},
		}},
		LeaderCommit: 2,
	})
	if !remove.Success {
		t.Fatalf("remove member append failed: %+v", remove)
	}

	peers := node.ClusterPeers()
	if len(peers) != 3 {
		t.Fatalf("expected cluster size 3 after remove, got peers=%v", peers)
	}
	for _, peer := range peers {
		if peer.ID == 3 {
			t.Fatalf("expected node 3 to be removed, got peers=%v", peers)
		}
	}
}
