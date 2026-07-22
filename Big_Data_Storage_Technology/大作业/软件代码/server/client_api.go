package server

import (
	"encoding/json"
	"errors"
	"net/http"

	"raft-kv/kv"
	"raft-kv/raft"
)

type kvRequest struct {
	Key   string `json:"key"`
	Value string `json:"value"`
}

type removePeerRequest struct {
	ID int `json:"id"`
}

func (s *HTTPServer) handleStatus(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodGet) {
		return
	}
	writeJSON(w, http.StatusOK, s.node.Status())
}

func (s *HTTPServer) handleLeader(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodGet) {
		return
	}
	writeJSON(w, http.StatusOK, s.node.LeaderInfo())
}

func (s *HTTPServer) handlePut(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodPost) {
		return
	}

	var req kvRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json"})
		return
	}

	entry, err := s.node.Propose(kv.Command{Op: kv.OpPut, Key: req.Key, Value: req.Value})
	if err != nil {
		s.writeClientError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "index": entry.Index, "term": entry.Term})
}

func (s *HTTPServer) handleDelete(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodPost) {
		return
	}

	var req kvRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json"})
		return
	}

	entry, err := s.node.Propose(kv.Command{Op: kv.OpDelete, Key: req.Key})
	if err != nil {
		s.writeClientError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "index": entry.Index, "term": entry.Term})
}

func (s *HTTPServer) handleGet(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodGet) {
		return
	}

	key := r.URL.Query().Get("key")
	value, ok, err := s.node.Get(key)
	if err != nil {
		s.writeClientError(w, err)
		return
	}
	if !ok {
		writeJSON(w, http.StatusNotFound, map[string]any{"found": false, "key": key})
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"found": true, "key": key, "value": value, "read_mode": "lease_read"})
}

func (s *HTTPServer) handleCluster(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodGet) {
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"peers":  s.node.ClusterPeers(),
		"status": s.node.Status(),
	})
}

func (s *HTTPServer) handleClusterAdd(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodPost) {
		return
	}

	var peer raft.Peer
	if err := json.NewDecoder(r.Body).Decode(&peer); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json"})
		return
	}
	entry, err := s.node.AddPeer(peer)
	if err != nil {
		s.writeClientError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "index": entry.Index, "term": entry.Term})
}

func (s *HTTPServer) handleClusterRemove(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodPost) {
		return
	}

	var req removePeerRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json"})
		return
	}
	entry, err := s.node.RemovePeer(req.ID)
	if err != nil {
		s.writeClientError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "index": entry.Index, "term": entry.Term})
}

func (s *HTTPServer) handleRequestVote(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodPost) {
		return
	}

	var args raft.RequestVoteArgs
	if err := json.NewDecoder(r.Body).Decode(&args); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json"})
		return
	}
	writeJSON(w, http.StatusOK, s.node.HandleRequestVote(args))
}

func (s *HTTPServer) handleAppendEntries(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodPost) {
		return
	}

	var args raft.AppendEntriesArgs
	if err := json.NewDecoder(r.Body).Decode(&args); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json"})
		return
	}
	writeJSON(w, http.StatusOK, s.node.HandleAppendEntries(args))
}

func (s *HTTPServer) handleInstallSnapshot(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodPost) {
		return
	}

	var args raft.InstallSnapshotArgs
	if err := json.NewDecoder(r.Body).Decode(&args); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json"})
		return
	}
	writeJSON(w, http.StatusOK, s.node.HandleInstallSnapshot(args))
}

func (s *HTTPServer) writeClientError(w http.ResponseWriter, err error) {
	if errors.Is(err, raft.ErrNotLeader) {
		leader := s.node.LeaderInfo()
		writeJSON(w, http.StatusConflict, map[string]any{
			"error":       "not leader",
			"leader_id":   leader.LeaderID,
			"leader_addr": leader.LeaderAddr,
		})
		return
	}
	if errors.Is(err, raft.ErrCommitTimeout) {
		writeJSON(w, http.StatusGatewayTimeout, map[string]string{"error": "commit timeout"})
		return
	}
	writeJSON(w, http.StatusBadRequest, map[string]string{"error": err.Error()})
}
