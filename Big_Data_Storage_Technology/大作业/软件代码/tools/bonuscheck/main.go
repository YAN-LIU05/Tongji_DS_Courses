package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"html"
	"io"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"time"
)

type peer struct {
	ID       int    `json:"id"`
	APIAddr  string `json:"api_addr"`
	RaftAddr string `json:"raft_addr"`
	DataDir  string `json:"data_dir"`
}

type clusterConfig struct {
	Nodes []peer `json:"nodes"`
}

type statusResponse struct {
	ID            int    `json:"id"`
	Role          string `json:"role"`
	Term          int    `json:"term"`
	LeaderID      int    `json:"leader_id"`
	LeaderAddr    string `json:"leader_addr"`
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

type clusterResponse struct {
	Peers  []peer         `json:"peers"`
	Status statusResponse `json:"status"`
}

type clientErrorResponse struct {
	Error      string `json:"error"`
	LeaderID   int    `json:"leader_id"`
	LeaderAddr string `json:"leader_addr"`
}

type persistentState struct {
	CurrentTerm   int               `json:"current_term"`
	VotedFor      int               `json:"voted_for"`
	CommitIndex   int               `json:"commit_index"`
	LastApplied   int               `json:"last_applied"`
	SnapshotIndex int               `json:"snapshot_index"`
	SnapshotTerm  int               `json:"snapshot_term"`
	Snapshot      map[string]string `json:"snapshot"`
	Peers         []peer            `json:"peers"`
}

type runReport struct {
	GeneratedAt      string            `json:"generated_at"`
	RepoRoot         string            `json:"repo_root"`
	OutputDir        string            `json:"output_dir"`
	GoCommand        string            `json:"go_command"`
	NodeBinary       string            `json:"node_binary"`
	Pass             bool              `json:"pass"`
	Core             coreResult        `json:"core"`
	FiveNode         fiveNodeResult    `json:"five_node"`
	SnapshotLeaseAdd snapshotLeaseAdd  `json:"snapshot_lease_dynamic_add"`
	Artifacts        map[string]string `json:"artifacts"`
	Warnings         []string          `json:"warnings,omitempty"`
}

type coreResult struct {
	Pass              bool                `json:"pass"`
	InitialLeaderID   int                 `json:"initial_leader_id"`
	InitialStatuses   []statusResponse    `json:"initial_statuses"`
	BasicPut          putResponse         `json:"basic_put"`
	BasicGet          getResponse         `json:"basic_get"`
	BasicDelete       putResponse         `json:"basic_delete"`
	FollowerRedirect  clientErrorResponse `json:"follower_redirect"`
	FollowerDownNode  int                 `json:"follower_down_node"`
	FollowerDownPut   putResponse         `json:"follower_down_put"`
	FailoverOldLeader int                 `json:"failover_old_leader"`
	FailoverNewLeader int                 `json:"failover_new_leader"`
	FailoverPut       putResponse         `json:"failover_put"`
	FailoverGet       getResponse         `json:"failover_get"`
	FinalStatuses     []statusResponse    `json:"final_statuses"`
	Notes             []string            `json:"notes"`
}

type fiveNodeResult struct {
	Pass     bool             `json:"pass"`
	LeaderID int              `json:"leader_id"`
	Statuses []statusResponse `json:"statuses"`
	Notes    []string         `json:"notes"`
}

type snapshotLeaseAdd struct {
	Pass                 bool             `json:"pass"`
	InitialLeaderID      int              `json:"initial_leader_id"`
	LeaseRead            getResponse      `json:"lease_read"`
	SnapshotLeaderStatus statusResponse   `json:"snapshot_leader_status"`
	SnapshotStateFile    string           `json:"snapshot_state_file"`
	SnapshotPersistent   persistentState  `json:"snapshot_persistent_state"`
	ClusterAfterAdd      clusterResponse  `json:"cluster_after_add"`
	DynamicPut           putResponse      `json:"dynamic_put"`
	StatusesAfterAdd     []statusResponse `json:"statuses_after_add"`
	Node4Status          statusResponse   `json:"node4_status"`
	Notes                []string         `json:"notes"`
}

type runningCluster struct {
	ctx        context.Context
	cancel     context.CancelFunc
	nodeBin    string
	configPath string
	logDir     string
	ids        []int
	cmds       []*exec.Cmd
	logs       []*os.File
}

func main() {
	var outBase string
	var goCommand string
	var keepBinary bool
	flag.StringVar(&outBase, "out", filepath.Join("report", "bonus_artifacts"), "directory for generated reports")
	flag.StringVar(&goCommand, "go", "", "go command path; defaults to GOEXE, PATH go, or D:\\Go\\bin\\go.exe on Windows")
	flag.BoolVar(&keepBinary, "keep-binary", false, "keep the temporary node binary after the run")
	flag.Parse()

	if err := run(outBase, goCommand, keepBinary); err != nil {
		fmt.Fprintf(os.Stderr, "bonuscheck failed: %v\n", err)
		os.Exit(1)
	}
}

func run(outBase, goCommand string, keepBinary bool) error {
	repoRoot, err := findRepoRoot()
	if err != nil {
		return err
	}
	runID := time.Now().Format("20060102_150405")
	outDir := filepath.Join(repoRoot, outBase, runID)
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		return fmt.Errorf("create output dir: %w", err)
	}

	goExe, err := resolveGo(goCommand)
	if err != nil {
		return err
	}
	nodeBin := filepath.Join(outDir, "raft-kv-node")
	if runtime.GOOS == "windows" {
		nodeBin += ".exe"
	}
	if err := buildNodeBinary(repoRoot, goExe, nodeBin); err != nil {
		return err
	}
	if !keepBinary {
		defer os.Remove(nodeBin)
	}

	client := &http.Client{Timeout: 900 * time.Millisecond}
	report := runReport{
		GeneratedAt: time.Now().Format(time.RFC3339),
		RepoRoot:    repoRoot,
		OutputDir:   outDir,
		GoCommand:   goExe,
		NodeBinary:  nodeBin,
		Artifacts:   make(map[string]string),
	}

	fmt.Println("== bonuscheck: core raft kv functions ==")
	core, err := runCoreScenario(client, nodeBin, outDir)
	if err != nil {
		report.Core.Notes = append(report.Core.Notes, err.Error())
		writeFailureReport(outDir, &report)
		return err
	}
	report.Core = core

	fmt.Println("== bonuscheck: five-node status ==")
	fiveNode, err := runFiveNodeScenario(client, nodeBin, outDir)
	if err != nil {
		report.FiveNode.Notes = append(report.FiveNode.Notes, err.Error())
		writeFailureReport(outDir, &report)
		return err
	}
	report.FiveNode = fiveNode

	fmt.Println("== bonuscheck: snapshot, lease read, dynamic add ==")
	snapshotLease, err := runSnapshotLeaseAddScenario(client, nodeBin, outDir)
	if err != nil {
		report.SnapshotLeaseAdd.Notes = append(report.SnapshotLeaseAdd.Notes, err.Error())
		writeFailureReport(outDir, &report)
		return err
	}
	report.SnapshotLeaseAdd = snapshotLease
	report.Pass = report.Core.Pass && report.FiveNode.Pass && report.SnapshotLeaseAdd.Pass

	jsonPath := filepath.Join(outDir, "bonus_test_results.json")
	if err := writeJSONFile(jsonPath, report); err != nil {
		return err
	}
	report.Artifacts["json"] = jsonPath

	mdPath := filepath.Join(outDir, "bonus_summary.md")
	if err := writeMarkdown(mdPath, report); err != nil {
		return err
	}
	report.Artifacts["markdown"] = mdPath

	svgPath := filepath.Join(outDir, "bonus_metrics.svg")
	if err := writeSVG(svgPath, report); err != nil {
		return err
	}
	report.Artifacts["svg"] = svgPath

	if err := writeJSONFile(jsonPath, report); err != nil {
		return err
	}

	fmt.Printf("PASS=%v\n", report.Pass)
	fmt.Printf("JSON: %s\n", jsonPath)
	fmt.Printf("Summary: %s\n", mdPath)
	fmt.Printf("Chart: %s\n", svgPath)
	if !report.Pass {
		return errors.New("one or more bonus checks failed")
	}
	return nil
}

