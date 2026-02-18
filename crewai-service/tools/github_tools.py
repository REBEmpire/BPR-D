"""
Agent-facing GitHub tools for BPR&D meeting service.
Provides the "virtual filesystem" interface for agents to read/write files
before they are atomically committed at the end of the session.
"""

import logging
import re
from typing import Dict, List, Tuple

from tools import github_tool

logger = logging.getLogger(__name__)


async def read_file_tool(path: str, staged_changes: Dict[str, str]) -> str:
    """
    Read a file, preferring the staged version if it exists.
    """
    if path in staged_changes:
        return f"[Reading from Staged Changes]\n{staged_changes[path]}"

    # Fallback to GitHub
    content = await github_tool.read_file(path)
    return content


async def write_file_tool(path: str, content: str, staged_changes: Dict[str, str]) -> str:
    """
    Stage a file for writing. Does NOT commit immediately.
    """
    staged_changes[path] = content
    return f"Successfully staged changes for '{path}'."


async def list_files_tool(path: str) -> str:
    """
    List files in a directory (wraps github_tool.read_file).
    """
    # github_tool.read_file handles directory listings if path is a dir
    return await github_tool.read_file(path)


def get_tool_definitions() -> str:
    """
    Return the XML tool definitions for the agent's system prompt.
    """
    return """
<tools>
    <tool name="read_file">
        <description>Read the content of a file from the repository.</description>
        <parameters>
            <parameter name="path" type="string" description="Path to the file (e.g., 'README.md')"/>
        </parameters>
        <example>
            <execute_tool name="read_file">
                <path>docs/guide.md</path>
            </execute_tool>
        </example>
    </tool>

    <tool name="write_file">
        <description>Write content to a file. Overwrites if exists. Content is staged and committed at the end.</description>
        <parameters>
            <parameter name="path" type="string" description="Path to the file"/>
            <parameter name="content" type="string" description="The full content to write"/>
        </parameters>
        <example>
            <execute_tool name="write_file">
                <path>notes/session.md</path>
                <content># Session Notes...</content>
            </execute_tool>
        </example>
    </tool>

    <tool name="list_files">
        <description>List files and directories in a given path.</description>
        <parameters>
            <parameter name="path" type="string" description="Directory path (e.g., '.' for root)"/>
        </parameters>
        <example>
            <execute_tool name="list_files">
                <path>crewai-service/agents</path>
            </execute_tool>
        </example>
    </tool>

    <tool name="done">
        <description>Signal that you have completed your tasks for this session.</description>
        <parameters />
        <example>
            <execute_tool name="done" />
        </example>
    </tool>
</tools>
"""


def parse_tool_calls(content: str) -> List[Tuple[str, Dict[str, str]]]:
    """
    Parse XML tool calls from the agent's response.
    Returns a list of (tool_name, parameters_dict).

    Supported format:
    <execute_tool name="tool_name">
        <param_name>param_value</param_name>
        ...
    </execute_tool>
    """
    tool_calls = []

    # Regex to find <execute_tool> blocks
    # dotall=True so . matches newlines
    tool_pattern = re.compile(r'<execute_tool\s+name="([^"]+)">\s*(.*?)\s*</execute_tool>', re.DOTALL)

    # Regex to find parameters inside the block
    param_pattern = re.compile(r'<([^>]+)>\s*(.*?)\s*</\1>', re.DOTALL)

    for match in tool_pattern.finditer(content):
        tool_name = match.group(1)
        params_block = match.group(2)

        params = {}
        for p_match in param_pattern.finditer(params_block):
            p_name = p_match.group(1)
            p_value = p_match.group(2).strip()
            params[p_name] = p_value

        tool_calls.append((tool_name, params))

    return tool_calls
