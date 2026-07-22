package kv

import "testing"

func TestStateMachinePutGetDelete(t *testing.T) {
	sm := NewStateMachine()

	if err := sm.Apply(Command{Op: OpPut, Key: "name", Value: "raft"}); err != nil {
		t.Fatalf("put failed: %v", err)
	}
	value, ok := sm.Get("name")
	if !ok || value != "raft" {
		t.Fatalf("expected name=raft, got value=%q ok=%v", value, ok)
	}

	if err := sm.Apply(Command{Op: OpDelete, Key: "name"}); err != nil {
		t.Fatalf("delete failed: %v", err)
	}
	if _, ok := sm.Get("name"); ok {
		t.Fatal("expected key to be deleted")
	}
}

func TestSnapshotRestore(t *testing.T) {
	sm := NewStateMachine()
	_ = sm.Apply(Command{Op: OpPut, Key: "a", Value: "1"})

	restored := NewStateMachine()
	restored.Restore(sm.Snapshot())

	value, ok := restored.Get("a")
	if !ok || value != "1" {
		t.Fatalf("expected restored value 1, got %q ok=%v", value, ok)
	}
}
