package raft

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"sort"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	"raft-kv/kv"
)

var (
	ErrNotLeader     = errors.New("not leader")
	ErrCommitTimeout = errors.New("commit timeout")
)

const (
	defaultSnapshotThreshold = 8
	defaultLeaderLease       = 500 * time.Millisecond
	readModeLease            = "lease_read"
)

type RaftNode struct {
	mu sync.Mutex

	id          int
	role        Role
	currentTerm int
	votedFor    int
	log         []LogEntry

	commitIndex int
	lastApplied int

	snapshotIndex int
	snapshotTerm  int

	nextIndex  map[int]int
	matchIndex map[int]int

	peers    []Peer
	self     Peer
	leaderID int

	store   *kv.StateMachine
	storage *Storage
	client  *http.Client

	electionMin       time.Duration
	electionMax       time.Duration
	heartbeatInterval time.Duration
	snapshotThreshold int
	leaderLease       time.Duration
	leaderLeaseUntil  time.Time
	resetElectionCh   chan struct{}
	stopCh            chan struct{}
	stopOnce          sync.Once
}

func NewRaftNode(id int, peers []Peer) (*RaftNode, error) {
	var self Peer
	found := false
	for _, peer := range peers {
		if peer.ID == id {
			self = peer
			found = true
			break
		}
	}
	if !found {
		return nil, fmt.Errorf("node id %d not found in cluster config", id)
	}

	storage := NewStorage(self.DataDir)
	state, err := storage.Load()
	if err != nil {
		return nil, err
	}
	activePeers := append([]Peer(nil), peers...)
	if len(state.Peers) > 0 {
		activePeers = clonePeers(state.Peers)
	}

	store := kv.NewStateMachine()
	store.Restore(state.Snapshot)

	n := &RaftNode{
		id:                id,
		role:              Follower,
		currentTerm:       state.CurrentTerm,
		votedFor:          state.VotedFor,
		log:               cloneEntries(state.Log),
		commitIndex:       state.CommitIndex,
		lastApplied:       state.SnapshotIndex,
		snapshotIndex:     state.SnapshotIndex,
		snapshotTerm:      state.SnapshotTerm,
		nextIndex:         make(map[int]int),
		matchIndex:        make(map[int]int),
		peers:             activePeers,
		self:              self,
		leaderID:          0,
		store:             store,
		storage:           storage,
		client:            &http.Client{Timeout: 350 * time.Millisecond},
		electionMin:       300 * time.Millisecond,
		electionMax:       600 * time.Millisecond,
		heartbeatInterval: 100 * time.Millisecond,
		snapshotThreshold: defaultSnapshotThreshold,
		leaderLease:       defaultLeaderLease,
		resetElectionCh:   make(chan struct{}, 1),
		stopCh:            make(chan struct{}),
	}

	n.mu.Lock()
	n.applyCommittedLocked()
	n.mu.Unlock()

	return n, nil
}

func (n *RaftNode) Start() {
	log.Printf("[node %d] start role=%s term=%d api=%s raft=%s", n.id, n.role, n.currentTerm, n.self.APIAddr, n.self.RaftAddr)
	n.signalElectionReset()
	go n.electionLoop()
}

func (n *RaftNode) Stop() {
	n.stopOnce.Do(func() {
		close(n.stopCh)
	})
}

func (n *RaftNode) ID() int {
	return n.id
}

func (n *RaftNode) Self() Peer {
	return n.self
}

func (n *RaftNode) Peers() []Peer {
	n.mu.Lock()
	defer n.mu.Unlock()
	return clonePeers(n.peers)
}

func (n *RaftNode) Status() Status {
	n.mu.Lock()
	defer n.mu.Unlock()

	return Status{
		ID:            n.id,
		Role:          n.role,
		Term:          n.currentTerm,
		LeaderID:      n.leaderID,
		LeaderAddr:    n.leaderAddrLocked(),
		CommitIndex:   n.commitIndex,
		LastApplied:   n.lastApplied,
		LogLen:        n.lastLogIndexLocked() - n.snapshotIndex,
		LastLogIndex:  n.lastLogIndexLocked(),
		LastLogTerm:   n.lastLogTermLocked(),
		SnapshotIndex: n.snapshotIndex,
		SnapshotTerm:  n.snapshotTerm,
		ClusterSize:   len(n.peers),
		Member:        n.isMemberLocked(n.id),
		ReadMode:      readModeLease,
	}
}

