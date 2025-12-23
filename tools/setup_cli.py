#!/usr/bin/env python3
"""
LeRobot Setup CLI Tool - Interactive TUI with arrow keys and mouse support
Supports: Windows PowerShell, CMD, Linux, MacOS
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Optional, List

# Auto-install textual if not available
try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Vertical, Horizontal
    from textual.widgets import Header, Footer, Button, Static, Label, Input, Checkbox, Select
    from textual.binding import Binding
    from textual.screen import Screen
except ImportError:
    print("Installing required package 'textual'...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "textual", "-q"])
        from textual.app import App, ComposeResult
        from textual.containers import Container, Vertical, Horizontal
        from textual.widgets import Header, Footer, Button, Static, Label, Input, Checkbox, Select
        from textual.binding import Binding
        from textual.screen import Screen
    except Exception as e:
        print(f"Error installing 'textual': {e}")
        print("Please run: pip install textual")
        sys.exit(1)

CONFIG_FILE = Path.home() / ".lerobot_setup_config.json"


class ConfigManager:
    """Manage configuration loading and saving"""
    
    @staticmethod
    def load_config() -> dict:
        """Load saved configuration from disk"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "leader_port": "",
            "leader_id": "Leader",
            "leader_type": "so101_leader",
            "follower_port": "",
            "follower_id": "Follower",
            "follower_type": "so101_follower",
            "cameras": [],
            "steps_completed": []
        }
    
    @staticmethod
    def save_config(config: dict):
        """Save configuration to disk"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")


class CommandRunner:
    """Handle command execution with error handling"""
    
    @staticmethod
    def run_command(command: str, interactive: bool = False) -> tuple[bool, str]:
        """
        Run a shell command with comprehensive error handling
        Returns: (success: bool, output: str)
        """
        try:
            if interactive:
                # For interactive commands - let user interact directly
                result = subprocess.run(command, shell=True)
                return result.returncode == 0, ""
            else:
                # For non-interactive commands
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                output = result.stdout if result.stdout else result.stderr
                return result.returncode == 0, output
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out (5 min limit)"
        except FileNotFoundError:
            return False, "Command not found. Is LeRobot installed?"
        except KeyboardInterrupt:
            return False, "Command interrupted by user"
        except Exception as e:
            return False, f"Unexpected error: {e}"


class PortConfigScreen(Screen):
    """Screen for configuring ports"""
    
    CSS = """
    PortConfigScreen {
        align: center middle;
    }
    
    #dialog {
        width: 70;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    Input {
        margin: 1 0;
    }
    
    Button {
        margin: 1 1;
    }
    """
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
    
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Port Configuration", id="title")
            yield Label("Leader Arm:")
            yield Input(placeholder="COM4 or /dev/ttyACM0", value=self.config.get("leader_port", ""), id="leader_port")
            yield Input(placeholder="Leader type", value=self.config.get("leader_type", "so101_leader"), id="leader_type")
            yield Input(placeholder="Leader ID", value=self.config.get("leader_id", "Leader"), id="leader_id")
            
            yield Label("Follower Arm:")
            yield Input(placeholder="COM3 or /dev/ttyACM1", value=self.config.get("follower_port", ""), id="follower_port")
            yield Input(placeholder="Follower type", value=self.config.get("follower_type", "so101_follower"), id="follower_type")
            yield Input(placeholder="Follower ID", value=self.config.get("follower_id", "Follower"), id="follower_id")
            
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="default", id="cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.config["leader_port"] = self.query_one("#leader_port", Input).value
            self.config["leader_type"] = self.query_one("#leader_type", Input).value
            self.config["leader_id"] = self.query_one("#leader_id", Input).value
            self.config["follower_port"] = self.query_one("#follower_port", Input).value
            self.config["follower_type"] = self.query_one("#follower_type", Input).value
            self.config["follower_id"] = self.query_one("#follower_id", Input).value
            ConfigManager.save_config(self.config)
            self.dismiss(True)
        else:
            self.dismiss(False)


class CameraConfigScreen(Screen):
    """Screen for configuring cameras"""
    
    CSS = """
    CameraConfigScreen {
        align: center middle;
    }
    
    #dialog {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    """
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.cameras = config.get("cameras", []).copy()
    
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Camera Configuration", id="title")
            
            if self.cameras:
                yield Label(f"Current cameras: {len(self.cameras)}")
                for idx, cam in enumerate(self.cameras):
                    yield Label(f"{idx+1}. {cam['name']}: {cam['type']}")
            
            yield Label("\nAdd Camera:")
            yield Input(placeholder="Camera name (e.g., front, wrist)", id="cam_name")
            yield Label("Type:")
            yield Select(
                [("OpenCV", "opencv"), ("Intel RealSense", "intelrealsense")],
                value="intelrealsense",
                id="cam_type"
            )
            yield Input(placeholder="Path/Index/Serial", id="cam_path")
            yield Input(placeholder="Width", value="640", id="cam_width")
            yield Input(placeholder="Height", value="480", id="cam_height")
            yield Input(placeholder="FPS", value="30", id="cam_fps")
            
            with Horizontal():
                yield Button("Add Camera", variant="success", id="add")
                yield Button("Save & Close", variant="primary", id="save")
                yield Button("Cancel", variant="default", id="cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add":
            cam_name = self.query_one("#cam_name", Input).value
            cam_type = self.query_one("#cam_type", Select).value
            cam_path = self.query_one("#cam_path", Input).value
            cam_width = self.query_one("#cam_width", Input).value
            cam_height = self.query_one("#cam_height", Input).value
            cam_fps = self.query_one("#cam_fps", Input).value
            
            if not cam_name or not cam_path:
                self.notify("Please fill in camera name and path/serial", severity="error")
                return
            
            camera = {
                "name": cam_name,
                "type": cam_type,
                "width": cam_width,
                "height": cam_height,
                "fps": cam_fps
            }
            
            if cam_type == "opencv":
                camera["path"] = cam_path
            else:
                camera["serial"] = cam_path
                camera["use_depth"] = True
            
            self.cameras.append(camera)
            self.notify(f"Camera '{cam_name}' added!", severity="information")
            
            # Clear inputs
            self.query_one("#cam_name", Input).value = ""
            self.query_one("#cam_path", Input).value = ""
            
        elif event.button.id == "save":
            self.config["cameras"] = self.cameras
            ConfigManager.save_config(self.config)
            self.dismiss(True)
        else:
            self.dismiss(False)


class LeRobotSetupApp(App):
    """Main LeRobot Setup Application"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main_container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 1 0;
    }
    
    #status {
        text-align: center;
        color: $text-muted;
        margin: 0 0 2 0;
    }
    
    .step-button {
        width: 100%;
        margin: 1 0;
        height: 3;
    }
    
    .completed {
        background: $success;
    }
    
    .info-panel {
        border: solid $primary;
        padding: 1;
        margin: 2 0;
        background: $boost;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "reset", "Reset Config"),
        Binding("c", "show_config", "Show Config"),
    ]
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager.load_config()
        self.steps_completed = set(self.config.get("steps_completed", []))
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Vertical(id="main_container"):
            yield Static("🤖 LeRobot Setup CLI", id="title")
            yield Static("Use arrow keys, mouse clicks, or shortcuts", id="status")
            
            # Info panel
            with Container(classes="info-panel"):
                leader_info = f"Leader: {self.config.get('leader_port', 'Not set')}"
                follower_info = f"Follower: {self.config.get('follower_port', 'Not set')}"
                camera_info = f"Cameras: {len(self.config.get('cameras', []))}"
                yield Static(f"{leader_info} | {follower_info} | {camera_info}", id="info")
            
            # Step buttons
            yield Button("1. Find Ports (Optional)", id="step_1", classes="step-button" + (" completed" if 1 in self.steps_completed else ""))
            yield Button("2. Setup Motors (Optional)", id="step_2", classes="step-button" + (" completed" if 2 in self.steps_completed else ""))
            yield Button("3. Calibrate Arms", id="step_3", classes="step-button" + (" completed" if 3 in self.steps_completed else ""))
            yield Button("4. Test Teleop (Basic)", id="step_4", classes="step-button" + (" completed" if 4 in self.steps_completed else ""))
            yield Button("5. Configure Cameras", id="step_5", classes="step-button" + (" completed" if 5 in self.steps_completed else ""))
            yield Button("6. Test Teleop (Cameras)", id="step_6", classes="step-button" + (" completed" if 6 in self.steps_completed else ""))
            
            # Action buttons
            with Horizontal():
                yield Button("⚙ Config Ports", id="config_ports", variant="primary")
                yield Button("📋 Show Config", id="show_config")
                yield Button("🔄 Reset", id="reset", variant="warning")
                yield Button("❌ Quit", id="quit", variant="error")
        
        yield Footer()
    
    def update_info(self):
        """Update the info panel"""
        leader_info = f"Leader: {self.config.get('leader_port', 'Not set')}"
        follower_info = f"Follower: {self.config.get('follower_port', 'Not set')}"
        camera_info = f"Cameras: {len(self.config.get('cameras', []))}"
        self.query_one("#info", Static).update(f"{leader_info} | {follower_info} | {camera_info}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "quit":
            self.exit()
        elif button_id == "reset":
            self.action_reset()
        elif button_id == "show_config":
            self.action_show_config()
        elif button_id == "config_ports":
            self.configure_ports()
        elif button_id.startswith("step_"):
            step_num = int(button_id.split("_")[1])
            self.run_step(step_num)
    
    def configure_ports(self):
        """Open port configuration screen"""
        def on_config_complete(result):
            if result:
                self.config = ConfigManager.load_config()
                self.update_info()
                self.notify("Port configuration saved!", severity="information")
        
        self.push_screen(PortConfigScreen(self.config), on_config_complete)
    
    def action_show_config(self):
        """Show current configuration"""
        config_text = f"""
Leader Port: {self.config.get('leader_port', 'Not set')}
Leader Type: {self.config.get('leader_type', 'Not set')}
Leader ID: {self.config.get('leader_id', 'Not set')}

Follower Port: {self.config.get('follower_port', 'Not set')}
Follower Type: {self.config.get('follower_type', 'Not set')}
Follower ID: {self.config.get('follower_id', 'Not set')}

Cameras: {len(self.config.get('cameras', []))}
"""
        if self.config.get('cameras'):
            config_text += "\nCamera Details:\n"
            for idx, cam in enumerate(self.config['cameras'], 1):
                config_text += f"  {idx}. {cam['name']}: {cam['type']}\n"
        
        self.notify(config_text, severity="information", timeout=10)
    
    def action_reset(self):
        """Reset configuration"""
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        self.config = ConfigManager.load_config()
        self.steps_completed.clear()
        self.update_info()
        self.notify("Configuration reset!", severity="warning")
        self.refresh()
    
    def ensure_ports_configured(self) -> bool:
        """Ensure ports are configured before running steps"""
        if not self.config.get("leader_port") or not self.config.get("follower_port"):
            self.notify("Please configure ports first! Click 'Config Ports' button.", severity="error")
            return False
        return True
    
    def run_step(self, step_num: int):
        """Run a specific step"""
        if step_num > 1 and not self.ensure_ports_configured():
            return
        
        # Suspend the app to run terminal commands
        with self.suspend():
            if step_num == 1:
                self.step_find_ports()
            elif step_num == 2:
                self.step_setup_motors()
            elif step_num == 3:
                self.step_calibrate()
            elif step_num == 4:
                self.step_test_teleop_basic()
            elif step_num == 5:
                self.step_configure_cameras()
            elif step_num == 6:
                self.step_test_teleop_cameras()
        
        # Update UI after step completes
        self.config = ConfigManager.load_config()
        self.steps_completed = set(self.config.get("steps_completed", []))
        self.update_info()
        self.refresh()
    
    def step_find_ports(self):
        """Step 1: Find ports"""
        print("\n" + "="*60)
        print("STEP 1: FIND PORTS")
        print("="*60)
        print("\nRunning lerobot-find-port to identify which port is which arm...")
        print("Follow the interactive prompts.\n")
        
        input("Press Enter to continue...")
        
        success, output = CommandRunner.run_command("lerobot-find-port", interactive=True)
        
        if not success:
            print("\n⚠ lerobot-find-port command not found or failed")
            print("Make sure LeRobot is installed and environment is activated\n")
        
        print("\nNow configure your ports in the app (click 'Config Ports' button)")
        input("\nPress Enter to return to app...")
    
    def step_setup_motors(self):
        """Step 2: Setup motors"""
        print("\n" + "="*60)
        print("STEP 2: SETUP MOTORS (OPTIONAL)")
        print("="*60)
        print("\n⚠ IMPORTANT:")
        print("• This step has likely been done already")
        print("• Only run if servos are not recognized")
        print("• Connect each motor INDIVIDUALLY (not daisy-chained)\n")
        
        choice = input("Do you need to setup motors? (y/n): ").lower()
        if choice != 'y':
            print("Skipping motor setup")
            self.steps_completed.add(2)
            self.config["steps_completed"] = list(self.steps_completed)
            ConfigManager.save_config(self.config)
            input("\nPress Enter to return to app...")
            return
        
        # Leader motors
        print("\n--- LEADER MOTORS ---")
        leader_cmd = (
            f"lerobot-setup-motors "
            f"--teleop.type={self.config['leader_type']} "
            f"--teleop.port={self.config['leader_port']}"
        )
        print(f"Command: {leader_cmd}\n")
        success_leader, output = CommandRunner.run_command(leader_cmd)
        print(output)
        
        # Follower motors
        print("\n--- FOLLOWER MOTORS ---")
        follower_cmd = (
            f"lerobot-setup-motors "
            f"--robot.type={self.config['follower_type']} "
            f"--robot.port={self.config['follower_port']}"
        )
        print(f"Command: {follower_cmd}\n")
        success_follower, output = CommandRunner.run_command(follower_cmd)
        print(output)
        
        if success_leader and success_follower:
            print("\n✓ Motor setup completed!")
            self.steps_completed.add(2)
            self.config["steps_completed"] = list(self.steps_completed)
            ConfigManager.save_config(self.config)
        
        input("\nPress Enter to return to app...")
    
    def step_calibrate(self):
        """Step 3: Calibrate arms"""
        print("\n" + "="*60)
        print("STEP 3: CALIBRATION")
        print("="*60)
        print("\nCalibration Process:")
        print("1. Move all 6 joints to their NEUTRAL CENTER positions")
        print("2. Press Enter when prompted")
        print("3. Move EACH joint slowly through its FULL range")
        print("4. Press Enter when requested")
        print("5. Calibration saves automatically\n")
        
        # Follower
        print("\n--- FOLLOWER ARM CALIBRATION ---")
        input("Press Enter when ready to calibrate follower arm...")
        follower_cmd = (
            f"lerobot-calibrate "
            f"--robot.type={self.config['follower_type']} "
            f"--robot.port={self.config['follower_port']} "
            f"--robot.id={self.config['follower_id']}"
        )
        print(f"Command: {follower_cmd}\n")
        CommandRunner.run_command(follower_cmd, interactive=True)
        
        # Leader
        print("\n--- LEADER ARM CALIBRATION ---")
        input("Press Enter when ready to calibrate leader arm...")
        leader_cmd = (
            f"lerobot-calibrate "
            f"--teleop.type={self.config['leader_type']} "
            f"--teleop.port={self.config['leader_port']} "
            f"--teleop.id={self.config['leader_id']}"
        )
        print(f"Command: {leader_cmd}\n")
        CommandRunner.run_command(leader_cmd, interactive=True)
        
        print("\n✓ Calibration completed!")
        self.steps_completed.add(3)
        self.config["steps_completed"] = list(self.steps_completed)
        ConfigManager.save_config(self.config)
        
        input("\nPress Enter to return to app...")
    
    def step_test_teleop_basic(self):
        """Step 4: Test basic teleoperation"""
        print("\n" + "="*60)
        print("STEP 4: TEST TELEOPERATION (BASIC)")
        print("="*60)
        print("\nMove the leader arm - follower should mirror movements")
        print("Press Ctrl+C to stop when done testing\n")
        
        input("Press Enter to start teleoperation...")
        
        teleop_cmd = (
            f"lerobot-teleoperate "
            f"--teleop.type={self.config['leader_type']} "
            f"--teleop.port={self.config['leader_port']} "
            f"--teleop.id={self.config['leader_id']} "
            f"--robot.type={self.config['follower_type']} "
            f"--robot.port={self.config['follower_port']} "
            f"--robot.id={self.config['follower_id']}"
        )
        print(f"Command: {teleop_cmd}\n")
        
        CommandRunner.run_command(teleop_cmd, interactive=True)
        
        print("\n✓ Teleoperation test completed!")
        self.steps_completed.add(4)
        self.config["steps_completed"] = list(self.steps_completed)
        ConfigManager.save_config(self.config)
        
        input("\nPress Enter to return to app...")
    
    def step_configure_cameras(self):
        """Step 5: Configure cameras"""
        def on_camera_config_complete(result):
            if result:
                self.config = ConfigManager.load_config()
                self.update_info()
                self.steps_completed.add(5)
                self.config["steps_completed"] = list(self.steps_completed)
                ConfigManager.save_config(self.config)
        
        self.push_screen(CameraConfigScreen(self.config), on_camera_config_complete)
    
    def build_camera_string(self) -> str:
        """Build camera configuration string"""
        if not self.config.get("cameras"):
            return ""
        
        cam_configs = []
        for cam in self.config["cameras"]:
            if cam["type"] == "opencv":
                config = (
                    f"{cam['name']}: {{type: opencv, "
                    f"index_or_path: {cam['path']}, "
                    f"width: {cam['width']}, height: {cam['height']}, fps: {cam['fps']}}}"
                )
            else:
                config = (
                    f"{cam['name']}: {{type: intelrealsense, "
                    f"serial_number_or_name: {cam['serial']}, "
                    f"width: {cam['width']}, height: {cam['height']}, fps: {cam['fps']}, "
                    f"use_depth: {str(cam.get('use_depth', True)).lower()}}}"
                )
            cam_configs.append(config)
        
        return '"{ ' + ', '.join(cam_configs) + ' }"'
    
    def step_test_teleop_cameras(self):
        """Step 6: Test teleoperation with cameras"""
        if not self.config.get("cameras"):
            print("\n⚠ No cameras configured")
            print("Please configure cameras first (Step 5)")
            input("\nPress Enter to return to app...")
            return
        
        print("\n" + "="*60)
        print("STEP 6: TEST TELEOPERATION WITH CAMERAS")
        print("="*60)
        print("\nCamera window should open. Move the leader arm!")
        print("Press Ctrl+C to stop when done testing\n")
        
        print("Cameras configured:")
        for cam in self.config["cameras"]:
            print(f"  • {cam['name']}: {cam['type']}")
        
        input("\nPress Enter to start teleoperation with cameras...")
        
        camera_str = self.build_camera_string()
        
        teleop_cmd = (
            f"lerobot-teleoperate "
            f"--robot.type={self.config['follower_type']} "
            f"--robot.port={self.config['follower_port']} "
            f"--robot.id={self.config['follower_id']} "
            f"--robot.cameras={camera_str} "
            f"--teleop.type={self.config['leader_type']} "
            f"--teleop.port={self.config['leader_port']} "
            f"--teleop.id={self.config['leader_id']} "
            f"--display_data=True"
        )
        print(f"Command: {teleop_cmd}\n")
        
        CommandRunner.run_command(teleop_cmd, interactive=True)
        
        print("\n✓ Camera teleoperation completed!")
        self.steps_completed.add(6)
        self.config["steps_completed"] = list(self.steps_completed)
        ConfigManager.save_config(self.config)
        
        input("\nPress Enter to return to app...")


def main():
    """Main entry point"""
    print("\n🤖 LeRobot Setup CLI v2.0")
    print("=" * 60)
    print("Checking LeRobot installation...")
    
    try:
        result = subprocess.run(
            "lerobot-calibrate --help",
            shell=True,
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            print("⚠ Warning: LeRobot commands may not be available")
            print("Make sure you've activated your LeRobot environment")
            choice = input("\nContinue anyway? (y/n): ")
            if choice.lower() != 'y':
                sys.exit(1)
    except Exception:
        print("⚠ Could not verify LeRobot installation")
    
    print("\n✓ Starting interactive TUI...")
    print("Use arrow keys, mouse clicks, or keyboard shortcuts\n")
    
    app = LeRobotSetupApp()
    app.run()


if __name__ == "__main__":
    main()