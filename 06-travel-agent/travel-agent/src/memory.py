from typing import Dict, Any

class Memory:
    def __init__(self):
        self.memory: Dict[str, Any] = {}

    def remember(self, key: str, value: Any) -> None:
        """Store a value in memory with the associated key."""
        self.memory[key] = value

    def recall(self, key: str) -> Any:
        """Retrieve a value from memory using the associated key."""
        return self.memory.get(key, None)

    def clear_memory(self) -> None:
        """Clear all stored memory."""
        self.memory.clear()