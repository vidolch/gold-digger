#!/usr/bin/env python3
"""
Minimal test to debug button visibility in Gold Digger TUI.
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Container, Horizontal, Vertical

class TestLayoutApp(App):
    """Simple app to test button layout."""

    CSS = """
    Button {
        margin: 1;
        min-width: 20;
        height: 3;
        background: red;
        color: white;
        border: solid white;
        text-style: bold;
    }

    Button:hover {
        background: yellow;
        color: black;
    }

    .test-container {
        height: auto;
        margin: 1;
        border: solid green;
        padding: 1;
    }

    .button-row {
        height: 5;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Static("🧪 Button Visibility Test", classes="title"),

            Static("Row 1: Horizontal Layout"),
            Container(
                Horizontal(
                    Button("Button 1", id="btn1"),
                    Button("Button 2", id="btn2"),
                    Button("Button 3", id="btn3"),
                ),
                classes="test-container button-row"
            ),

            Static("Row 2: Vertical Layout"),
            Container(
                Vertical(
                    Button("Button A", id="btnA"),
                    Button("Button B", id="btnB"),
                    Button("Button C", id="btnC"),
                ),
                classes="test-container"
            ),

            Static("Row 3: Simple Container"),
            Container(
                Button("Simple Button 1", id="simple1"),
                Button("Simple Button 2", id="simple2"),
                classes="test-container button-row"
            ),
        )

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        self.notify(f"Button pressed: {event.button.label}")

if __name__ == "__main__":
    app = TestLayoutApp()
    app.run()