func (n *RaftNode) LeaderInfo() LeaderInfo {
	n.mu.Lock()
	defer n.mu.Unlock()

	return LeaderInfo{
		LeaderID:   n.leaderID,
		LeaderAddr: n.leaderAddrLocked(),
		IsLeader:   n.role == Leader,
	}
}

func (n *RaftNode) Snapshot() map[string]string {
	return n.store.Snapshot()
}

func (n *RaftNode) Get(key string) (string, bool, error) {
	n.mu.Lock()
	isLeader := n.role == Leader
	n.mu.Unlock()

	if !isLeader {
		return "", false, ErrNotLeader
	}
	if err := n.ensureLeaderLease(); err != nil {
		return "", false, err
	}
	value, ok := n.store.Get(key)
	return value, ok, nil
}

func (n *RaftNode) Propose(cmd kv.Command) (LogEntry, error) {
	if err := validateCommand(cmd); err != nil {
		return LogEntry{}, err
	}

	n.mu.Lock()
	if n.role != Leader || !n.isMemberLocked(n.id) {
		n.mu.Unlock()
		return LogEntry{}, ErrNotLeader
	}

	entry := LogEntry{
		Index:   n.lastLogIndexLocked() + 1,
		Term:    n.currentTerm,
		Command: cmd,
	}
	n.log = append(n.log, entry)
	n.matchIndex[n.id] = entry.Index
	n.nextIndex[n.id] = entry.Index + 1
	n.persistLocked()
	peers := clonePeers(n.peers)
	log.Printf("[node %d] append client command index=%d term=%d op=%s key=%s", n.id, entry.Index, entry.Term, cmd.Op, cmd.Key)

	if n.majorityLocked() == 1 {
		n.commitIndex = entry.Index
		n.applyCommittedLocked()
		n.mu.Unlock()
		return entry, nil
	}
	n.mu.Unlock()

	done := make(chan struct{}, len(peers)-1)
	for _, peer := range peers {
		if peer.ID == n.id {
			continue
		}
		peer := peer
		go func() {
			n.replicateToPeer(peer)
			done <- struct{}{}
		}()
	}

	timeout := time.NewTimer(3 * time.Second)
	defer timeout.Stop()
	tick := time.NewTicker(20 * time.Millisecond)
	defer tick.Stop()

	remaining := len(peers) - 1
	for {
		n.mu.Lock()
		committed := n.role == Leader && n.commitIndex >= entry.Index
		steppedDown := n.role != Leader
		n.mu.Unlock()

		if committed {
			n.broadcastAppendEntries()
			return entry, nil
		}
		if steppedDown {
			return LogEntry{}, ErrNotLeader
		}
		if remaining == 0 {
			return LogEntry{}, ErrCommitTimeout
		}

		select {
		case <-done:
			remaining--
		case <-tick.C:
		case <-timeout.C:
			return LogEntry{}, ErrCommitTimeout
		}
	}
}

func (n *RaftNode) HandleRequestVote(args RequestVoteArgs) RequestVoteReply {
	resetElection := false
	stateChanged := false

	n.mu.Lock()
	reply := RequestVoteReply{Term: n.currentTerm}
	if !n.isMemberLocked(n.id) || !n.isMemberLocked(args.CandidateID) {
		n.mu.Unlock()
		return reply
	}
	if args.Term < n.currentTerm {
		n.mu.Unlock()
		return reply
	}

	if args.Term > n.currentTerm {
		n.becomeFollowerLocked(args.Term, 0)
		stateChanged = true
	}

	canVote := n.votedFor == -1 || n.votedFor == args.CandidateID
	upToDate := n.isCandidateLogUpToDateLocked(args.LastLogIndex, args.LastLogTerm)
	if canVote && upToDate {
		n.votedFor = args.CandidateID
		n.role = Follower
		n.leaderID = 0
		reply.VoteGranted = true
		resetElection = true
		stateChanged = true
		log.Printf("[node %d] vote granted to node %d term=%d", n.id, args.CandidateID, n.currentTerm)
	}
	if stateChanged {
		n.persistLocked()
	}
	reply.Term = n.currentTerm
	n.mu.Unlock()

	if resetElection {
		n.signalElectionReset()
	}
	return reply
}

