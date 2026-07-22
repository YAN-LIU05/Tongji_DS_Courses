package server

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func TestUIServesHTML(t *testing.T) {
	server := &HTTPServer{}
	req := httptest.NewRequest(http.MethodGet, "/ui/", nil)
	rec := httptest.NewRecorder()

	server.handleUI(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("GET /ui/ status=%d want=%d", rec.Code, http.StatusOK)
	}
	if got := rec.Header().Get("Content-Type"); !strings.Contains(got, "text/html") {
		t.Fatalf("GET /ui/ content type=%q, want html", got)
	}
	body := rec.Body.String()
	for _, want := range []string{"Raft KV Console", "/kv/put", "/kv/get", "/cluster/add"} {
		if !strings.Contains(body, want) {
			t.Fatalf("GET /ui/ body missing %q", want)
		}
	}
}

func TestAPIMuxHandlesCORSPreflight(t *testing.T) {
	server := &HTTPServer{}
	req := httptest.NewRequest(http.MethodOptions, "/kv/put", nil)
	req.Header.Set("Origin", "http://127.0.0.1:8001")
	req.Header.Set("Access-Control-Request-Method", "POST")
	req.Header.Set("Access-Control-Request-Headers", "Content-Type")
	rec := httptest.NewRecorder()

	server.apiMux().ServeHTTP(rec, req)

	if rec.Code != http.StatusNoContent {
		t.Fatalf("OPTIONS /kv/put status=%d want=%d", rec.Code, http.StatusNoContent)
	}
	if got := rec.Header().Get("Access-Control-Allow-Origin"); got != "*" {
		t.Fatalf("allow origin=%q want *", got)
	}
	if got := rec.Header().Get("Access-Control-Allow-Methods"); !strings.Contains(got, "POST") {
		t.Fatalf("allow methods=%q missing POST", got)
	}
}

func TestUIServedByRunningNode(t *testing.T) {
	cluster := startTestCluster(t, 3, 64)
	leader := cluster.waitForLeader(t, 6*time.Second)

	resp, err := cluster.client.Get("http://" + leader.LeaderAddr + "/ui/")
	if err != nil {
		t.Fatalf("GET /ui/ from running node failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /ui/ from running node status=%d want=%d", resp.StatusCode, http.StatusOK)
	}
	if got := resp.Header.Get("Content-Type"); !strings.Contains(got, "text/html") {
		t.Fatalf("GET /ui/ from running node content type=%q, want html", got)
	}
}