func runCoreScenario(client *http.Client, nodeBin, outDir string) (coreResult, error) {
	scenarioDir := filepath.Join(outDir, "core")
	peers, err := makePeers(3, filepath.Join(scenarioDir, "data"))
	if err != nil {
		return coreResult{}, err
	}
	configPath := filepath.Join(scenarioDir, "cluster3.json")
	if err := writeConfig(configPath, peers); err != nil {
		return coreResult{}, err
	}

	ctx, cancel := context.WithCancel(context.Background())
	cluster, err := startCluster(ctx, nodeBin, configPath, []int{1, 2, 3}, filepath.Join(scenarioDir, "logs"))
	if err != nil {
		cancel()
		return coreResult{}, err
	}
	defer cluster.stop()

	leader, statuses, err := waitForOneLeader(client, peers, 12*time.Second)
	if err != nil {
		return coreResult{}, err
	}
	sortStatuses(statuses)
	result := coreResult{
		InitialLeaderID: leader.ID,
		InitialStatuses: statuses,
		Notes: []string{
			"three-node cluster elected exactly one leader",
		},
	}

	var follower statusResponse
	for _, status := range statuses {
		if status.ID != leader.ID {
			follower = status
			break
		}
	}
	followerPeer, ok := peerByID(peers, follower.ID)
	if !ok {
		return coreResult{}, fmt.Errorf("follower peer %d not found", follower.ID)
	}
	statusCode, redirectBody, err := postJSONRaw(client, followerPeer.APIAddr, "/kv/put", map[string]string{
		"key":   "wrong_node",
		"value": "x",
	})
	if err != nil {
		return coreResult{}, err
	}
	if statusCode != http.StatusConflict {
		return coreResult{}, fmt.Errorf("expected follower write HTTP 409, got %d body=%s", statusCode, strings.TrimSpace(string(redirectBody)))
	}
	var redirect clientErrorResponse
	if err := json.Unmarshal(redirectBody, &redirect); err != nil {
		return coreResult{}, err
	}
	if redirect.Error != "not leader" || redirect.LeaderID != leader.ID || redirect.LeaderAddr == "" {
		return coreResult{}, fmt.Errorf("unexpected follower redirect response: %+v", redirect)
	}
	result.FollowerRedirect = redirect
	result.Notes = append(result.Notes, "follower write returned leader redirect information")

	leaderAddr := leader.LeaderAddr
	put, leaderAddr, err := postToLeader(client, peers, leaderAddr, "/kv/put", map[string]string{
		"key":   "basic_name",
		"value": "raft",
	})
	if err != nil {
		return coreResult{}, err
	}
	result.BasicPut = put

	var basicGet getResponse
	if err := getJSON(client, leaderAddr, "/kv/get?key=basic_name", http.StatusOK, &basicGet); err != nil {
		return coreResult{}, err
	}
	if !basicGet.Found || basicGet.Value != "raft" {
		return coreResult{}, fmt.Errorf("unexpected basic get response: %+v", basicGet)
	}
	result.BasicGet = basicGet

	del, leaderAddr, err := postToLeader(client, peers, leaderAddr, "/kv/delete", map[string]string{"key": "basic_name"})
	if err != nil {
		return coreResult{}, err
	}
	result.BasicDelete = del
	if err := getJSON(client, leaderAddr, "/kv/get?key=basic_name", http.StatusNotFound, nil); err != nil {
		return coreResult{}, err
	}
	result.Notes = append(result.Notes, "Put/Get/Delete and deleted-key 404 passed")

	result.FollowerDownNode = follower.ID
	if err := cluster.stopID(follower.ID); err != nil {
		return coreResult{}, err
	}
	followerDownPut, leaderAddr, err := postToLeader(client, peers, leaderAddr, "/kv/put", map[string]string{
		"key":   "after_follower_down",
		"value": "ok",
	})
	if err != nil {
		return coreResult{}, err
	}
	result.FollowerDownPut = followerDownPut
	result.Notes = append(result.Notes, "write succeeded after one follower was stopped")

	if err := cluster.startID(follower.ID); err != nil {
		return coreResult{}, err
	}
	if _, err := waitForAllStatuses(client, peers, 8*time.Second, func(statuses []statusResponse) bool {
		return len(statuses) == 3
	}); err != nil {
		return coreResult{}, err
	}

	currentLeader, _, err := waitForOneLeader(client, peers, 8*time.Second)
	if err != nil {
		return coreResult{}, err
	}
	result.FailoverOldLeader = currentLeader.ID
	if err := cluster.stopID(currentLeader.ID); err != nil {
		return coreResult{}, err
	}
	newLeader, finalStatuses, err := waitForOneLeader(client, peers, 12*time.Second)
	if err != nil {
		return coreResult{}, err
	}
	if newLeader.ID == currentLeader.ID {
		return coreResult{}, fmt.Errorf("expected new leader after stopping node %d", currentLeader.ID)
	}
	result.FailoverNewLeader = newLeader.ID
	failoverPut, newLeaderAddr, err := postToLeader(client, peers, newLeader.LeaderAddr, "/kv/put", map[string]string{
		"key":   "after_leader_down",
		"value": "ok",
	})
	if err != nil {
		return coreResult{}, err
	}
	result.FailoverPut = failoverPut
	var failoverGet getResponse
	if err := getJSON(client, newLeaderAddr, "/kv/get?key=after_leader_down", http.StatusOK, &failoverGet); err != nil {
		return coreResult{}, err
	}
	if !failoverGet.Found || failoverGet.Value != "ok" {
		return coreResult{}, fmt.Errorf("unexpected failover get response: %+v", failoverGet)
	}
	result.FailoverGet = failoverGet
	finalStatuses, err = waitForAllStatuses(client, peers, 6*time.Second, func(statuses []statusResponse) bool {
		if len(statuses) != 2 {
			return false
		}
		for _, status := range statuses {
			if status.CommitIndex < failoverPut.Index {
				return false
			}
		}
		return true
	})
	if err != nil {
		return coreResult{}, err
	}
	sortStatuses(finalStatuses)
	result.FinalStatuses = finalStatuses
	result.Notes = append(result.Notes, "new leader served Put/Get after old leader stopped")
	result.Pass = true

	if err := writeJSONFile(filepath.Join(scenarioDir, "core_functions.json"), result); err != nil {
		return coreResult{}, err
	}
	return result, nil
}

