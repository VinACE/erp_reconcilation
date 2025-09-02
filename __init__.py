# /home/vinsentparamanantham/erp/agents/__init__.py
import asyncio
from .context import RunnerContext


class Agent:
    def __init__(self, name=None, instructions=None, model=None, **kwargs):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.extra = kwargs


class RunnerResult:
    def __init__(self, output_text, steps=None):
        self.output_text = output_text
        self.steps = steps or []


class Step:
    def __init__(self, step_type, tool_call=None, output=None):
        self.type = step_type
        self.tool_call = tool_call
        self.output = output


class Runner:
    @staticmethod
    async def run(agent: Agent, prompt: str, context: RunnerContext = None):
        steps = []

        if not context or "servers" not in context.mcp_config:
            return RunnerResult(
                output_text="No MCP servers defined in RunnerContext.",
                steps=[]
            )

        # For now, just handle the first server in the config
        for server_name, server_info in context.mcp_config["servers"].items():
            cmd = [server_info["command"]] + server_info.get("args", [])
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()

                if stdout:
                    steps.append(Step("tool_call", tool_call=server_name, output=stdout.decode()))
                if stderr:
                    steps.append(Step("error", tool_call=server_name, output=stderr.decode()))
            except Exception as e:
                steps.append(Step("error", tool_call=server_name, output=str(e)))

        # Build output_text by combining steps
        output_summary = f"[{agent.name}] executed with model={agent.model}\nPrompt: {prompt}\n\n"
        for s in steps:
            output_summary += f"\nStep: {s.type}\nTool: {s.tool_call}\nOutput:\n{s.output}\n"

        return RunnerResult(output_text=output_summary, steps=steps)
