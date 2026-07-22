package raft

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sync"
)

type PersistentState struct {
	CurrentTerm   int               `json:"current_term"`
	VotedFor      int               `json:"voted_for"`
	Log           []LogEntry        `json:"log"`
	CommitIndex   int               `json:"commit_index"`
	LastApplied   int               `json:"last_applied"`
	SnapshotIndex int               `json:"snapshot_index"`
	SnapshotTerm  int               `json:"snapshot_term"`
	Snapshot      map[string]string `json:"snapshot,omitempty"`
	Peers         []Peer            `json:"peers,omitempty"`
}

type Storage struct {
	mu   sync.Mutex
	path string
}

func NewStorage(dataDir string) *Storage {
	return &Storage{path: filepath.Join(dataDir, "state.json")}
}

func (s *Storage) Load() (PersistentState, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	state := defaultPersistentState()
	data, err := os.ReadFile(s.path)
	if errors.Is(err, os.ErrNotExist) {
		return state, nil
	}
	if err != nil {
		return state, err
	}
	if len(data) == 0 {
		return state, nil
	}
	if err := json.Unmarshal(data, &state); err != nil {
		return state, err
	}
	normalizePersistentState(&state)
	return state, nil
}

func (s *Storage) Save(state PersistentState) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	normalizePersistentState(&state)
	if err := os.MkdirAll(filepath.Dir(s.path), 0o755); err != nil {
		return err
	}

	data, err := json.MarshalIndent(state, "", "  ")
	if err != nil {
		return err
	}

	tmp := s.path + ".tmp"
	if err := os.WriteFile(tmp, data, 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, s.path)
}

func defaultPersistentState() PersistentState {
	return PersistentState{
		VotedFor: -1,
		Log:      []LogEntry{{Index: 0, Term: 0}},
		Snapshot: make(map[string]string),
	}
}

func normalizePersistentState(state *PersistentState) {
	if len(state.Log) == 0 {
		state.Log = []LogEntry{{Index: state.SnapshotIndex, Term: state.SnapshotTerm}}
	}
	if state.SnapshotIndex < 0 {
		state.SnapshotIndex = 0
	}
	if state.Log[0].Index != state.SnapshotIndex || state.Log[0].Term != state.SnapshotTerm {
		state.Log = append([]LogEntry{{Index: state.SnapshotIndex, Term: state.SnapshotTerm}}, state.Log...)
	}
	for i := 1; i < len(state.Log); i++ {
		if state.Log[i].Index <= state.Log[i-1].Index {
			state.Log[i].Index = state.Log[i-1].Index + 1
		}
	}
	if state.VotedFor == 0 {
		state.VotedFor = -1
	}
	lastIndex := state.Log[len(state.Log)-1].Index
	if state.CommitIndex > lastIndex {
		state.CommitIndex = lastIndex
	}
	if state.CommitIndex < state.SnapshotIndex {
		state.CommitIndex = state.SnapshotIndex
	}
	if state.LastApplied > state.CommitIndex {
		state.LastApplied = state.CommitIndex
	}
	if state.LastApplied < state.SnapshotIndex {
		state.LastApplied = state.SnapshotIndex
	}
	if state.Snapshot == nil {
		state.Snapshot = make(map[string]string)
	}
}
