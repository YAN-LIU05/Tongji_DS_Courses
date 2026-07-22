package server

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"testing"
	"time"

	"raft-kv/raft"
)

type testCluster struct {
	peers   []raft.Peer
	nodes   []*raft.RaftNode
	servers []*HTTPServer
	client  *http.Client
}

type statusResponse struct {
	ID            int       `json:"id"`
	Role          raft.Role `json:"role"`
	LeaderID      int       `json:"leader_id"`
	LeaderAddr    string    `json:"leader_addr"`
	CommitIndex   int       `json:"commit_index"`
	LastLogIndex  int       `json:"last_log_index"`
	SnapshotIndex int       `json:"snapshot_index"`
	LogLen        int       `json:"log_len"`
	ClusterSize   int       `json:"cluster_size"`
}

type putResponse struct {
	OK    bool `json:"ok"`
	Index int  `json:"index"`
	Term  int  `json:"term"`
}

type getResponse struct {
	Found    bool   `json:"found"`
	Key      string `json:"key"`
	Value    string `json:"value"`
	ReadMode string `json:"read_mode"`
}

type clientErrorResponse struct {
	Error      string `json:"error"`
	LeaderID   int    `json:"leader_id"`
	LeaderAddr string `json:"leader_addr"`
}

func TestFollowerWriteReturnsLeaderInfoOverHTTP(t *testing.T) {
	cluster := startTestCluster(t, 3, 64)
	leader := cluster.waitForLeader(t, 6*time.Second)
	follower := cluster.waitForFollowerAwareOfLeader(t, leader.ID, 4*time.Second)

	var errResp clientErrorResponse
	cluster.postJSON(t, cluster.peerAddrByID(t, follower.ID), "/kv/put", map[string]string{"key": "wrong_node", "value": "x"}, http.StatusConflict, &errResp)
	if errResp.Error != "not leader" || errResp.LeaderID != leader.ID || errResp.LeaderAddr != leader.LeaderAddr {
		t.Fatalf("expected leader redirect info, got %+v leader=%+v", errResp, leader)
	}
}

func TestThreeNodeLeaderFailoverOverHTTP(t *testing.T) {
	cluster := startTestCluster(t, 3, 64)
	leader := cluster.waitForLeader(t, 6*time.Second)

	var before putResponse
	cluster.postJSON(t, leader.LeaderAddr, "/kv/put", map[string]string{"key": "before_failover", "value": "ok"}, http.StatusOK, &before)
	if !before.OK {
		t.Fatalf("put before failover failed: %+v", before)
	}

	cluster.stopNode(t, cluster.peerIndexByID(t, leader.ID))
	newLeader := cluster.waitForLeader(t, 8*time.Second)
	if newLeader.ID == leader.ID {
		t.Fatalf("expected a different leader after stopping node %d", leader.ID)
	}

	var afterPut putResponse
	cluster.postJSON(t, newLeader.LeaderAddr, "/kv/put", map[string]string{"key": "after_leader_down", "value": "ok"}, http.StatusOK, &afterPut)
	if !afterPut.OK {
		t.Fatalf("put after leader failover failed: %+v", afterPut)
	}

	var afterGet getResponse
	cluster.getJSON(t, newLeader.LeaderAddr, "/kv/get?key=after_leader_down", http.StatusOK, &afterGet)
	if !afterGet.Found || afterGet.Value != "ok" {
		t.Fatalf("unexpected get after leader failover: %+v", afterGet)
	}
}

func TestFiveNodeClusterSurvivesTwoFollowerFailuresOverHTTP(t *testing.T) {
	cluster := startTestCluster(t, 5, 64)
	leader := cluster.waitForLeader(t, 6*time.Second)

	var put putResponse
	cluster.postJSON(t, leader.LeaderAddr, "/kv/put", map[string]string{"key": "name", "value": "raft5"}, http.StatusOK, &put)
	if !put.OK {
		t.Fatalf("put failed: %+v", put)
	}

	var get getResponse
	cluster.getJSON(t, leader.LeaderAddr, "/kv/get?key=name", http.StatusOK, &get)
	if !get.Found || get.Value != "raft5" || get.ReadMode != "lease_read" {
		t.Fatalf("unexpected get response: %+v", get)
	}

	stopped := 0
	for i, peer := range cluster.peers {
		if peer.ID == leader.ID {
			continue
		}
		cluster.stopNode(t, i)
		stopped++
		if stopped == 2 {
			break
		}
	}

	var failoverPut putResponse
	cluster.postJSON(t, leader.LeaderAddr, "/kv/put", map[string]string{"key": "after_two_followers_down", "value": "ok"}, http.StatusOK, &failoverPut)
	if !failoverPut.OK {
		t.Fatalf("put after follower failures failed: %+v", failoverPut)
	}

	var after getResponse
	cluster.getJSON(t, leader.LeaderAddr, "/kv/get?key=after_two_followers_down", http.StatusOK, &after)
	if !after.Found || after.Value != "ok" {
		t.Fatalf("unexpected get after follower failures: %+v", after)
	}
}

