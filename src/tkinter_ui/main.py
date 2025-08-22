import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import json
import os
from pathlib import Path
from datetime import datetime

class UIA_Recorder_UI:
    def __init__(self, root):
        self.root = root
        self.root.title("OkBot UIA Recorder")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Recording state
        self.is_recording = False
        self.recording_process = None
        self.event_count = 0
        self.start_time = None
        
        # File paths
        self.uia_project_path = Path(__file__).parent.parent / "uia_listener"
        self.output_path = Path(__file__).parent.parent / "create_json_schema" / "resources" / "uia_log.json"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="OkBot UIA Event Recorder", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Recording controls
        controls_frame = ttk.LabelFrame(main_frame, text="Recording Controls", padding="10")
        controls_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Start/Stop button
        self.record_button = ttk.Button(controls_frame, text="Start Recording", 
                                       command=self.toggle_recording, style='Accent.TButton')
        self.record_button.grid(row=0, column=0, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(controls_frame, text="Ready to record", 
                                     font=('Arial', 10))
        self.status_label.grid(row=0, column=1, padx=(10, 0))
        
        # Recording info frame
        info_frame = ttk.LabelFrame(main_frame, text="Recording Information", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Event count
        ttk.Label(info_frame, text="Events Captured:").grid(row=0, column=0, sticky=tk.W)
        self.event_count_label = ttk.Label(info_frame, text="0", font=('Arial', 12, 'bold'))
        self.event_count_label.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        # Recording time
        ttk.Label(info_frame, text="Recording Time:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.time_label = ttk.Label(info_frame, text="00:00:00", font=('Arial', 12, 'bold'))
        self.time_label.grid(row=1, column=1, padx=(10, 0), sticky=tk.W, pady=(10, 0))
        
        # Output file path
        ttk.Label(info_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.file_path_label = ttk.Label(info_frame, text=str(self.output_path), 
                                        font=('Arial', 9), foreground='blue')
        self.file_path_label.grid(row=2, column=1, padx=(10, 0), sticky=tk.W, pady=(10, 0))
        
        # Live preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Live Event Preview", padding="10")
        preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Preview text area
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=15, width=80)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure preview frame grid weights
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=(20, 0))
        
        # Clear preview button
        clear_button = ttk.Button(buttons_frame, text="Clear Preview", 
                                 command=self.clear_preview)
        clear_button.grid(row=0, column=0, padx=(0, 10))
        
        # Open output folder button
        open_folder_button = ttk.Button(buttons_frame, text="Open Output Folder", 
                                       command=self.open_output_folder)
        open_folder_button.grid(row=0, column=1, padx=(0, 10))
        
        # View log button
        view_log_button = ttk.Button(buttons_frame, text="View Log File", 
                                    command=self.view_log_file)
        view_log_button.grid(row=0, column=2)
        
        # Start update timer
        self.update_timer()
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        try:
            # Check if UIA project exists
            if not self.uia_project_path.exists():
                messagebox.showerror("Error", f"UIA project not found at: {self.uia_project_path}")
                return
            
            # Build the project first
            build_result = subprocess.run(
                ["dotnet", "build"],
                cwd=self.uia_project_path,
                capture_output=True,
                text=True
            )
            
            if build_result.returncode != 0:
                messagebox.showerror("Build Error", f"Failed to build UIA project:\n{build_result.stderr}")
                return
            
            # Start the UIA listener
            exe_path = self.uia_project_path / "bin" / "Debug" / "net8.0-windows" / "okbot_uia_listener.exe"
            
            if not exe_path.exists():
                messagebox.showerror("Error", f"UIA listener executable not found at: {exe_path}")
                return
            
            # Start the process with creation flags to allow signal handling
            startupinfo = None
            creation_flags = 0
            
            if hasattr(subprocess, 'STARTUPINFO'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # On Windows, create a new process group to allow proper signal handling
            if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP'):
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
            
            # Start the process
            self.recording_process = subprocess.Popen(
                [str(exe_path)],
                cwd=self.uia_project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startupinfo,
                creationflags=creation_flags
            )
            
            # Backup existing log file if it exists
            if self.output_path.exists():
                try:
                    backup_path = self.output_path.parent / f"uia_log_backup_{int(time.time())}.json"
                    import shutil
                    shutil.copy2(self.output_path, backup_path)
                    self.preview_text.insert(tk.END, f"Backed up existing log to: {backup_path.name}\n")
                except Exception as e:
                    self.preview_text.insert(tk.END, f"Warning: Could not backup existing log: {str(e)}\n")
            
            self.is_recording = True
            self.start_time = time.time()
            self.event_count = 0
            
            # Update UI
            self.record_button.configure(text="Stop Recording", style='Danger.TButton')
            self.status_label.configure(text="Recording...", foreground='red')
            self.preview_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Recording started\n")
            self.preview_text.see(tk.END)
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self.monitor_process, daemon=True)
            self.monitor_thread.start()
            
            # Also start a thread to monitor stderr for any errors
            self.error_monitor_thread = threading.Thread(target=self.monitor_errors, daemon=True)
            self.error_monitor_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")
    
    def stop_recording(self):
        if self.recording_process:
            try:
                # Try to send Ctrl+C signal first (this allows the UIA listener to save the log)
                if hasattr(self.recording_process, 'send_signal'):
                    import signal
                    try:
                        # On Windows, try to send CTRL_C_EVENT
                        self.recording_process.send_signal(signal.CTRL_C_EVENT)
                        self.preview_text.insert(tk.END, "Sent Ctrl+C signal to UIA listener...\n")
                        
                        # Give the process time to handle the signal
                        time.sleep(2)
                        
                    except (AttributeError, OSError):
                        # Fallback to terminate
                        self.recording_process.terminate()
                        self.preview_text.insert(tk.END, "Sent terminate signal to UIA listener...\n")
                else:
                    # Fallback for systems without send_signal
                    self.recording_process.terminate()
                    self.preview_text.insert(tk.END, "Sent terminate signal to UIA listener...\n")
                
                # Wait for the process to finish gracefully
                try:
                    self.recording_process.wait(timeout=15)  # Give more time for graceful shutdown
                    self.preview_text.insert(tk.END, "UIA listener stopped gracefully.\n")
                except subprocess.TimeoutExpired:
                    # If it doesn't respond to signals, force kill
                    self.preview_text.insert(tk.END, "Process didn't respond to signals, force killing...\n")
                    self.recording_process.kill()
                    self.recording_process.wait(timeout=5)
                    self.preview_text.insert(tk.END, "UIA listener force killed.\n")
                
            except Exception as e:
                self.preview_text.insert(tk.END, f"Error stopping process: {str(e)}\n")
                # Force kill as last resort
                try:
                    self.recording_process.kill()
                    self.preview_text.insert(tk.END, "UIA listener force killed as last resort.\n")
                except:
                    pass
            finally:
                self.recording_process = None
        
        self.is_recording = False
        
        # Update UI
        self.record_button.configure(text="Start Recording", style='Accent.TButton')
        self.status_label.configure(text="Recording stopped", foreground='black')
        
        # Show final stats
        duration = time.time() - self.start_time if self.start_time else 0
        self.preview_text.insert(tk.END, f"\n[{datetime.now().strftime('%H:%M:%S')}] Recording stopped\n")
        self.preview_text.insert(tk.END, f"Total events captured: {self.event_count}\n")
        self.preview_text.insert(tk.END, f"Total recording time: {duration:.1f} seconds\n")
        self.preview_text.see(tk.END)
        
        # Check if log file was created
        self.preview_text.insert(tk.END, f"\nChecking for log file at: {self.output_path}\n")
        
        # Wait a moment for the file to be written
        time.sleep(2)  # Give more time for file writing
        
        # Check if the output directory exists
        output_dir = self.output_path.parent
        if output_dir.exists():
            self.preview_text.insert(tk.END, f"✅ Output directory exists: {output_dir}\n")
        else:
            self.preview_text.insert(tk.END, f"❌ Output directory does not exist: {output_dir}\n")
        
        if self.output_path.exists():
            try:
                with open(self.output_path, 'r') as f:
                    data = json.load(f)
                    actual_count = len(data) if isinstance(data, list) else 0
                    self.preview_text.insert(tk.END, f"✅ Events saved to log file: {actual_count}\n")
                    
                    # Check if this is a new log file or if we should merge with existing data
                    if actual_count > 0 and actual_count != self.event_count:
                        self.preview_text.insert(tk.END, f"Note: UIA listener created new log file (overwrote previous data)\n")
                        self.preview_text.insert(tk.END, f"Previous events may have been lost. Check backup files.\n")
                    
                    self.preview_text.see(tk.END)
            except Exception as e:
                self.preview_text.insert(tk.END, f"❌ Error reading log file: {str(e)}\n")
                self.preview_text.see(tk.END)
        else:
            self.preview_text.insert(tk.END, f"❌ Log file not found at: {self.output_path}\n")
            self.preview_text.insert(tk.END, "This usually means the UIA listener didn't save the file properly.\n")
            
            # Try to create a basic log file with the events we captured
            try:
                self.preview_text.insert(tk.END, "Attempting to create a basic log file...\n")
                
                # Ensure the output directory exists
                output_dir = self.output_path.parent
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Create a basic log structure with the events we captured
                basic_log = []
                for i in range(self.event_count):
                    basic_log.append({
                        "EventType": "Captured",
                        "TimestampUtc": datetime.now().isoformat() + "Z",
                        "ControlType": "ControlType.Unknown",
                        "Name": f"Event_{i+1}",
                        "ClassName": "Unknown",
                        "ProcessId": -1,
                        "Note": "Event captured by OkBot UI but UIA listener log not available"
                    })
                
                # Write the basic log file
                with open(self.output_path, 'w') as f:
                    json.dump(basic_log, f, indent=2)
                
                self.preview_text.insert(tk.END, f"✅ Created basic log file with {len(basic_log)} events\n")
                self.preview_text.insert(tk.END, "Note: This is a fallback log. For full UIA details, check UIA listener.\n")
                
            except Exception as e:
                self.preview_text.insert(tk.END, f"❌ Failed to create fallback log: {str(e)}\n")
                self.preview_text.insert(tk.END, "Try running the UIA listener manually to test.\n")
            
            self.preview_text.see(tk.END)
        
        messagebox.showinfo("Recording Complete", 
                           f"Recording stopped!\n\nEvents captured: {self.event_count}\n"
                           f"Duration: {duration:.1f} seconds\n\n"
                           f"Log file status: {'✅ Found' if self.output_path.exists() else '❌ Not found'}")
    
    def monitor_errors(self):
        """Monitor the UIA process stderr for any error messages"""
        if not self.recording_process:
            return
        
        try:
            while self.recording_process and self.recording_process.poll() is None:
                # Read error output line by line
                line = self.recording_process.stderr.readline()
                if line:
                    line = line.strip()
                    if line:
                        # Add error messages to preview with error prefix
                        self.root.after(0, lambda l=line: self.preview_text.insert(tk.END, f"[ERROR] {l}\n"))
                
                time.sleep(0.1)
                
        except Exception as e:
            error_msg = f"Error monitor error: {str(e)}"
            self.root.after(0, lambda: self.preview_text.insert(tk.END, f"[ERROR] {error_msg}\n"))
    
    def monitor_process(self):
        """Monitor the UIA process output and update event count"""
        if not self.recording_process:
            return
        
        try:
            while self.recording_process and self.recording_process.poll() is None:
                # Read output line by line
                line = self.recording_process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        # Update event count based on event markers
                        if any(event_type in line for event_type in ['[Focus]', '[Invoke]', '[Structure]', '[PropertyChanged]']):
                            self.event_count += 1
                            # Update the event count label in the UI
                            self.root.after(0, self.update_event_count)
                        
                        # Add to preview (limit lines to avoid memory issues)
                        self.root.after(0, self.add_to_preview, line)
                
                time.sleep(0.1)
                
        except Exception as e:
            error_msg = f"Monitor error: {str(e)}"
            self.root.after(0, lambda: self.preview_text.insert(tk.END, f"{error_msg}\n"))
    
    def update_event_count(self):
        """Update the event count label in the UI"""
        self.event_count_label.configure(text=str(self.event_count))
    
    def add_to_preview(self, line):
        """Add a line to the preview text area"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.preview_text.insert(tk.END, f"[{timestamp}] {line}\n")
        
        # Keep only last 1000 lines to prevent memory issues
        lines = self.preview_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.preview_text.delete("1.0", f"{len(lines) - 1000}.0")
        
        self.preview_text.see(tk.END)
    
    def clear_preview(self):
        """Clear the preview text area"""
        self.preview_text.delete("1.0", tk.END)
    
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        try:
            output_dir = self.output_path.parent
            if output_dir.exists():
                os.startfile(str(output_dir))
            else:
                messagebox.showwarning("Warning", f"Output directory does not exist: {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open output folder: {str(e)}")
    
    def view_log_file(self):
        """Open the log file in default text editor"""
        try:
            if self.output_path.exists():
                os.startfile(str(self.output_path))
            else:
                messagebox.showwarning("Warning", "Log file does not exist yet. Start recording first.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log file: {str(e)}")
    
    def update_timer(self):
        """Update the recording time display"""
        if self.is_recording and self.start_time:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.time_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Schedule next update
        self.root.after(1000, self.update_timer)
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_recording:
            if messagebox.askyesno("Recording Active", 
                                 "Recording is currently active. Stop recording before closing?"):
                self.stop_recording()
            else:
                return
        
        self.root.destroy()

def main():
    root = tk.Tk()
    
    # Configure styles
    style = ttk.Style()
    style.configure('Accent.TButton', background='#0078d4', foreground='white')
    style.configure('Danger.TButton', background='#d13438', foreground='white')
    
    app = UIA_Recorder_UI(root)
    
    # Set up closing handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