func (n *RaftNode) HandleAppendEntries(args AppendEntriesArgs) AppendEntriesReply {
	resetElection := false
	stateChanged := false

	n.mu.Lock()
	reply := AppendEntriesReply{Term: n.currentTerm, MatchIndex: n.lastLogIndexLocked()}
	if args.Term < n.currentTerm {
		n.mu.Unlock()
		return reply
	}
	if !n.isMemberLocked(args.LeaderID) {
		n.mu.Unlock()
		return reply
	}

	if args.Term > n.currentTerm || n.role != Follower {
		if args.Term > n.currentTerm {
			stateChanged = true
		}
		n.becomeFollowerLocked(args.Term, args.LeaderID)
	}
	n.leaderID = args.LeaderID
	resetElection = true

	if args.PrevLogIndex < n.snapshotIndex {
		if stateChanged {
			n.persistLocked()
		}
		reply.Term = n.currentTerm
		reply.Success = false
		reply.MatchIndex = n.snapshotIndex
		n.mu.Unlock()
		n.signalElectionReset()
		return reply
	}
	prevTerm, ok := n.termAtLocked(args.PrevLogIndex)
	if !ok {
		if stateChanged {
			n.persistLocked()
		}
		reply.Term = n.currentTerm
		reply.Success = false
		reply.MatchIndex = n.lastLogIndexLocked()
		n.mu.Unlock()
		n.signalElectionReset()
		return reply
	}
	if prevTerm != args.PrevLogTerm {
		if stateChanged {
			n.persistLocked()
		}
		reply.Term = n.currentTerm
		reply.Success = false
		reply.MatchIndex = args.PrevLogIndex - 1
		if reply.MatchIndex < n.snapshotIndex {
			reply.MatchIndex = n.snapshotIndex
		}
		n.mu.Unlock()
		n.signalElectionReset()
		return reply
	}

	changed := n.mergeEntriesLocked(args.PrevLogIndex, args.Entries)
	if args.LeaderCommit > n.commitIndex {
		n.commitIndex = minInt(args.LeaderCommit, n.lastLogIndexLocked())
		changed = true
		n.applyCommittedLocked()
	}
	if changed || stateChanged {
		n.persistLocked()
	}

	reply.Term = n.currentTerm
	reply.Success = true
	reply.MatchIndex = n.lastLogIndexLocked()
	n.mu.Unlock()

	if resetElection {
		n.signalElectionReset()
	}
	return reply
}

