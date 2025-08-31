/**
 * This program records UI Automation events from the user's desktop and persists them to a JSON file.
 * Enhanced to track mouse clicks, browser URLs, and detailed element information for automation schema.
 */

using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Threading;
using System.Windows.Automation;
using System.Windows.Forms;
using System.Diagnostics;

internal static class Program
{
    // Optional: filter to the current foreground process only
    private static int _foregroundPidFilter = 0;

    // In-memory event log to persist on exit
    private static readonly List<LogEvent> _eventLog = new();
    private static readonly object _eventLogLock = new();

    // Mouse tracking
    private static readonly List<MouseClickEvent> _mouseClicks = new();
    private static readonly object _mouseClicksLock = new();

    // Browser URL tracking
    private static readonly List<BrowserUrlEvent> _browserUrls = new();
    private static readonly object _browserUrlsLock = new();

    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out int lpdwProcessId);

    [DllImport("user32.dll")]
    private static extern void GetCursorPos(out POINT lpPoint);

    [DllImport("user32.dll")]
    private static extern IntPtr GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    private static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    [DllImport("user32.dll")]
    private static extern IntPtr FindWindowEx(IntPtr hwndParent, IntPtr hwndChildAfter, string lpszClass, string lpszWindow);

    [DllImport("user32.dll")]
    private static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    private static extern int GetClassName(IntPtr hWnd, System.Text.StringBuilder lpClassName, int nMaxCount);

    [StructLayout(LayoutKind.Sequential)]
    private struct POINT
    {
        public int x;
        public int y;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct RECT
    {
        public int left;
        public int top;
        public int right;
        public int bottom;
    }

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

        // Start mouse tracking
        StartMouseTracking();

        // Start browser URL tracking
        StartBrowserUrlTracking();

        // 1) Focus changed (fires when the user focuses a new control/window)
        Automation.AddAutomationFocusChangedEventHandler(OnFocusChanged);

        // 2) Invoked (e.g., button click via InvokePattern)
        Automation.AddAutomationEventHandler(
            InvokePattern.InvokedEvent,
            AutomationElement.RootElement,
            TreeScope.Subtree,
            OnInvoked);

        // 3) Structure changed (e.g., new windows/controls appear or disappear)
        Automation.AddStructureChangedEventHandler(
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

    private static void StartMouseTracking()
    {
        var mouseThread = new Thread(() =>
        {
            while (true)
            {
                try
                {
                    GetCursorPos(out POINT point);
                    
                    // Check for mouse clicks (simplified - in production you'd use SetWindowsHookEx)
                    if (Control.MouseButtons == MouseButtons.Left || Control.MouseButtons == MouseButtons.Right)
                    {
                        var clickEvent = new MouseClickEvent
                        {
                            TimestampUtc = DateTime.UtcNow,
                            X = point.x,
                            Y = point.y,
                            Button = Control.MouseButtons == MouseButtons.Left ? "left" : "right"
                        };

                        lock (_mouseClicksLock)
                        {
                            _mouseClicks.Add(clickEvent);
                        }

                        Console.WriteLine($"[Mouse] {clickEvent.Button} click at ({point.x}, {point.y})");
                    }

                    Thread.Sleep(50); // Check every 50ms
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[Mouse][ERR] {ex.Message}");
                }
            }
        })
        {
            IsBackground = true
        };
        mouseThread.Start();
    }

    private static void StartBrowserUrlTracking()
    {
        var browserThread = new Thread(() =>
        {
            while (true)
            {
                try
                {
                    // Track Chrome browser URLs
                    TrackChromeUrls();
                    
                    // Track other browsers as needed
                    Thread.Sleep(1000); // Check every second
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[Browser][ERR] {ex.Message}");
                }
            }
        })
        {
            IsBackground = true
        };
        browserThread.Start();
    }

    private static void TrackChromeUrls()
    {
        try
        {
            var chromeWindows = FindWindow("Chrome_WidgetWin_1", null);
            if (chromeWindows != IntPtr.Zero)
            {
                var url = ExtractChromeUrl(chromeWindows);
                if (!string.IsNullOrEmpty(url))
                {
                    var urlEvent = new BrowserUrlEvent
                    {
                        TimestampUtc = DateTime.UtcNow,
                        ProcessName = "chrome",
                        Url = url
                    };

                    lock (_browserUrlsLock)
                    {
                        // Only add if URL changed
                        if (_browserUrls.Count == 0 || _browserUrls[_browserUrls.Count - 1].Url != url)
                        {
                            _browserUrls.Add(urlEvent);
                            Console.WriteLine($"[Browser] Chrome URL: {url}");
                        }
                    }
                }
            }
        }
        catch { }
    }

    private static string ExtractChromeUrl(IntPtr chromeWindow)
    {
        try
        {
            // This is a simplified approach - in production you'd use Chrome DevTools Protocol
            var title = GetWindowTitle(chromeWindow);
            if (title.Contains(" - Google Chrome"))
            {
                var url = title.Replace(" - Google Chrome", "");
                if (url.StartsWith("http://") || url.StartsWith("https://"))
                {
                    return url;
                }
            }
        }
        catch { }
        return string.Empty;
    }

    private static string GetWindowTitle(IntPtr hwnd)
    {
        var title = new System.Text.StringBuilder(256);
        GetWindowText(hwnd, title, title.Capacity);
        return title.ToString();
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
            var processName = GetProcessName(el);
            var ancestorPath = GetAncestorPath(el);
            var coords = GetElementCoordinates(el);

            Console.WriteLine($"[Focus] {controlType}  Name='{name}'  Class='{className}'  Process='{processName}'  PID={SafePid(el)}");

            AddLogEvent(new LogEvent
            {
                EventType = "Focus",
                TimestampUtc = DateTime.UtcNow,
                ControlType = controlType,
                Name = name,
                ClassName = className,
                ProcessId = SafePid(el),
                ProcessName = processName,
                AncestorPath = ancestorPath,
                Coordinates = coords
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
            var processName = GetProcessName(el);
            var ancestorPath = GetAncestorPath(el);
            var coords = GetElementCoordinates(el);

            Console.WriteLine($"[Invoke] {controlType}  Name='{name}'  Process='{processName}'  PID={SafePid(el)}");

            AddLogEvent(new LogEvent
            {
                EventType = "Invoke",
                TimestampUtc = DateTime.UtcNow,
                ControlType = controlType,
                Name = name,
                ClassName = className,
                ProcessId = SafePid(el),
                ProcessName = processName,
                AncestorPath = ancestorPath,
                Coordinates = coords
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
            var processName = GetProcessName(el);
            var ancestorPath = GetAncestorPath(el);
            var coords = GetElementCoordinates(el);

            Console.WriteLine($"[Structure] {e.StructureChangeType}  On '{name}'  Process='{processName}'  PID={SafePid(el)}");

            AddLogEvent(new LogEvent
            {
                EventType = "StructureChanged",
                TimestampUtc = DateTime.UtcNow,
                ControlType = controlType,
                Name = name,
                ClassName = className,
                ProcessId = SafePid(el),
                ProcessName = processName,
                AncestorPath = ancestorPath,
                Coordinates = coords,
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
            var processName = GetProcessName(el);
            var ancestorPath = GetAncestorPath(el);
            var coords = GetElementCoordinates(el);

            Console.WriteLine($"[PropertyChanged] {propName} -> {newVal}  (Name='{name}' Process='{processName}' PID={SafePid(el)})");

            AddLogEvent(new LogEvent
            {
                EventType = "PropertyChanged",
                TimestampUtc = DateTime.UtcNow,
                ControlType = controlType,
                Name = name,
                ClassName = className,
                ProcessId = SafePid(el),
                ProcessName = processName,
                AncestorPath = ancestorPath,
                Coordinates = coords,
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

    private static string GetProcessName(AutomationElement el)
    {
        try
        {
            var pid = SafePid(el);
            if (pid > 0)
            {
                var process = Process.GetProcessById(pid);
                return process.ProcessName;
            }
        }
        catch { }
        return string.Empty;
    }

    private static List<string> GetAncestorPath(AutomationElement el)
    {
        var path = new List<string>();
        try
        {
            var current = el;
            var maxDepth = 10; // Prevent infinite loops
            var depth = 0;

            while (current != null && depth < maxDepth)
            {
                var name = Safe(current, AutomationElement.NameProperty);
                if (!string.IsNullOrEmpty(name))
                {
                    path.Insert(0, name);
                }
                else
                {
                    var controlType = SafeControlType(current);
                    path.Insert(0, controlType);
                }

                current = TreeWalker.RawViewWalker.GetParent(current);
                depth++;
            }
        }
        catch { }
        return path;
    }

    private static ElementCoordinates? GetElementCoordinates(AutomationElement el)
    {
        try
        {
            var boundingRect = el.Current.BoundingRectangle;
            if (boundingRect.IsEmpty) return null;

            return new ElementCoordinates
            {
                Coords = new Point { X = (int)boundingRect.X, Y = (int)boundingRect.Y },
                Bbox = new BoundingBox
                {
                    Left = (int)boundingRect.Left,
                    Top = (int)boundingRect.Top,
                    Right = (int)boundingRect.Right,
                    Bottom = (int)boundingRect.Bottom
                }
            };
        }
        catch
        {
            return null;
        }
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
            
            // Save UIA events
            var uiaFileName = "uia_log.json";
            var uiaFilePath = Path.Combine(targetDir, uiaFileName);
            var options = new JsonSerializerOptions { WriteIndented = true };
            
            List<LogEvent> uiaSnapshot;
            lock (_eventLogLock)
            {
                uiaSnapshot = new List<LogEvent>(_eventLog);
            }
            File.WriteAllText(uiaFilePath, JsonSerializer.Serialize(uiaSnapshot, options));
            Console.WriteLine($"Saved UIA log to: {uiaFilePath}");

            // Save mouse clicks
            var mouseFileName = "mouse_clicks.json";
            var mouseFilePath = Path.Combine(targetDir, mouseFileName);
            
            List<MouseClickEvent> mouseSnapshot;
            lock (_mouseClicksLock)
            {
                mouseSnapshot = new List<MouseClickEvent>(_mouseClicks);
            }
            File.WriteAllText(mouseFilePath, JsonSerializer.Serialize(mouseSnapshot, options));
            Console.WriteLine($"Saved mouse clicks to: {mouseFilePath}");

            // Save browser URLs
            var browserFileName = "browser_urls.json";
            var browserFilePath = Path.Combine(targetDir, browserFileName);
            
            List<BrowserUrlEvent> browserSnapshot;
            lock (_browserUrlsLock)
            {
                browserSnapshot = new List<BrowserUrlEvent>(_browserUrls);
            }
            File.WriteAllText(browserFilePath, JsonSerializer.Serialize(browserSnapshot, options));
            Console.WriteLine($"Saved browser URLs to: {browserFilePath}");
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
            return Path.Combine(baseDir, "resources", "output_logs");
        }
        return Path.Combine(srcDir, "create_json_schema", "resources", "output_logs");
    }

    private class LogEvent
    {
        public string EventType { get; set; } = string.Empty;
        public DateTime TimestampUtc { get; set; }
        public string ControlType { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string ClassName { get; set; } = string.Empty;
        public int ProcessId { get; set; }
        public string ProcessName { get; set; } = string.Empty;
        public List<string> AncestorPath { get; set; } = new();
        public ElementCoordinates? Coordinates { get; set; }
        public string? PropertyName { get; set; }
        public object? NewValue { get; set; }
        public string? StructureChangeType { get; set; }
    }

    private class MouseClickEvent
    {
        public DateTime TimestampUtc { get; set; }
        public int X { get; set; }
        public int Y { get; set; }
        public string Button { get; set; } = string.Empty;
    }

    private class BrowserUrlEvent
    {
        public DateTime TimestampUtc { get; set; }
        public string ProcessName { get; set; } = string.Empty;
        public string Url { get; set; } = string.Empty;
    }

    private class ElementCoordinates
    {
        public Point Coords { get; set; }
        public BoundingBox Bbox { get; set; }
    }

    private class Point
    {
        public int X { get; set; }
        public int Y { get; set; }
    }

    private class BoundingBox
    {
        public int Left { get; set; }
        public int Top { get; set; }
        public int Right { get; set; }
        public int Bottom { get; set; }
    }
}