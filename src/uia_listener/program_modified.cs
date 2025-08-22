/**
 * This program records UI Automation events from the user's desktop and persists them to a JSON file.
 * MODIFIED VERSION: Appends to existing log files instead of overwriting them.
 */

using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Threading;
using System.Windows.Automation;

internal static class Program
{
    // Optional: filter to the current foreground process only
    private static int _foregroundPidFilter = 0;

    // In-memory event log to persist on exit
    private static readonly List<LogEvent> _eventLog = new();
    private static readonly object _eventLogLock = new();

    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out int lpdwProcessId);

    [STAThread] // UIA callbacks work best with STA
    private static void Main(string[] args)
    {
        Console.WriteLine("UIA event listener starting...");
        Console.WriteLine("Press ENTER to toggle 'foreground app only' filter. Press Ctrl+C to exit.\n");

        // Ensure we also persist logs on process exit (in case of window close/shutdown)
        AppDomain.CurrentDomain.ProcessExit += (s, e) =>
        {
            try { WriteEventLogToJson(); } catch { }
        };

        // Start with no filter (listen to the whole desktop)
        SetForegroundPidFilter(enabled: false);

        // 1) Focus changed (fires when the user focuses a new control/window)
        Automation.AddAutomationFocusChangedEventHandler(OnFocusChanged);

        // 2) Invoked (e.g., button click via InvokePattern)
        Automation.AddAutomationEventHandler(
            InvokePattern.InvokedEvent,
            AutomationElement.RootElement,
            TreeScope.Subtree,
            OnInvoked);

        // 3) Structure changed (e.g., new windows/controls appear or disappear)
        Automation.AddAutomationEventHandler(
            AutomationElement.RootElement,
            TreeScope.Subtree,
            OnStructureChanged);

        // 4) Property changes (here we watch Name & IsOffscreen globally)
        Automation.AddAutomationPropertyChangedEventHandler(
            AutomationElement.RootElement,
            TreeScope.Subtree,
            OnPropertyChanged,
            AutomationElement.NameProperty,
            AutomationElement.IsOffscreenProperty);

        // Simple input loop so you can toggle the foreground filter
        var inputThread = new Thread(() =>
        {
            while (true)
            {
                Console.ReadLine();
                // Toggle the filter
                SetForegroundPidFilter(enabled: _foregroundPidFilter == 0);
            }
        })
        {
            IsBackground = true
        };
        inputThread.Start();

        // Keep the process alive
        var quit = new ManualResetEvent(false);
        Console.CancelKeyPress += (s, e) =>
        {
            e.Cancel = true;
            quit.Set();
        };
        quit.WaitOne();

        // Cleanup on exit
        Automation.RemoveAutomationFocusChangedEventHandler(OnFocusChanged);
        Automation.RemoveAllEventHandlers();
        WriteEventLogToJson();
        Console.WriteLine("UIA event listener stopped.");
    }

    private static void SetForegroundPidFilter(bool enabled)
    {
        if (!enabled)
        {
            _foregroundPidFilter = 0;
            Console.WriteLine("[Filter] Listening to ALL processes.");
            return;
        }

        var hwnd = GetForegroundWindow();
        if (hwnd == IntPtr.Zero)
        {
            Console.WriteLine("[Filter] No foreground window found; still listening to ALL.");
            _foregroundPidFilter = 0;
            return;
        }

        GetWindowThreadProcessId(hwnd, out var pid);
        _foregroundPidFilter = pid;
        Console.WriteLine($"[Filter] Foreground-only mode ON (PID={_foregroundPidFilter}).");
    }

    private static bool PassesFilter(AutomationElement? el)
    {
        if (_foregroundPidFilter == 0 || el is null) return true;

        // Try to compare the element's process ID to the foreground PID
        object? pidObj = el.GetCurrentPropertyValue(AutomationElement.ProcessIdProperty, true);
        if (pidObj is int pid && pid == _foregroundPidFilter) return true;

        return false;
    }

    private static void OnFocusChanged(object? src, AutomationFocusChangedEventArgs e)
    {
        try
        {
            var el = AutomationElement.FocusedElement;
            if (el is null || !PassesFilter(el)) return;

            var name = Safe(el, AutomationElement.NameProperty);
            var controlType = SafeControlType(el);
            var className = Safe(el, AutomationElement.ClassNameProperty);

            Console.WriteLine($"[Focus] {controlType}  Name='{name}'  Class='{className}'  PID={SafePid(el)}");

            AddLogEvent(new LogEvent
            {
                EventType = "Focus",
                TimestampUtc = DateTime.UtcNow,
                ControlType = controlType,
                Name = name,
                ClassName = className,
                ProcessId = SafePid(el)
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Focus][ERR] {ex.Message}");
        }
    }

    private static void OnInvoked(object? src, AutomationEventArgs e)
    {
        try
        {
            if (src is not AutomationElement el || !PassesFilter(el)) return;

            var name = Safe(el, AutomationElement.NameProperty);
            var controlType = SafeControlType(el);
            var className = Safe(el, AutomationElement.ClassNameProperty);
            Console.WriteLine($"[Invoke] {controlType}  Name='{name}'  PID={SafePid(el)}");

            AddLogEvent(new LogEvent
            {
                EventType = "Invoke",
                TimestampUtc = DateTime.UtcNow,
                ControlType = controlType,
                Name = name,
                ClassName = className,
                ProcessId = SafePid(el)
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Invoke][ERR] {ex.Message}");
        }
    }

    private static void OnStructureChanged(object? src, StructureChangedEventArgs e)
    {
        try
        {
            if (src is not AutomationElement el || !PassesFilter(el)) return;

            var name = Safe(el, AutomationElement.NameProperty);
            var controlType = SafeControlType(el);
            var className = Safe(el, AutomationElement.ClassNameProperty);
            Console.WriteLine($"[Structure] {e.StructureChangeType}  On '{name}'  PID={SafePid(el)}");

            AddLogEvent(new LogEvent
            {
                EventType = "StructureChanged",
                TimestampUtc = DateTime.UtcNow,
                ControlType = controlType,
                Name = name,
                ClassName = className,
                ProcessId = SafePid(el),
                StructureChangeType = e.StructureChangeType.ToString()
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Structure][ERR] {ex.Message}");
        }
    }

    private static void OnPropertyChanged(object? src, AutomationPropertyChangedEventArgs e)
    {
        try
        {
            if (src is not AutomationElement el || !PassesFilter(el)) return;

            var propName = e.Property.ProgrammaticName;
            var newVal = e.NewValue;
            var name = Safe(el, AutomationElement.NameProperty);
            var controlType = SafeControlType(el);
            var className = Safe(el, AutomationElement.ClassNameProperty);
            Console.WriteLine($"[PropertyChanged] {propName} -> {newVal}  (Name='{name}' PID={SafePid(el)})");

            AddLogEvent(new LogEvent
            {
                EventType = "PropertyChanged",
                TimestampUtc = DateTime.UtcNow,
                ControlType = controlType,
                Name = name,
                ClassName = className,
                ProcessId = SafePid(el),
                PropertyName = propName,
                NewValue = newVal
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[PropChanged][ERR] {ex.Message}");
        }
    }

    // -------- helpers --------
    private static string Safe(AutomationElement el, AutomationProperty prop)
    {
        try
        {
            var v = el.GetCurrentPropertyValue(prop, true);
            return v?.ToString() ?? string.Empty;
        }
        catch { return string.Empty; }
    }

    private static string SafeControlType(AutomationElement el)
    {
        try
        {
            var ct = (ControlType)el.GetCurrentPropertyValue(AutomationElement.ControlTypeProperty, true);
            return ct?.ProgrammaticName ?? "ControlType.Unknown";
        }
        catch { return "ControlType.Unknown"; }
    }

    private static int SafePid(AutomationElement el)
    {
        try
        {
            var v = el.GetCurrentPropertyValue(AutomationElement.ProcessIdProperty, true);
            return v is int i ? i : -1;
        }
        catch { return -1; }
    }

    private static void AddLogEvent(LogEvent logEvent)
    {
        lock (_eventLogLock)
        {
            _eventLog.Add(logEvent);
        }
    }

    private static void WriteEventLogToJson()
    {
        try
        {
            var targetDir = GetResourcesDirectory();
            Directory.CreateDirectory(targetDir);
            var fileName = "uia_log.json";
            var filePath = Path.Combine(targetDir, fileName);
            var options = new JsonSerializerOptions { WriteIndented = true };
            
            List<LogEvent> allEvents = new();
            
            // Try to read existing events from the file
            if (File.Exists(filePath))
            {
                try
                {
                    var existingJson = File.ReadAllText(filePath);
                    var existingEvents = JsonSerializer.Deserialize<List<LogEvent>>(existingJson);
                    if (existingEvents != null)
                    {
                        allEvents.AddRange(existingEvents);
                        Console.WriteLine($"Loaded {existingEvents.Count} existing events from log file");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[LoadLog][ERR] Could not load existing log: {ex.Message}");
                }
            }
            
            // Add new events from this session
            List<LogEvent> newEvents;
            lock (_eventLogLock)
            {
                newEvents = new List<LogEvent>(_eventLog);
            }
            
            allEvents.AddRange(newEvents);
            
            // Write all events back to the file
            File.WriteAllText(filePath, JsonSerializer.Serialize(allEvents, options));
            Console.WriteLine($"Saved UIA log to: {filePath} (Total: {allEvents.Count} events, New: {newEvents.Count} events)");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[SaveLog][ERR] {ex.Message}");
        }
    }

    private static string GetResourcesDirectory()
    {
        var baseDir = AppContext.BaseDirectory; // .../src/uia_listener/bin/Debug/net8.0-windows/
        var uiaProjectDir = Directory.GetParent(baseDir)?.Parent?.Parent?.Parent?.FullName; // -> .../src/uia_listener
        var srcDir = Directory.GetParent(uiaProjectDir ?? string.Empty)?.FullName; // -> .../src
        if (string.IsNullOrEmpty(srcDir))
        {
            return Path.Combine(baseDir, "resources");
        }
        return Path.Combine(srcDir, "create_json_schema", "resources");
    }

    private class LogEvent
    {
        public string EventType { get; set; } = string.Empty;
        public DateTime TimestampUtc { get; set; }
        public string ControlType { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string ClassName { get; set; } = string.Empty;
        public int ProcessId { get; set; }
        public string? PropertyName { get; set; }
        public object? NewValue { get; set; }
        public string? StructureChangeType { get; set; }
    }
}