func (n *RaftNode) HandleInstallSnapshot(args InstallSnapshotArgs) InstallSnapshotReply {
	resetElection := false

	n.mu.Lock()
	reply := InstallSnapshotReply{Term: n.currentTerm, MatchIndex: n.snapshotIndex}
	if args.Term < n.currentTerm {
		n.mu.Unlock()
		return reply
	}
	if len(args.Peers) > 0 {
		n.peers = clonePeers(args.Peers)
		n.sortPeersLocked()
	}
	if !n.isMemberLocked(args.LeaderID) {
		n.mu.Unlock()
		return reply
	}
	if args.Term > n.currentTerm || n.role != Follower {
		n.becomeFollowerLocked(args.Term, args.LeaderID)
	}
	n.leaderID = args.LeaderID
	resetElection = true

	if args.LastIncludedIndex < n.snapshotIndex {
		reply.Term = n.currentTerm
		reply.Success = true
		reply.MatchIndex = n.snapshotIndex
		n.persistLocked()
		n.mu.Unlock()
		n.signalElectionReset()
		return reply
	}

	n.store.Restore(args.Snapshot)
	n.snapshotIndex = args.LastIncludedIndex
	n.snapshotTerm = args.LastIncludedTerm

	newLog := []LogEntry{{Index: n.snapshotIndex, Term: n.snapshotTerm}}
	if n.hasLogIndexLocked(args.LastIncludedIndex) {
		offset := n.logOffsetLocked(args.LastIncludedIndex)
		if offset+1 < len(n.log) {
			newLog = append(newLog, cloneEntries(n.log[offset+1:])...)
		}
	}
	n.log = newLog
	n.commitIndex = maxInt(n.commitIndex, args.LastIncludedIndex)
	n.commitIndex = minInt(n.commitIndex, n.lastLogIndexLocked())
	if n.commitIndex < n.snapshotIndex {
		n.commitIndex = n.snapshotIndex
	}
	n.lastApplied = n.snapshotIndex
	n.ensurePeerProgressLocked(n.id)
	n.applyCommittedLocked()

	reply.Term = n.currentTerm
	reply.Success = true
	reply.MatchIndex = n.snapshotIndex
	n.mu.Unlock()

	if resetElection {
		n.signalElectionReset()
	}
	return reply
}

func (n *RaftNode) startElection() {
	n.mu.Lock()
	if n.role == Leader || !n.isMemberLocked(n.id) {
		n.mu.Unlock()
		return
	}

	n.role = Candidate
	n.currentTerm++
	term := n.currentTerm
	n.votedFor = n.id
	n.leaderID = 0
	lastIndex := n.lastLogIndexLocked()
	lastTerm := n.lastLogTermLocked()
	majority := n.majorityLocked()
	peers := clonePeers(n.peers)
	n.persistLocked()
	log.Printf("[node %d] start election term=%d", n.id, term)
	n.mu.Unlock()

	n.signalElectionReset()

	var votes int32 = 1
	var promoted sync.Once
	if majority == 1 {
		n.promoteToLeader(term)
		return
	}

	args := RequestVoteArgs{
		Term:         term,
		CandidateID:  n.id,
		LastLogIndex: lastIndex,
		LastLogTerm:  lastTerm,
	}

	for _, peer := range peers {
		if peer.ID == n.id {
			continue
		}
		peer := peer
		go func() {
			reply, ok := n.sendRequestVote(peer, args)
			if !ok {
				return
			}
			if reply.Term > term {
				n.stepDown(reply.Term, 0)
				return
			}
			if reply.VoteGranted && atomic.AddInt32(&votes, 1) >= int32(majority) {
				promoted.Do(func() {
					n.promoteToLeader(term)
				})
			}
		}()
	}
}

func (n *RaftNode) promoteToLeader(term int) {
	n.mu.Lock()
	if n.role != Candidate || n.currentTerm != term || !n.isMemberLocked(n.id) {
		n.mu.Unlock()
		return
	}

	lastIndex := n.lastLogIndexLocked()
	n.role = Leader
	n.leaderID = n.id
	n.leaderLeaseUntil = time.Time{}
	for _, peer := range n.peers {
		n.nextIndex[peer.ID] = lastIndex + 1
		n.matchIndex[peer.ID] = 0
	}
	n.matchIndex[n.id] = lastIndex
	log.Printf("[node %d] become Leader term=%d", n.id, n.currentTerm)
	n.mu.Unlock()

	go n.heartbeatLoop(term)
}

func (n *RaftNode) stepDown(term int, leaderID int) {
	n.mu.Lock()
	n.becomeFollowerLocked(term, leaderID)
	n.persistLocked()
	n.mu.Unlock()
	n.signalElectionReset()
}

func (n *RaftNode) becomeFollowerLocked(term int, leaderID int) {
	if term > n.currentTerm {
		n.currentTerm = term
		n.votedFor = -1
	}
	if n.role != Follower {
		log.Printf("[node %d] become Follower term=%d leader=%d", n.id, n.currentTerm, leaderID)
	}
	n.role = Follower
	n.leaderID = leaderID
	n.leaderLeaseUntil = time.Time{}
}