func TestSnapshotCompactionVisibleThroughHTTPStatus(t *testing.T) {
	cluster := startTestCluster(t, 3, 3)
	leader := cluster.waitForLeader(t, 6*time.Second)

	for i := 1; i <= 5; i++ {
		var put putResponse
		cluster.postJSON(t, leader.LeaderAddr, "/kv/put", map[string]string{
			"key":   fmt.Sprintf("snap%d", i),
			"value": fmt.Sprintf("v%d", i),
		}, http.StatusOK, &put)
	}

	status := cluster.waitForStatus(t, leader.LeaderAddr, 3*time.Second, func(s statusResponse) bool {
		return s.SnapshotIndex >= 3 && s.LogLen < s.LastLogIndex
	})
	if status.SnapshotIndex < 3 {
		t.Fatalf("expected compacted snapshot, got %+v", status)
	}

	var get getResponse
	cluster.getJSON(t, leader.LeaderAddr, "/kv/get?key=snap5", http.StatusOK, &get)
	if !get.Found || get.Value != "v5" {
		t.Fatalf("unexpected get after snapshot: %+v", get)
	}
}

func TestDynamicAddNodeCatchesUpOverHTTP(t *testing.T) {
	cluster := startTestCluster(t, 3, 64)
	leader := cluster.waitForLeader(t, 6*time.Second)

	newPeer := raft.Peer{
		ID:       4,
		APIAddr:  freeAddr(t),
		RaftAddr: freeAddr(t),
		DataDir:  t.TempDir(),
	}
	var add putResponse
	cluster.postJSON(t, leader.LeaderAddr, "/cluster/add", newPeer, http.StatusOK, &add)
	if !add.OK {
		t.Fatalf("add node failed: %+v", add)
	}

	cluster.peers = append(cluster.peers, newPeer)
	node, err := raft.NewRaftNode(newPeer.ID, cluster.peers)
	if err != nil {
		t.Fatalf("new node 4 failed: %v", err)
	}
	node.SetSnapshotThreshold(64)
	srv := NewHTTPServer(node)
	_ = srv.Start()
	node.Start()
	cluster.nodes = append(cluster.nodes, node)
	cluster.servers = append(cluster.servers, srv)

	cluster.waitForStatus(t, leader.LeaderAddr, 4*time.Second, func(s statusResponse) bool {
		return s.ClusterSize == 4
	})

	var put putResponse
	cluster.postJSON(t, leader.LeaderAddr, "/kv/put", map[string]string{"key": "node4", "value": "caught-up"}, http.StatusOK, &put)
	if !put.OK {
		t.Fatalf("put after dynamic add failed: %+v", put)
	}

	cluster.waitForStatus(t, newPeer.APIAddr, 5*time.Second, func(s statusResponse) bool {
		return s.CommitIndex >= put.Index && s.ClusterSize == 4
	})
}

func startTestCluster(t *testing.T, n int, snapshotThreshold int) *testCluster {
	t.Helper()

	cluster := &testCluster{
		peers:   make([]raft.Peer, 0, n),
		nodes:   make([]*raft.RaftNode, 0, n),
		servers: make([]*HTTPServer, 0, n),
		client:  &http.Client{Timeout: 700 * time.Millisecond},
	}
	for i := 1; i <= n; i++ {
		cluster.peers = append(cluster.peers, raft.Peer{
			ID:       i,
			APIAddr:  freeAddr(t),
			RaftAddr: freeAddr(t),
			DataDir:  t.TempDir(),
		})
	}

	for _, peer := range cluster.peers {
		node, err := raft.NewRaftNode(peer.ID, cluster.peers)
		if err != nil {
			t.Fatalf("new node %d failed: %v", peer.ID, err)
		}
		node.SetSnapshotThreshold(snapshotThreshold)
		srv := NewHTTPServer(node)
		_ = srv.Start()
		node.Start()
		cluster.nodes = append(cluster.nodes, node)
		cluster.servers = append(cluster.servers, srv)
	}

	t.Cleanup(func() {
		for i := range cluster.nodes {
			cluster.stopNode(t, i)
		}
	})
	return cluster
}