func runFiveNodeScenario(client *http.Client, nodeBin, outDir string) (fiveNodeResult, error) {
	scenarioDir := filepath.Join(outDir, "five_node")
	peers, err := makePeers(5, filepath.Join(scenarioDir, "data"))
	if err != nil {
		return fiveNodeResult{}, err
	}
	configPath := filepath.Join(scenarioDir, "cluster5.json")
	if err := writeConfig(configPath, peers); err != nil {
		return fiveNodeResult{}, err
	}

	ctx, cancel := context.WithCancel(context.Background())
	cluster, err := startCluster(ctx, nodeBin, configPath, []int{1, 2, 3, 4, 5}, filepath.Join(scenarioDir, "logs"))
	if err != nil {
		cancel()
		return fiveNodeResult{}, err
	}
	defer cluster.stop()

	leader, statuses, err := waitForOneLeader(client, peers, 12*time.Second)
	if err != nil {
		return fiveNodeResult{}, err
	}
	statuses, err = waitForAllStatuses(client, peers, 5*time.Second, func(statuses []statusResponse) bool {
		if len(statuses) != 5 {
			return false
		}
		leaders := 0
		for _, status := range statuses {
			if status.ClusterSize != 5 {
				return false
			}
			if status.Role == "Leader" {
				leaders++
			}
		}
		return leaders == 1
	})
	if err != nil {
		return fiveNodeResult{}, err
	}
	sortStatuses(statuses)
	result := fiveNodeResult{
		Pass:     true,
		LeaderID: leader.ID,
		Statuses: statuses,
		Notes: []string{
			"five nodes responded to /status",
			"exactly one node is Leader",
			"each node reports cluster_size=5",
		},
	}
	if err := writeJSONFile(filepath.Join(scenarioDir, "five_node_status.json"), result); err != nil {
		return fiveNodeResult{}, err
	}
	return result, nil
}

