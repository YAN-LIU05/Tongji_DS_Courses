package main

import (
	"context"
	"flag"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"raft-kv/raft"
	"raft-kv/server"
)

func main() {
	id := flag.Int("id", 0, "node id in cluster config")
	configPath := flag.String("config", "config/cluster.json", "cluster config path")
	flag.Parse()

	if *id == 0 {
		log.Fatal("missing --id")
	}

	cfg, err := raft.LoadClusterConfig(*configPath)
	if err != nil {
		log.Fatalf("load cluster config failed: %v", err)
	}

	node, err := raft.NewRaftNode(*id, cfg.Nodes)
	if err != nil {
		log.Fatalf("create raft node failed: %v", err)
	}

	httpServer := server.NewHTTPServer(node)
	errCh := httpServer.Start()
	node.Start()

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)

	select {
	case sig := <-sigCh:
		log.Printf("[node %d] receive signal %s, shutting down", node.ID(), sig)
	case err := <-errCh:
		log.Printf("[node %d] server error: %v", node.ID(), err)
	}

	node.Stop()
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	if err := httpServer.Shutdown(ctx); err != nil {
		log.Printf("[node %d] shutdown server failed: %v", node.ID(), err)
	}
}
