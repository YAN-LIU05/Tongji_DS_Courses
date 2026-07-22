package raft

func (n *RaftNode) lastLogIndexLocked() int {
	if len(n.log) == 0 {
		return n.snapshotIndex
	}
	return n.log[len(n.log)-1].Index
}

func (n *RaftNode) lastLogTermLocked() int {
	if len(n.log) == 0 {
		return n.snapshotTerm
	}
	return n.log[len(n.log)-1].Term
}

func (n *RaftNode) logOffsetLocked(index int) int {
	if len(n.log) == 0 {
		return -1
	}
	return index - n.log[0].Index
}

func (n *RaftNode) hasLogIndexLocked(index int) bool {
	offset := n.logOffsetLocked(index)
	return offset >= 0 && offset < len(n.log)
}

func (n *RaftNode) termAtLocked(index int) (int, bool) {
	offset := n.logOffsetLocked(index)
	if offset < 0 || offset >= len(n.log) {
		return 0, false
	}
	return n.log[offset].Term, true
}

func (n *RaftNode) entryAtLocked(index int) (LogEntry, bool) {
	offset := n.logOffsetLocked(index)
	if offset < 0 || offset >= len(n.log) {
		return LogEntry{}, false
	}
	return n.log[offset], true
}

func (n *RaftNode) entriesFromLocked(index int) []LogEntry {
	offset := n.logOffsetLocked(index)
	if offset < 0 {
		offset = 0
	}
	if offset > len(n.log) {
		offset = len(n.log)
	}
	return cloneEntries(n.log[offset:])
}

func (n *RaftNode) isCandidateLogUpToDateLocked(lastIndex, lastTerm int) bool {
	myTerm := n.lastLogTermLocked()
	if lastTerm != myTerm {
		return lastTerm > myTerm
	}
	return lastIndex >= n.lastLogIndexLocked()
}

func cloneEntries(entries []LogEntry) []LogEntry {
	cp := make([]LogEntry, len(entries))
	copy(cp, entries)
	return cp
}
