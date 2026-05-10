import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

load_dotenv()

from src.agents.supervisor_agent import supervisor_agent

console = Console()


def main():
    parser = argparse.ArgumentParser(description="ITP Multi-Agent Clinical Decision Support")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--note", type=str, help="Clinical note as inline string")
    group.add_argument("--note-file", type=str, help="Path to clinical note .txt file")
    args = parser.parse_args()

    if args.note:
        note = args.note
    else:
        note_path = Path(args.note_file)
        if not note_path.exists():
            console.print(f"[red]Error: file not found: {note_path}[/red]")
            sys.exit(1)
        note = note_path.read_text(encoding="utf-8")

    try:
        for chunk in supervisor_agent.stream({"content": note}):
            if "data" in chunk:
                console.print(chunk["data"], end="", highlight=False)
        console.print()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