func runSnapshotLeaseAddScenario(client *http.Client, nodeBin, outDir string) (snapshotLeaseAdd, error) {
	scenarioDir := filepath.Join(outDir, "snapshot_lease_dynamic_add")
	allPeers, err := makePeers(4, filepath.Join(scenarioDir, "data"))
	if err != nil {
		return snapshotLeaseAdd{}, err
	}
	threePeers := append([]peer(nil), allPeers[:3]...)
	config3Path := filepath.Join(scenarioDir, "cluster3.json")
	config4Path := filepath.Join(scenarioDir, "cluster4.json")
	if err := writeConfig(config3Path, threePeers); err != nil {
		return snapshotLeaseAdd{}, err
	}
	if err := writeConfig(config4Path, allPeers); err != nil {
		return snapshotLeaseAdd{}, err
	}

	ctx, cancel := context.WithCancel(context.Background())
	cluster, err := startCluster(ctx, nodeBin, config3Path, []int{1, 2, 3}, filepath.Join(scenarioDir, "logs"))
	if err != nil {
		cancel()
		return snapshotLeaseAdd{}, err
	}
	defer cluster.stop()

	leader, _, err := waitForOneLeader(client, threePeers, 12*time.Second)
	if err != nil {
		return snapshotLeaseAdd{}, err
	}
	result := snapshotLeaseAdd{InitialLeaderID: leader.ID}

	leasePut, leaderAddr, err := postToLeader(client, threePeers, leader.LeaderAddr, "/kv/put", map[string]string{
		"key":   "lease_demo",
		"value": "read-ok",
	})
	if err != nil {
		return snapshotLeaseAdd{}, err
	}
	_ = leasePut
	var leaseRead getResponse
	if err := getJSON(client, leaderAddr, "/kv/get?key=lease_demo", http.StatusOK, &leaseRead); err != nil {
		return snapshotLeaseAdd{}, err
	}
	if !leaseRead.Found || leaseRead.Value != "read-ok" || leaseRead.ReadMode != "lease_read" {
		return snapshotLeaseAdd{}, fmt.Errorf("unexpected lease read response: %+v", leaseRead)
	}
	result.LeaseRead = leaseRead
	result.Notes = append(result.Notes, "lease read returned read_mode=lease_read")

	for i := 1; i <= 10; i++ {
		body := map[string]string{
			"key":   fmt.Sprintf("snap_%02d", i),
			"value": fmt.Sprintf("v%02d", i),
		}
		var put putResponse
		put, leaderAddr, err = postToLeader(client, threePeers, leaderAddr, "/kv/put", body)
		if err != nil {
			return snapshotLeaseAdd{}, fmt.Errorf("snapshot put %d failed: %w", i, err)
		}
		if !put.OK {
			return snapshotLeaseAdd{}, fmt.Errorf("snapshot put %d returned ok=false", i)
		}
	}
	snapshotStatus, err := waitForStatus(client, leaderAddr, 8*time.Second, func(status statusResponse) bool {
		return status.SnapshotIndex > 0 && status.LogLen < status.LastLogIndex
	})
	if err != nil {
		return snapshotLeaseAdd{}, err
	}
	result.SnapshotLeaderStatus = snapshotStatus
	result.Notes = append(result.Notes, "snapshot_index advanced and log_len shrank after compaction")

	leaderPeer, ok := peerByID(allPeers, snapshotStatus.ID)
	if !ok {
		return snapshotLeaseAdd{}, fmt.Errorf("leader peer %d not found", snapshotStatus.ID)
	}
	statePath := filepath.Join(leaderPeer.DataDir, "state.json")
	var persisted persistentState
	if err := readJSONFile(statePath, &persisted); err != nil {
		return snapshotLeaseAdd{}, fmt.Errorf("read persistent state: %w", err)
	}
	if persisted.SnapshotIndex <= 0 || len(persisted.Snapshot) == 0 {
		return snapshotLeaseAdd{}, fmt.Errorf("persistent snapshot fields not populated: %+v", persisted)
	}
	result.SnapshotStateFile = statePath
	result.SnapshotPersistent = persisted

	addBody := allPeers[3]
	var add putResponse
	add, leaderAddr, err = postToLeader(client, threePeers, leaderAddr, "/cluster/add", addBody)
	if err != nil {
		return snapshotLeaseAdd{}, fmt.Errorf("cluster add failed: %w", err)
	}
	if !add.OK {
		return snapshotLeaseAdd{}, fmt.Errorf("cluster add returned ok=false")
	}

	cluster4, err := startCluster(ctx, nodeBin, config4Path, []int{4}, filepath.Join(scenarioDir, "logs"))
	if err != nil {
		return snapshotLeaseAdd{}, err
	}
	oldCancel := cluster.cancel
	cluster.cancel = func() {
		oldCancel()
		cluster4.cancel()
	}
	cluster.cmds = append(cluster.cmds, cluster4.cmds...)
	cluster.logs = append(cluster.logs, cluster4.logs...)

	leader4, _, err := waitForOneLeader(client, allPeers, 12*time.Second)
	if err != nil {
		return snapshotLeaseAdd{}, err
	}
	leaderAddr = leader4.LeaderAddr

	var clusterState clusterResponse
	if err := getJSON(client, leaderAddr, "/cluster", http.StatusOK, &clusterState); err != nil {
		return snapshotLeaseAdd{}, err
	}
	if len(clusterState.Peers) != 4 {
		return snapshotLeaseAdd{}, fmt.Errorf("expected 4 peers after add, got %d", len(clusterState.Peers))
	}
	result.ClusterAfterAdd = clusterState
	result.Notes = append(result.Notes, "cluster/add committed and /cluster shows four peers")

	dynamicPut, leaderAddr, err := postToLeader(client, allPeers, leaderAddr, "/kv/put", map[string]string{
		"key":   "dynamic_node4",
		"value": "joined",
	})
	if err != nil {
		return snapshotLeaseAdd{}, fmt.Errorf("dynamic put failed: %w", err)
	}
	result.DynamicPut = dynamicPut

	node4Status, err := waitForStatus(client, allPeers[3].APIAddr, 10*time.Second, func(status statusResponse) bool {
		return status.ClusterSize == 4 && status.CommitIndex >= dynamicPut.Index
	})
	if err != nil {
		return snapshotLeaseAdd{}, err
	}
	result.Node4Status = node4Status
	statusesAfterAdd, err := waitForAllStatuses(client, allPeers, 5*time.Second, func(statuses []statusResponse) bool {
		if len(statuses) != 4 {
			return false
		}
		for _, status := range statuses {
			if status.ClusterSize != 4 {
				return false
			}
		}
		return true
	})
	if err != nil {
		return snapshotLeaseAdd{}, err
	}
	sortStatuses(statusesAfterAdd)
	result.StatusesAfterAdd = statusesAfterAdd
	result.Notes = append(result.Notes, "node4 caught up to the dynamic write commit index")
	result.Pass = true

	if err := writeJSONFile(filepath.Join(scenarioDir, "snapshot_lease_dynamic_add.json"), result); err != nil {
		return snapshotLeaseAdd{}, err
	}
	return result, nil
}

