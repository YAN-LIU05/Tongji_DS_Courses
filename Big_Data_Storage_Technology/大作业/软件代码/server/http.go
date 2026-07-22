package server

import (
	"context"
	"embed"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"strings"
	"time"

	"raft-kv/raft"
)

//go:embed static/ui.html
var uiFS embed.FS

type HTTPServer struct {
	node      *raft.RaftNode
	apiServer *http.Server
	rpcServer *http.Server
}

func NewHTTPServer(node *raft.RaftNode) *HTTPServer {
	s := &HTTPServer{node: node}
	self := node.Self()
	s.apiServer = &http.Server{
		Addr:              self.APIAddr,
		Handler:           s.apiMux(),
		ReadHeaderTimeout: 3 * time.Second,
	}
	s.rpcServer = &http.Server{
		Addr:              self.RaftAddr,
		Handler:           s.rpcMux(),
		ReadHeaderTimeout: 3 * time.Second,
	}
	return s
}

func (s *HTTPServer) Start() <-chan error {
	errCh := make(chan error, 2)
	go func() {
		log.Printf("[node %d] api server listen on %s", s.node.ID(), s.apiServer.Addr)
		if err := s.apiServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- err
		}
	}()
	go func() {
		log.Printf("[node %d] raft rpc server listen on %s", s.node.ID(), s.rpcServer.Addr)
		if err := s.rpcServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- err
		}
	}()
	return errCh
}

func (s *HTTPServer) Shutdown(ctx context.Context) error {
	apiErr := s.apiServer.Shutdown(ctx)
	rpcErr := s.rpcServer.Shutdown(ctx)
	if apiErr != nil {
		return apiErr
	}
	return rpcErr
}

func (s *HTTPServer) apiMux() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/ui", s.handleUI)
	mux.HandleFunc("/ui/", s.handleUI)
	mux.HandleFunc("/status", s.handleStatus)
	mux.HandleFunc("/leader", s.handleLeader)
	mux.HandleFunc("/kv/put", s.handlePut)
	mux.HandleFunc("/kv/get", s.handleGet)
	mux.HandleFunc("/kv/delete", s.handleDelete)
	mux.HandleFunc("/cluster", s.handleCluster)
	mux.HandleFunc("/cluster/add", s.handleClusterAdd)
	mux.HandleFunc("/cluster/remove", s.handleClusterRemove)
	return withAPIHeaders(mux)
}

func (s *HTTPServer) rpcMux() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("/raft/request_vote", s.handleRequestVote)
	mux.HandleFunc("/raft/append_entries", s.handleAppendEntries)
	mux.HandleFunc("/raft/install_snapshot", s.handleInstallSnapshot)
	return mux
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(value); err != nil {
		log.Printf("write json response failed: %v", err)
	}
}

func methodAllowed(w http.ResponseWriter, r *http.Request, method string) bool {
	if r.Method == method {
		return true
	}
	writeJSON(w, http.StatusMethodNotAllowed, map[string]string{"error": "method not allowed"})
	return false
}

func withAPIHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		w.Header().Set("Access-Control-Max-Age", "600")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func (s *HTTPServer) handleUI(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path == "/ui" {
		http.Redirect(w, r, "/ui/", http.StatusMovedPermanently)
		return
	}
	if r.URL.Path != "/ui/" && r.URL.Path != "/ui/index.html" {
		http.NotFound(w, r)
		return
	}
	if r.Method != http.MethodGet && r.Method != http.MethodHead {
		w.Header().Set("Allow", "GET, HEAD, OPTIONS")
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	html, err := uiFS.ReadFile("static/ui.html")
	if err != nil {
		http.Error(w, "ui asset not found", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store")
	if r.Method == http.MethodHead {
		return
	}
	if _, err := w.Write([]byte(strings.TrimSpace(string(html)))); err != nil {
		log.Printf("write ui response failed: %v", err)
	}
}
