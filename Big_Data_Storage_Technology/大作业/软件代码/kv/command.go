package kv

const (
	OpPut        = "Put"
	OpDelete     = "Delete"
	OpAddNode    = "AddNode"
	OpRemoveNode = "RemoveNode"
)

type Command struct {
	Op    string `json:"op"`
	Key   string `json:"key"`
	Value string `json:"value,omitempty"`
}