func (n *RaftNode) broadcastAppendEntries() {
	n.mu.Lock()
	peers := clonePeers(n.peers)
	n.mu.Unlock()

	for _, peer := range peers {
		if peer.ID == n.id {
			continue
		}
		peer := peer
		go n.replicateToPeer(peer)
	}
}

func (n *RaftNode) replicateToPeer(peer Peer) bool {
	maxAttempts := n.maxReplicationAttempts()
	for attempt := 0; attempt < maxAttempts; attempt++ {
		if args, ok := n.buildInstallSnapshotArgs(peer.ID); ok {
			reply, ok := n.sendInstallSnapshot(peer, args)
			if !ok {
				return false
			}
			n.mu.Lock()
			if reply.Term > n.currentTerm {
				n.becomeFollowerLocked(reply.Term, 0)
				n.persistLocked()
				n.mu.Unlock()
				n.signalElectionReset()
				return false
			}
			if n.role != Leader || n.currentTerm != args.Term {
				n.mu.Unlock()
				return false
			}
			if reply.Success {
				n.matchIndex[peer.ID] = reply.MatchIndex
				n.nextIndex[peer.ID] = reply.MatchIndex + 1
				n.advanceCommitIndexLocked()
				n.mu.Unlock()
				continue
			}
			n.mu.Unlock()
			return false
		}

		args, ok := n.buildAppendEntriesArgs(peer.ID)
		if !ok {
			return false
		}

		reply, ok := n.sendAppendEntries(peer, args)
		if !ok {
			return false
		}

		n.mu.Lock()
		if reply.Term > n.currentTerm {
			n.becomeFollowerLocked(reply.Term, 0)
			n.persistLocked()
			n.mu.Unlock()
			n.signalElectionReset()
			return false
		}
		if n.role != Leader || n.currentTerm != args.Term {
			n.mu.Unlock()
			return false
		}

		if reply.Success {
			n.matchIndex[peer.ID] = reply.MatchIndex
			n.nextIndex[peer.ID] = reply.MatchIndex + 1
			n.advanceCommitIndexLocked()
			n.mu.Unlock()
			return true
		}

		oldNext := n.nextIndex[peer.ID]
		newNext := reply.MatchIndex + 1
		if newNext < 1 {
			newNext = 1
		}
		if newNext >= oldNext && oldNext > 1 {
			newNext = oldNext - 1
		}
		n.nextIndex[peer.ID] = newNext
		n.mu.Unlock()
	}
	return false
}

func (n *RaftNode) buildAppendEntriesArgs(peerID int) (AppendEntriesArgs, bool) {
	n.mu.Lock()
	defer n.mu.Unlock()

	if n.role != Leader {
		return AppendEntriesArgs{}, false
	}

	next := n.nextIndex[peerID]
	if next <= n.snapshotIndex {
		return AppendEntriesArgs{}, false
	}
	if next < n.snapshotIndex+1 {
		next = n.snapshotIndex + 1
	}
	lastIndex := n.lastLogIndexLocked()
	if next > lastIndex+1 {
		next = lastIndex + 1
	}
	prevIndex := next - 1
	prevTerm, ok := n.termAtLocked(prevIndex)
	if !ok {
		return AppendEntriesArgs{}, false
	}

	return AppendEntriesArgs{
		Term:         n.currentTerm,
		LeaderID:     n.id,
		PrevLogIndex: prevIndex,
		PrevLogTerm:  prevTerm,
		Entries:      n.entriesFromLocked(next),
		LeaderCommit: n.commitIndex,
	}, true
}