func buildNodeBinary(repoRoot, goExe, outPath string) error {
	fmt.Printf("building node binary with %s\n", goExe)
	if err := os.MkdirAll(filepath.Dir(outPath), 0o755); err != nil {
		return err
	}
	cmd := exec.Command(goExe, "build", "-buildvcs=false", "-o", outPath, "./cmd/node")
	cmd.Dir = repoRoot
	cmd.Env = goEnv(repoRoot)
	var output bytes.Buffer
	cmd.Stdout = &output
	cmd.Stderr = &output
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("go build failed: %w\n%s", err, output.String())
	}
	return nil
}

func startCluster(ctx context.Context, nodeBin, configPath string, ids []int, logDir string) (*runningCluster, error) {
	if err := os.MkdirAll(logDir, 0o755); err != nil {
		return nil, err
	}
	clusterCtx, cancel := context.WithCancel(ctx)
	cluster := &runningCluster{
		ctx:        clusterCtx,
		cancel:     cancel,
		nodeBin:    nodeBin,
		configPath: configPath,
		logDir:     logDir,
	}
	for _, id := range ids {
		if err := cluster.startID(id); err != nil {
			cancel()
			cluster.stop()
			return nil, err
		}
	}
	return cluster, nil
}

func (c *runningCluster) startID(id int) error {
	logPath := filepath.Join(c.logDir, fmt.Sprintf("node%d_%d.log", id, time.Now().UnixNano()))
	logFile, err := os.Create(logPath)
	if err != nil {
		return err
	}
	cmd := exec.CommandContext(c.ctx, c.nodeBin, fmt.Sprintf("--id=%d", id), "--config="+c.configPath)
	cmd.Stdout = logFile
	cmd.Stderr = logFile
	if err := cmd.Start(); err != nil {
		logFile.Close()
		return fmt.Errorf("start node %d: %w", id, err)
	}
	c.ids = append(c.ids, id)
	c.cmds = append(c.cmds, cmd)
	c.logs = append(c.logs, logFile)
	return nil
}

func (c *runningCluster) stopID(id int) error {
	for i, nodeID := range c.ids {
		if nodeID != id || c.cmds[i] == nil {
			continue
		}
		if err := stopCommand(c.cmds[i]); err != nil {
			return err
		}
		c.cmds[i] = nil
		if c.logs[i] != nil {
			_ = c.logs[i].Close()
			c.logs[i] = nil
		}
		return nil
	}
	return fmt.Errorf("node %d is not running", id)
}

func (c *runningCluster) stop() {
	if c == nil {
		return
	}
	if c.cancel != nil {
		c.cancel()
	}
	for _, cmd := range c.cmds {
		_ = stopCommand(cmd)
	}
	c.closeLogs()
}

func stopCommand(cmd *exec.Cmd) error {
	if cmd == nil || cmd.Process == nil {
		return nil
	}
	done := make(chan error, 1)
	go func() {
		done <- cmd.Wait()
	}()
	select {
	case err := <-done:
		return err
	case <-time.After(2 * time.Second):
		if err := cmd.Process.Kill(); err != nil {
			return err
		}
		<-done
		return nil
	}
}

func (c *runningCluster) closeLogs() {
	for _, logFile := range c.logs {
		if logFile != nil {
			_ = logFile.Close()
		}
	}
	c.logs = nil
}

func makePeers(n int, dataRoot string) ([]peer, error) {
	peers := make([]peer, 0, n)
	for i := 1; i <= n; i++ {
		apiAddr, err := freeAddr()
		if err != nil {
			return nil, err
		}
		raftAddr, err := freeAddr()
		if err != nil {
			return nil, err
		}
		peers = append(peers, peer{
			ID:       i,
			APIAddr:  apiAddr,
			RaftAddr: raftAddr,
			DataDir:  filepath.Join(dataRoot, fmt.Sprintf("node%d", i)),
		})
	}
	return peers, nil
}

func freeAddr() (string, error) {
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return "", err
	}
	defer listener.Close()
	return listener.Addr().String(), nil
}

func writeConfig(path string, peers []peer) error {
	return writeJSONFile(path, clusterConfig{Nodes: peers})
}

func waitForOneLeader(client *http.Client, peers []peer, timeout time.Duration) (statusResponse, []statusResponse, error) {
	statuses, err := waitForAllStatuses(client, peers, timeout, func(statuses []statusResponse) bool {
		leaders := 0
		for _, status := range statuses {
			if status.Role == "Leader" {
				leaders++
			}
		}
		return leaders == 1
	})
	if err != nil {
		return statusResponse{}, nil, err
	}
	for _, status := range statuses {
		if status.Role == "Leader" {
			return status, statuses, nil
		}
	}
	return statusResponse{}, statuses, errors.New("no leader found")
}

func waitForAllStatuses(client *http.Client, peers []peer, timeout time.Duration, ok func([]statusResponse) bool) ([]statusResponse, error) {
	deadline := time.Now().Add(timeout)
	var last []statusResponse
	for time.Now().Before(deadline) {
		statuses := make([]statusResponse, 0, len(peers))
		for _, peer := range peers {
			var status statusResponse
			if err := getJSON(client, peer.APIAddr, "/status", http.StatusOK, &status); err != nil {
				continue
			}
			statuses = append(statuses, status)
		}
		sortStatuses(statuses)
		last = statuses
		if ok(statuses) {
			return statuses, nil
		}
		time.Sleep(120 * time.Millisecond)
	}
	return nil, fmt.Errorf("timed out waiting for statuses, last=%+v", last)
}

