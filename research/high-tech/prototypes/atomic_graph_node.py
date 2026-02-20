import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json

# Mock embedding function
def mock_embed(text: str) -> List[float]:
    # Simulate a 128-dim vector
    return [0.1 * len(text) % 1.0] * 128

@dataclass
class AtomicNode:
    """
    Represents an Atomic Skill Node in the GraphRAG system.
    """
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    inputs: Dict[str, str] = field(default_factory=dict)
    outputs: Dict[str, str] = field(default_factory=dict)
    execution_path: Optional[str] = None
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def generate_embedding(self):
        """Generates vector embedding for the node description."""
        content = f"{self.name}: {self.description} Inputs: {json.dumps(self.inputs)} Outputs: {json.dumps(self.outputs)}"
        self.embedding = mock_embed(content)
        return self.embedding

    def to_graph_node(self) -> Dict[str, Any]:
        """Serializes to graph-ready dictionary."""
        return {
            "id": self.node_id,
            "label": "Skill",
            "properties": {
                "name": self.name,
                "description": self.description,
                "inputs": json.dumps(self.inputs),
                "outputs": json.dumps(self.outputs),
                "execution_path": self.execution_path,
                "vector": self.embedding
            }
        }

class SkillGraphManager:
    def __init__(self):
        self.nodes: Dict[str, AtomicNode] = {}

    def register_skill(self, name: str, description: str, inputs: Dict, outputs: Dict, exec_path: str):
        node = AtomicNode(
            name=name,
            description=description,
            inputs=inputs,
            outputs=outputs,
            execution_path=exec_path
        )
        node.generate_embedding()
        self.nodes[node.node_id] = node
        print(f"Registered Atomic Skill: {name} ({node.node_id})")
        return node

if __name__ == "__main__":
    manager = SkillGraphManager()

    # Define a skill: "Web Search"
    search_skill = manager.register_skill(
        name="WebSearch",
        description="Searches the internet for a given query and returns top results.",
        inputs={"query": "string", "num_results": "int"},
        outputs={"results": "List[Dict]"},
        exec_path="tools.search.execute"
    )

    # Define a skill: "Summarize"
    summary_skill = manager.register_skill(
        name="SummarizeText",
        description="Condenses a long text into a short summary.",
        inputs={"text": "string", "max_length": "int"},
        outputs={"summary": "string"},
        exec_path="tools.llm.summarize"
    )

    # Simulate retrieval
    print(f"\nGraph contains {len(manager.nodes)} atomic skills.")
    print(f"Sample Node (JSON): {json.dumps(search_skill.to_graph_node(), indent=2)}")