func (n *RaftNode) buildInstallSnapshotArgs(peerID int) (InstallSnapshotArgs, bool) {
	n.mu.Lock()
	defer n.mu.Unlock()

	if n.role != Leader {
		return InstallSnapshotArgs{}, false
	}
	next := n.nextIndex[peerID]
	if next == 0 {
		next = n.snapshotIndex + 1
	}
	if next > n.snapshotIndex {
		return InstallSnapshotArgs{}, false
	}
	return InstallSnapshotArgs{
		Term:              n.currentTerm,
		LeaderID:          n.id,
		LastIncludedIndex: n.snapshotIndex,
		LastIncludedTerm:  n.snapshotTerm,
		Snapshot:          cloneSnapshot(n.store.Snapshot()),
		Peers:             clonePeers(n.peers),
		LeaderCommit:      n.commitIndex,
	}, true
}

func (n *RaftNode) mergeEntriesLocked(prevLogIndex int, entries []LogEntry) bool {
	changed := false
	for i, entry := range entries {
		index := prevLogIndex + 1 + i
		entry.Index = index
		if index <= n.snapshotIndex {
			continue
		}

		offset := n.logOffsetLocked(index)
		if offset >= 0 && offset < len(n.log) {
			if n.log[offset].Term == entry.Term {
				continue
			}
			n.log = n.log[:offset]
			for j := i; j < len(entries); j++ {
				newEntry := entries[j]
				newEntry.Index = prevLogIndex + 1 + j
				if newEntry.Index <= n.snapshotIndex {
					continue
				}
				n.log = append(n.log, newEntry)
			}
			return true
		}

		for j := i; j < len(entries); j++ {
			newEntry := entries[j]
			newEntry.Index = prevLogIndex + 1 + j
			if newEntry.Index <= n.snapshotIndex {
				continue
			}
			n.log = append(n.log, newEntry)
		}
		changed = true
		break
	}
	return changed
}

func (n *RaftNode) advanceCommitIndexLocked() {
	for index := n.lastLogIndexLocked(); index > n.commitIndex; index-- {
		term, ok := n.termAtLocked(index)
		if !ok || term != n.currentTerm {
			continue
		}

		replicated := 1
		for _, peer := range n.peers {
			if peer.ID == n.id {
				continue
			}
			if n.matchIndex[peer.ID] >= index {
				replicated++
			}
		}

		if replicated >= n.majorityLocked() {
			n.commitIndex = index
			n.applyCommittedLocked()
			log.Printf("[node %d] commit index advanced to %d", n.id, n.commitIndex)
			return
		}
	}
}

func (n *RaftNode) applyCommittedLocked() {
	for n.lastApplied < n.commitIndex {
		n.lastApplied++
		entry, ok := n.entryAtLocked(n.lastApplied)
		if !ok {
			if n.lastApplied <= n.snapshotIndex {
				continue
			}
			log.Printf("[node %d] missing committed log index=%d", n.id, n.lastApplied)
			break
		}
		if entry.Command.Op == "" {
			continue
		}
		if err := n.applyCommandLocked(entry.Command); err != nil {
			log.Printf("[node %d] apply index=%d failed: %v", n.id, entry.Index, err)
		}
	}
	n.maybeCompactLogLocked()
	n.persistLocked()
}

func (n *RaftNode) applyCommandLocked(cmd kv.Command) error {
	switch cmd.Op {
	case kv.OpPut, kv.OpDelete:
		return n.store.Apply(cmd)
	case kv.OpAddNode:
		var peer Peer
		if err := json.Unmarshal([]byte(cmd.Value), &peer); err != nil {
			return err
		}
		return n.addPeerLocked(peer)
	case kv.OpRemoveNode:
		id, err := strconv.Atoi(cmd.Key)
		if err != nil {
			return err
		}
		n.removePeerLocked(id)
		return nil
	default:
		return kv.ErrUnknownOp
	}
}

func (n *RaftNode) maybeCompactLogLocked() {
	if n.snapshotThreshold <= 0 || n.commitIndex-n.snapshotIndex < n.snapshotThreshold {
		return
	}
	term, ok := n.termAtLocked(n.commitIndex)
	if !ok {
		return
	}
	offset := n.logOffsetLocked(n.commitIndex)
	if offset < 0 || offset >= len(n.log) {
		return
	}

	n.snapshotIndex = n.commitIndex
	n.snapshotTerm = term
	newLog := []LogEntry{{Index: n.snapshotIndex, Term: n.snapshotTerm}}
	if offset+1 < len(n.log) {
		newLog = append(newLog, cloneEntries(n.log[offset+1:])...)
	}
	n.log = newLog
	n.matchIndex[n.id] = n.snapshotIndex
	n.nextIndex[n.id] = n.snapshotIndex + 1
	log.Printf("[node %d] compact log to snapshot index=%d term=%d keys=%d", n.id, n.snapshotIndex, n.snapshotTerm, n.store.Size())
}