func waitForStatus(client *http.Client, addr string, timeout time.Duration, ok func(statusResponse) bool) (statusResponse, error) {
	deadline := time.Now().Add(timeout)
	var last statusResponse
	for time.Now().Before(deadline) {
		if err := getJSON(client, addr, "/status", http.StatusOK, &last); err == nil && ok(last) {
			return last, nil
		}
		time.Sleep(120 * time.Millisecond)
	}
	return statusResponse{}, fmt.Errorf("timed out waiting for status on %s, last=%+v", addr, last)
}

func postToLeader(client *http.Client, peers []peer, leaderAddr, path string, body any) (putResponse, string, error) {
	addr := leaderAddr
	if addr == "" {
		leader, _, err := waitForOneLeader(client, peers, 6*time.Second)
		if err != nil {
			return putResponse{}, "", err
		}
		addr = leader.LeaderAddr
	}
	for attempt := 0; attempt < 5; attempt++ {
		var out putResponse
		statusCode, responseBody, err := postJSONRaw(client, addr, path, body)
		if err != nil {
			leader, _, leaderErr := waitForOneLeader(client, peers, 4*time.Second)
			if leaderErr != nil {
				return putResponse{}, "", fmt.Errorf("%w; leader retry failed: %v", err, leaderErr)
			}
			addr = leader.LeaderAddr
			continue
		}
		if statusCode == http.StatusOK {
			if err := json.Unmarshal(responseBody, &out); err != nil {
				return putResponse{}, addr, err
			}
			return out, addr, nil
		}
		var redirect struct {
			Error      string `json:"error"`
			LeaderAddr string `json:"leader_addr"`
		}
		_ = json.Unmarshal(responseBody, &redirect)
		if statusCode == http.StatusConflict && redirect.LeaderAddr != "" {
			addr = redirect.LeaderAddr
			time.Sleep(100 * time.Millisecond)
			continue
		}
		return putResponse{}, addr, fmt.Errorf("post %s%s status=%d body=%s", addr, path, statusCode, strings.TrimSpace(string(responseBody)))
	}
	return putResponse{}, addr, fmt.Errorf("post %s%s exhausted leader retries", addr, path)
}

func getJSON(client *http.Client, addr, path string, wantStatus int, out any) error {
	url := "http://" + addr + path
	resp, err := client.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	if resp.StatusCode != wantStatus {
		return fmt.Errorf("get %s status=%d want=%d body=%s", url, resp.StatusCode, wantStatus, strings.TrimSpace(string(body)))
	}
	if out == nil {
		return nil
	}
	if err := json.Unmarshal(body, out); err != nil {
		return fmt.Errorf("decode %s: %w", url, err)
	}
	return nil
}

func postJSONRaw(client *http.Client, addr, path string, body any) (int, []byte, error) {
	data, err := json.Marshal(body)
	if err != nil {
		return 0, nil, err
	}
	url := "http://" + addr + path
	resp, err := client.Post(url, "application/json", bytes.NewReader(data))
	if err != nil {
		return 0, nil, err
	}
	defer resp.Body.Close()
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return 0, nil, err
	}
	return resp.StatusCode, responseBody, nil
}

