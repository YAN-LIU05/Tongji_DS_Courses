package raft

import (
	"math/rand"
	"time"
)

func (n *RaftNode) electionLoop() {
	for {
		timeout := n.randomElectionTimeout()
		timer := time.NewTimer(timeout)

		select {
		case <-timer.C:
			n.mu.Lock()
			role := n.role
			n.mu.Unlock()
			if role != Leader {
				go n.startElection()
			}
		case <-n.resetElectionCh:
			if !timer.Stop() {
				select {
				case <-timer.C:
				default:
				}
			}
		case <-n.stopCh:
			timer.Stop()
			return
		}
	}
}

func (n *RaftNode) randomElectionTimeout() time.Duration {
	delta := n.electionMax - n.electionMin
	if delta <= 0 {
		return n.electionMin
	}
	return n.electionMin + time.Duration(rand.Int63n(int64(delta)))
}

func (n *RaftNode) signalElectionReset() {
	select {
	case n.resetElectionCh <- struct{}{}:
	default:
	}
}

func (n *RaftNode) heartbeatLoop(term int) {
	n.broadcastAppendEntries()

	ticker := time.NewTicker(n.heartbeatInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			n.mu.Lock()
			active := n.role == Leader && n.currentTerm == term
			n.mu.Unlock()
			if !active {
				return
			}
			n.broadcastAppendEntries()
		case <-n.stopCh:
			return
		}
	}
}
