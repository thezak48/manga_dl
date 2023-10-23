"""Progress bar helper."""
from rich.progress import (
    BarColumn,
    Progress as RichProgress,
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
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("?", style="progress.data.speed", justify="center")
        return Text(
            f"{task.speed:2.0f} {task.fields.get('type')}/s",
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
        return self.progress.add_task(description, total=total, rendered_total=total)

    def update(self, task, advance):
        """Update the progress bar."""
        self.progress.update(task, advance=advance)