func writeMarkdown(path string, report runReport) error {
	var b strings.Builder
	fmt.Fprintf(&b, "# Raft KV Full Feature Auto Test\n\n")
	fmt.Fprintf(&b, "- Generated: `%s`\n", report.GeneratedAt)
	fmt.Fprintf(&b, "- Pass: `%v`\n", report.Pass)
	fmt.Fprintf(&b, "- Output directory: `%s`\n\n", report.OutputDir)

	fmt.Fprintf(&b, "## Core functions\n\n")
	fmt.Fprintf(&b, "- Pass: `%v`\n", report.Core.Pass)
	fmt.Fprintf(&b, "- Initial leader: `node%d`\n", report.Core.InitialLeaderID)
	fmt.Fprintf(&b, "- Put/Get/Delete: put index `%d`, get value `%s`, delete index `%d`\n",
		report.Core.BasicPut.Index, report.Core.BasicGet.Value, report.Core.BasicDelete.Index)
	fmt.Fprintf(&b, "- Follower redirect: `%s`, leader `node%d`\n",
		report.Core.FollowerRedirect.Error, report.Core.FollowerRedirect.LeaderID)
	fmt.Fprintf(&b, "- Follower down: stopped `node%d`, write index `%d`\n",
		report.Core.FollowerDownNode, report.Core.FollowerDownPut.Index)
	fmt.Fprintf(&b, "- Leader failover: `node%d` -> `node%d`, get value `%s`\n\n",
		report.Core.FailoverOldLeader, report.Core.FailoverNewLeader, report.Core.FailoverGet.Value)
	fmt.Fprintf(&b, "| node | role | term | leader | commit | applied | last_log | log_len | snapshot | cluster |\n")
	fmt.Fprintf(&b, "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
	for _, status := range report.Core.FinalStatuses {
		fmt.Fprintf(&b, "| %d | %s | %d | %d | %d | %d | %d | %d | %d | %d |\n",
			status.ID, status.Role, status.Term, status.LeaderID, status.CommitIndex,
			status.LastApplied, status.LastLogIndex, status.LogLen, status.SnapshotIndex, status.ClusterSize)
	}

	fmt.Fprintf(&b, "## Five-node status\n\n")
	fmt.Fprintf(&b, "- Pass: `%v`\n", report.FiveNode.Pass)
	fmt.Fprintf(&b, "- Leader: `node%d`\n\n", report.FiveNode.LeaderID)
	fmt.Fprintf(&b, "| node | role | term | leader | commit | applied | last_log | log_len | snapshot | cluster |\n")
	fmt.Fprintf(&b, "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
	for _, status := range report.FiveNode.Statuses {
		fmt.Fprintf(&b, "| %d | %s | %d | %d | %d | %d | %d | %d | %d | %d |\n",
			status.ID, status.Role, status.Term, status.LeaderID, status.CommitIndex,
			status.LastApplied, status.LastLogIndex, status.LogLen, status.SnapshotIndex, status.ClusterSize)
	}

	fmt.Fprintf(&b, "\n## Snapshot, Lease Read, Dynamic Add\n\n")
	fmt.Fprintf(&b, "- Pass: `%v`\n", report.SnapshotLeaseAdd.Pass)
	fmt.Fprintf(&b, "- Lease read: key `%s`, value `%s`, read mode `%s`\n",
		report.SnapshotLeaseAdd.LeaseRead.Key, report.SnapshotLeaseAdd.LeaseRead.Value, report.SnapshotLeaseAdd.LeaseRead.ReadMode)
	fmt.Fprintf(&b, "- Snapshot: index `%d`, term `%d`, log_len `%d`, state file `%s`\n",
		report.SnapshotLeaseAdd.SnapshotLeaderStatus.SnapshotIndex,
		report.SnapshotLeaseAdd.SnapshotLeaderStatus.SnapshotTerm,
		report.SnapshotLeaseAdd.SnapshotLeaderStatus.LogLen,
		report.SnapshotLeaseAdd.SnapshotStateFile)
	fmt.Fprintf(&b, "- Dynamic add: peers `%d`, node4 commit `%d`, dynamic put index `%d`\n\n",
		len(report.SnapshotLeaseAdd.ClusterAfterAdd.Peers),
		report.SnapshotLeaseAdd.Node4Status.CommitIndex,
		report.SnapshotLeaseAdd.DynamicPut.Index)
	fmt.Fprintf(&b, "| node | role | term | leader | commit | applied | last_log | log_len | snapshot | cluster |\n")
	fmt.Fprintf(&b, "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
	for _, status := range report.SnapshotLeaseAdd.StatusesAfterAdd {
		fmt.Fprintf(&b, "| %d | %s | %d | %d | %d | %d | %d | %d | %d | %d |\n",
			status.ID, status.Role, status.Term, status.LeaderID, status.CommitIndex,
			status.LastApplied, status.LastLogIndex, status.LogLen, status.SnapshotIndex, status.ClusterSize)
	}
	return os.WriteFile(path, []byte(b.String()), 0o644)
}

func writeSVG(path string, report runReport) error {
	const width = 1180
	const height = 990
	var b strings.Builder
	fmt.Fprintf(&b, `<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">`, width, height, width, height)
	fmt.Fprintf(&b, `<rect width="100%%" height="100%%" fill="#f8fafc"/>`)
	fmt.Fprintf(&b, `<text x="40" y="54" font-family="Arial, sans-serif" font-size="26" font-weight="700" fill="#111827">Raft KV Full Feature Auto Test</text>`)
	fmt.Fprintf(&b, `<text x="40" y="82" font-family="Arial, sans-serif" font-size="14" fill="#4b5563">%s | pass=%v</text>`, html.EscapeString(report.GeneratedAt), report.Pass)

	drawPanel(&b, 40, 115, 1100, 170, "Core Raft KV checks")
	drawNodeCards(&b, 70, 165, report.Core.InitialStatuses)
	fmt.Fprintf(&b, `<text x="720" y="168" font-family="Arial, sans-serif" font-size="14" fill="#374151">Put/Get/Delete: value=%s, delete_index=%d</text>`,
		html.EscapeString(report.Core.BasicGet.Value), report.Core.BasicDelete.Index)
	fmt.Fprintf(&b, `<text x="720" y="198" font-family="Arial, sans-serif" font-size="14" fill="#374151">Follower down: node%d stopped, write_index=%d</text>`,
		report.Core.FollowerDownNode, report.Core.FollowerDownPut.Index)
	fmt.Fprintf(&b, `<text x="720" y="228" font-family="Arial, sans-serif" font-size="14" fill="#374151">Leader failover: node%d -> node%d, value=%s</text>`,
		report.Core.FailoverOldLeader, report.Core.FailoverNewLeader, html.EscapeString(report.Core.FailoverGet.Value))

	drawPanel(&b, 40, 315, 1100, 215, "Five-node cluster status")
	drawNodeCards(&b, 70, 365, report.FiveNode.Statuses)

	drawPanel(&b, 40, 560, 520, 200, "Snapshot fields")
	s := report.SnapshotLeaseAdd.SnapshotLeaderStatus
	maxMetric := maxInt(1, s.LastLogIndex, s.CommitIndex, s.LastApplied)
	drawMetricBar(&b, 75, 620, 410, "commit_index", s.CommitIndex, maxMetric, "#2563eb")
	drawMetricBar(&b, 75, 665, 410, "last_applied", s.LastApplied, maxMetric, "#0891b2")
	drawMetricBar(&b, 75, 710, 410, "snapshot_index", s.SnapshotIndex, maxMetric, "#16a34a")
	fmt.Fprintf(&b, `<text x="75" y="748" font-family="Arial, sans-serif" font-size="13" fill="#374151">snapshot_term=%d, log_len=%d, state keys=%d</text>`,
		s.SnapshotTerm, s.LogLen, len(report.SnapshotLeaseAdd.SnapshotPersistent.Snapshot))

	drawPanel(&b, 620, 560, 520, 200, "Lease Read")
	l := report.SnapshotLeaseAdd.LeaseRead
	fmt.Fprintf(&b, `<text x="655" y="628" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#111827">GET %s = %s</text>`,
		html.EscapeString(l.Key), html.EscapeString(l.Value))
	fmt.Fprintf(&b, `<rect x="655" y="658" width="245" height="46" rx="6" fill="#dcfce7" stroke="#86efac"/>`)
	fmt.Fprintf(&b, `<text x="675" y="688" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#166534">read_mode: %s</text>`, html.EscapeString(l.ReadMode))

	drawPanel(&b, 40, 790, 1100, 170, "Dynamic add node")
	drawNodeCards(&b, 70, 840, report.SnapshotLeaseAdd.StatusesAfterAdd)
	fmt.Fprintf(&b, `<text x="70" y="938" font-family="Arial, sans-serif" font-size="14" fill="#374151">/cluster/add peers=%d, dynamic write index=%d, node4 commit=%d</text>`,
		len(report.SnapshotLeaseAdd.ClusterAfterAdd.Peers),
		report.SnapshotLeaseAdd.DynamicPut.Index,
		report.SnapshotLeaseAdd.Node4Status.CommitIndex)

	fmt.Fprintf(&b, `</svg>`)
	return os.WriteFile(path, []byte(b.String()), 0o644)
}

func drawPanel(b *strings.Builder, x, y, w, h int, title string) {
	fmt.Fprintf(b, `<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="#ffffff" stroke="#cbd5e1"/>`, x, y, w, h)
	fmt.Fprintf(b, `<text x="%d" y="%d" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#111827">%s</text>`, x+25, y+36, html.EscapeString(title))
}

func drawNodeCards(b *strings.Builder, x, y int, statuses []statusResponse) {
	for i, status := range statuses {
		cardX := x + i*205
		fill := "#eff6ff"
		stroke := "#93c5fd"
		roleFill := "#dbeafe"
		roleColor := "#1d4ed8"
		if status.Role == "Leader" {
			fill = "#f0fdf4"
			stroke = "#86efac"
			roleFill = "#dcfce7"
			roleColor = "#166534"
		}
		fmt.Fprintf(b, `<rect x="%d" y="%d" width="180" height="88" rx="6" fill="%s" stroke="%s"/>`, cardX, y, fill, stroke)
		fmt.Fprintf(b, `<text x="%d" y="%d" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#111827">node%d</text>`, cardX+15, y+28, status.ID)
		fmt.Fprintf(b, `<rect x="%d" y="%d" width="86" height="24" rx="12" fill="%s"/>`, cardX+80, y+12, roleFill)
		fmt.Fprintf(b, `<text x="%d" y="%d" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="%s">%s</text>`, cardX+94, y+29, roleColor, html.EscapeString(status.Role))
		fmt.Fprintf(b, `<text x="%d" y="%d" font-family="Arial, sans-serif" font-size="12" fill="#374151">commit=%d applied=%d</text>`, cardX+15, y+54, status.CommitIndex, status.LastApplied)
		fmt.Fprintf(b, `<text x="%d" y="%d" font-family="Arial, sans-serif" font-size="12" fill="#374151">snapshot=%d cluster=%d</text>`, cardX+15, y+74, status.SnapshotIndex, status.ClusterSize)
	}
}

func drawMetricBar(b *strings.Builder, x, y, width int, label string, value, maxValue int, color string) {
	barWidth := value * width / maxValue
	if barWidth < 2 && value > 0 {
		barWidth = 2
	}
	fmt.Fprintf(b, `<text x="%d" y="%d" font-family="Arial, sans-serif" font-size="13" fill="#374151">%s</text>`, x, y-8, html.EscapeString(label))
	fmt.Fprintf(b, `<rect x="%d" y="%d" width="%d" height="20" rx="4" fill="#e5e7eb"/>`, x+125, y-23, width)
	fmt.Fprintf(b, `<rect x="%d" y="%d" width="%d" height="20" rx="4" fill="%s"/>`, x+125, y-23, barWidth, color)
	fmt.Fprintf(b, `<text x="%d" y="%d" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#111827">%d</text>`, x+135+barWidth, y-8, value)
}

func writeJSONFile(path string, value any) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	data, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	data = append(data, '\n')
	return os.WriteFile(path, data, 0o644)
}

func readJSONFile(path string, out any) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, out)
}

