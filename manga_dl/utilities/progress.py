"""Progress bar helper."""
from rich.progress import BarColumn
from rich.progress import Progress as RichProgress
from rich.progress import (
    ProgressColumn,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.text import Text


class CustomTransferSpeedColumn(ProgressColumn):
    """Renders human readable transfer speed."""

    def render(self, task) -> Text:
        """Show data transfer speed."""
        speed = task.fields.get("speed")
        if speed is None:
            return Text("?", style="progress.data.speed", justify="center")
        return Text(
            f"{speed} Kb/s",
            style="progress.data.speed",
            justify="center",
        )


class Progress:
    """Progress bar helper."""

    def __init__(self):
        self.progress = RichProgress(
            TextColumn("{task.description}", justify="left"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.2f}%",
            "•",
            SpinnerColumn(style="progress.data.speed"),
            CustomTransferSpeedColumn(),
            "•",
            TextColumn(
                "[green]{task.completed:>02d}[/]/[bold green]{task.fields[rendered_total]}[/]",
                justify="left",
            ),
            SpinnerColumn(),
            "•",
            TimeRemainingColumn(),
            transient=False,
            refresh_per_second=20,
        )

    def add_task(self, description, total):
        """Add a new task to the progress bar."""
        return self.progress.add_task(
            description, total=total, rendered_total=total, speed=""
        )

    def update(self, taskId, advance):
        """Update the progress bar."""
        self.progress.update(taskId, advance=advance)

    def remove_task(self, taskId):
        """Mark a task as completed and hide it."""
        self.progress.stop_task(taskId)
        self.progress.tasks[taskId].visible = False

    def exit(self):
        """Send exit signal to the progress bar."""
        progress = RichProgress()
        progress.console.print("[bold red]Stopping Download[/]...")
        progress.console.print("[red]Download Stopped[/]!")
        progress.console.print("")