func (n *RaftNode) persistLocked() {
	if n.storage == nil {
		return
	}
	state := PersistentState{
		CurrentTerm:   n.currentTerm,
		VotedFor:      n.votedFor,
		Log:           cloneEntries(n.log),
		CommitIndex:   n.commitIndex,
		LastApplied:   n.lastApplied,
		SnapshotIndex: n.snapshotIndex,
		SnapshotTerm:  n.snapshotTerm,
		Snapshot:      cloneSnapshot(n.store.Snapshot()),
		Peers:         clonePeers(n.peers),
	}
	if err := n.storage.Save(state); err != nil {
		log.Printf("[node %d] persist failed: %v", n.id, err)
	}
}

func (n *RaftNode) ensureLeaderLease() error {
	n.mu.Lock()
	now := time.Now()
	if n.role != Leader || !n.isMemberLocked(n.id) {
		n.mu.Unlock()
		return ErrNotLeader
	}
	if now.Before(n.leaderLeaseUntil) {
		n.mu.Unlock()
		return nil
	}
	term := n.currentTerm
	peers := clonePeers(n.peers)
	majority := n.majorityLocked()
	lease := n.leaderLease
	n.mu.Unlock()

	if majority == 1 {
		n.mu.Lock()
		if n.role == Leader && n.currentTerm == term {
			n.leaderLeaseUntil = time.Now().Add(lease)
			n.mu.Unlock()
			return nil
		}
		n.mu.Unlock()
		return ErrNotLeader
	}

	var successes int32 = 1
	done := make(chan struct{}, len(peers)-1)
	for _, peer := range peers {
		if peer.ID == n.id {
			continue
		}
		peer := peer
		go func() {
			if n.replicateToPeer(peer) {
				atomic.AddInt32(&successes, 1)
			}
			done <- struct{}{}
		}()
	}

	timeout := time.NewTimer(lease)
	defer timeout.Stop()
	for completed := 0; completed < len(peers)-1; {
		if int(atomic.LoadInt32(&successes)) >= majority {
			n.mu.Lock()
			if n.role == Leader && n.currentTerm == term {
				n.leaderLeaseUntil = time.Now().Add(lease)
				n.mu.Unlock()
				return nil
			}
			n.mu.Unlock()
			return ErrNotLeader
		}
		select {
		case <-done:
			completed++
		case <-timeout.C:
			n.mu.Lock()
			leader := n.role == Leader && n.currentTerm == term
			n.mu.Unlock()
			if !leader {
				return ErrNotLeader
			}
			return ErrCommitTimeout
		}
	}

	if int(atomic.LoadInt32(&successes)) >= majority {
		n.mu.Lock()
		if n.role == Leader && n.currentTerm == term {
			n.leaderLeaseUntil = time.Now().Add(lease)
			n.mu.Unlock()
			return nil
		}
		n.mu.Unlock()
		return ErrNotLeader
	}
	return ErrCommitTimeout
}

func (n *RaftNode) leaderAddrLocked() string {
	for _, peer := range n.peers {
		if peer.ID == n.leaderID {
			return peer.APIAddr
		}
	}
	return ""
}

func (n *RaftNode) ClusterPeers() []Peer {
	n.mu.Lock()
	defer n.mu.Unlock()
	return clonePeers(n.peers)
}

func (n *RaftNode) AddPeer(peer Peer) (LogEntry, error) {
	data, err := json.Marshal(peer)
	if err != nil {
		return LogEntry{}, err
	}
	return n.Propose(kv.Command{
		Op:    kv.OpAddNode,
		Key:   strconv.Itoa(peer.ID),
		Value: string(data),
	})
}

