package kv

import (
	"errors"
	"sync"
)

var (
	ErrEmptyKey  = errors.New("key is empty")
	ErrUnknownOp = errors.New("unknown command operation")
)

type StateMachine struct {
	mu   sync.RWMutex
	data map[string]string
}

func NewStateMachine() *StateMachine {
	return &StateMachine{data: make(map[string]string)}
}

func (s *StateMachine) Apply(cmd Command) error {
	if cmd.Key == "" {
		return ErrEmptyKey
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	switch cmd.Op {
	case OpPut:
		s.data[cmd.Key] = cmd.Value
	case OpDelete:
		delete(s.data, cmd.Key)
	default:
		return ErrUnknownOp
	}
	return nil
}

func (s *StateMachine) Get(key string) (string, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	value, ok := s.data[key]
	return value, ok
}

func (s *StateMachine) Snapshot() map[string]string {
	s.mu.RLock()
	defer s.mu.RUnlock()

	cp := make(map[string]string, len(s.data))
	for key, value := range s.data {
		cp[key] = value
	}
	return cp
}

func (s *StateMachine) Restore(snapshot map[string]string) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.data = make(map[string]string, len(snapshot))
	for key, value := range snapshot {
		s.data[key] = value
	}
}

func (s *StateMachine) Size() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.data)
}