func (c *testCluster) waitForLeader(t *testing.T, timeout time.Duration) statusResponse {
	t.Helper()

	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		var leaders []statusResponse
		for _, peer := range c.peers {
			var status statusResponse
			if err := c.getJSONErr(peer.APIAddr, "/status", &status); err != nil {
				continue
			}
			if status.Role == raft.Leader {
				leaders = append(leaders, status)
			}
		}
		if len(leaders) == 1 {
			return leaders[0]
		}
		time.Sleep(100 * time.Millisecond)
	}
	t.Fatalf("timed out waiting for one leader")
	return statusResponse{}
}

func (c *testCluster) waitForFollowerAwareOfLeader(t *testing.T, leaderID int, timeout time.Duration) statusResponse {
	t.Helper()

	deadline := time.Now().Add(timeout)
	var last statusResponse
	for time.Now().Before(deadline) {
		for _, peer := range c.peers {
			var status statusResponse
			if err := c.getJSONErr(peer.APIAddr, "/status", &status); err != nil {
				continue
			}
			last = status
			if status.Role == raft.Follower && status.LeaderID == leaderID && status.LeaderAddr != "" {
				return status
			}
		}
		time.Sleep(100 * time.Millisecond)
	}
	t.Fatalf("timed out waiting for follower to learn leader %d, last=%+v", leaderID, last)
	return statusResponse{}
}

func (c *testCluster) waitForStatus(t *testing.T, addr string, timeout time.Duration, ok func(statusResponse) bool) statusResponse {
	t.Helper()

	deadline := time.Now().Add(timeout)
	var last statusResponse
	for time.Now().Before(deadline) {
		if err := c.getJSONErr(addr, "/status", &last); err == nil && ok(last) {
			return last
		}
		time.Sleep(100 * time.Millisecond)
	}
	t.Fatalf("timed out waiting for status condition on %s, last=%+v", addr, last)
	return statusResponse{}
}

func (c *testCluster) peerIndexByID(t *testing.T, id int) int {
	t.Helper()
	for i, peer := range c.peers {
		if peer.ID == id {
			return i
		}
	}
	t.Fatalf("node id %d not found", id)
	return -1
}

func (c *testCluster) peerAddrByID(t *testing.T, id int) string {
	t.Helper()
	for _, peer := range c.peers {
		if peer.ID == id {
			return peer.APIAddr
		}
	}
	t.Fatalf("node id %d not found", id)
	return ""
}

func (c *testCluster) stopNode(t *testing.T, index int) {
	t.Helper()
	if index < 0 || index >= len(c.nodes) || c.nodes[index] == nil {
		return
	}
	c.nodes[index].Stop()
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	if err := c.servers[index].Shutdown(ctx); err != nil {
		t.Logf("shutdown node %d: %v", c.peers[index].ID, err)
	}
	c.nodes[index] = nil
	c.servers[index] = nil
}

func (c *testCluster) postJSON(t *testing.T, addr, path string, body any, wantStatus int, out any) {
	t.Helper()
	data, err := json.Marshal(body)
	if err != nil {
		t.Fatalf("marshal request failed: %v", err)
	}
	url := "http://" + addr + path
	resp, err := c.client.Post(url, "application/json", bytes.NewReader(data))
	if err != nil {
		t.Fatalf("post %s failed: %v", url, err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != wantStatus {
		t.Fatalf("post %s status=%d want=%d", url, resp.StatusCode, wantStatus)
	}
	if out != nil {
		if err := json.NewDecoder(resp.Body).Decode(out); err != nil {
			t.Fatalf("decode response from %s failed: %v", url, err)
		}
	}
}

func (c *testCluster) getJSON(t *testing.T, addr, path string, wantStatus int, out any) {
	t.Helper()
	url := "http://" + addr + path
	resp, err := c.client.Get(url)
	if err != nil {
		t.Fatalf("get %s failed: %v", url, err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != wantStatus {
		t.Fatalf("get %s status=%d want=%d", url, resp.StatusCode, wantStatus)
	}
	if out != nil {
		if err := json.NewDecoder(resp.Body).Decode(out); err != nil {
			t.Fatalf("decode response from %s failed: %v", url, err)
		}
	}
}

func (c *testCluster) getJSONErr(addr, path string, out any) error {
	url := "http://" + addr + path
	resp, err := c.client.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("status %d", resp.StatusCode)
	}
	return json.NewDecoder(resp.Body).Decode(out)
}

func freeAddr(t *testing.T) string {
	t.Helper()
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("allocate port failed: %v", err)
	}
	defer listener.Close()
	return listener.Addr().String()
}