func (n *RaftNode) RemovePeer(id int) (LogEntry, error) {
	return n.Propose(kv.Command{
		Op:  kv.OpRemoveNode,
		Key: strconv.Itoa(id),
	})
}

func (n *RaftNode) SetSnapshotThreshold(threshold int) {
	n.mu.Lock()
	defer n.mu.Unlock()
	n.snapshotThreshold = threshold
}

func (n *RaftNode) addPeerLocked(peer Peer) error {
	if peer.ID <= 0 || peer.APIAddr == "" || peer.RaftAddr == "" || peer.DataDir == "" {
		return fmt.Errorf("invalid peer")
	}
	for i := range n.peers {
		if n.peers[i].ID == peer.ID {
			n.peers[i] = peer
			n.ensurePeerProgressLocked(peer.ID)
			n.sortPeersLocked()
			return nil
		}
	}
	n.peers = append(n.peers, peer)
	n.ensurePeerProgressLocked(peer.ID)
	n.sortPeersLocked()
	log.Printf("[node %d] add cluster member node=%d api=%s raft=%s", n.id, peer.ID, peer.APIAddr, peer.RaftAddr)
	return nil
}

func (n *RaftNode) removePeerLocked(id int) {
	nextPeers := n.peers[:0]
	for _, peer := range n.peers {
		if peer.ID != id {
			nextPeers = append(nextPeers, peer)
		}
	}
	n.peers = nextPeers
	delete(n.nextIndex, id)
	delete(n.matchIndex, id)
	if id == n.id {
		n.role = Follower
		n.leaderID = 0
		n.leaderLeaseUntil = time.Time{}
	}
	log.Printf("[node %d] remove cluster member node=%d", n.id, id)
}

func (n *RaftNode) sortPeersLocked() {
	sort.Slice(n.peers, func(i, j int) bool {
		return n.peers[i].ID < n.peers[j].ID
	})
}

func (n *RaftNode) ensurePeerProgressLocked(id int) {
	if _, ok := n.nextIndex[id]; !ok {
		n.nextIndex[id] = 1
	}
	if _, ok := n.matchIndex[id]; !ok {
		n.matchIndex[id] = 0
	}
	if id == n.id {
		n.matchIndex[id] = n.lastLogIndexLocked()
		n.nextIndex[id] = n.lastLogIndexLocked() + 1
	}
}

func (n *RaftNode) isMemberLocked(id int) bool {
	for _, peer := range n.peers {
		if peer.ID == id {
			return true
		}
	}
	return false
}

func (n *RaftNode) majorityLocked() int {
	return len(n.peers)/2 + 1
}

func (n *RaftNode) maxReplicationAttempts() int {
	n.mu.Lock()
	defer n.mu.Unlock()

	attempts := len(n.log) + 2
	if attempts < 3 {
		return 3
	}
	return attempts
}

func validateCommand(cmd kv.Command) error {
	if cmd.Key == "" {
		return kv.ErrEmptyKey
	}
	switch cmd.Op {
	case kv.OpPut, kv.OpDelete:
		return nil
	case kv.OpAddNode:
		var peer Peer
		if err := json.Unmarshal([]byte(cmd.Value), &peer); err != nil {
			return err
		}
		if peer.ID <= 0 || peer.APIAddr == "" || peer.RaftAddr == "" || peer.DataDir == "" {
			return fmt.Errorf("invalid peer")
		}
		return nil
	case kv.OpRemoveNode:
		if _, err := strconv.Atoi(cmd.Key); err != nil {
			return err
		}
		return nil
	default:
		return kv.ErrUnknownOp
	}
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func cloneSnapshot(snapshot map[string]string) map[string]string {
	cp := make(map[string]string, len(snapshot))
	for key, value := range snapshot {
		cp[key] = value
	}
	return cp
}

func clonePeers(peers []Peer) []Peer {
	cp := make([]Peer, len(peers))
	copy(cp, peers)
	return cp
}