func writeFailureReport(outDir string, report *runReport) {
	_ = writeJSONFile(filepath.Join(outDir, "bonus_test_results_failed.json"), report)
}

func findRepoRoot() (string, error) {
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "", errors.New("go.mod not found; run from inside the raft-kv repository")
		}
		dir = parent
	}
}

func resolveGo(explicit string) (string, error) {
	candidates := []string{}
	if explicit != "" {
		candidates = append(candidates, explicit)
	}
	if envGo := os.Getenv("GOEXE"); envGo != "" {
		candidates = append(candidates, envGo)
	}
	candidates = append(candidates, "go")
	if runtime.GOOS == "windows" {
		candidates = append(candidates, `D:\Go\bin\go.exe`)
	}
	for _, candidate := range candidates {
		if path, err := exec.LookPath(candidate); err == nil {
			return path, nil
		}
		if filepath.IsAbs(candidate) {
			if _, err := os.Stat(candidate); err == nil {
				return candidate, nil
			}
		}
	}
	return "", errors.New("go command not found; pass -go or set GOEXE")
}

func goEnv(repoRoot string) []string {
	env := os.Environ()
	if os.Getenv("GOCACHE") == "" {
		cacheDir := filepath.Join(repoRoot, ".gocache")
		_ = os.MkdirAll(cacheDir, 0o755)
		env = append(env, "GOCACHE="+cacheDir)
	}
	return env
}

func peerByID(peers []peer, id int) (peer, bool) {
	for _, peer := range peers {
		if peer.ID == id {
			return peer, true
		}
	}
	return peer{}, false
}

func sortStatuses(statuses []statusResponse) {
	sort.Slice(statuses, func(i, j int) bool {
		return statuses[i].ID < statuses[j].ID
	})
}

func maxInt(values ...int) int {
	maxValue := values[0]
	for _, value := range values[1:] {
		if value > maxValue {
			maxValue = value
		}
	}
	return maxValue
}
