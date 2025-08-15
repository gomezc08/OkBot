using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Automation;

internal static class Program
{
    // Optional: filter to the current foreground process only
    private static int _foregroundPidFilter = 0;

    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out int lpdwProcessId);

    [STAThread] // UIA callbacks work best with STA
    private static void Main(string[] args)
    {
        Console.WriteLine("UIA event listener starting...");
        Console.WriteLine("Press ENTER to toggle 'foreground app only' filter. Press Ctrl+C to exit.\n");

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
            var el = Automation.FocusedElement;
            if (el is null || !PassesFilter(el)) return;

            var name = Safe(el, AutomationElement.NameProperty);
            var controlType = SafeControlType(el);
            var className = Safe(el, AutomationElement.ClassNameProperty);

            Console.WriteLine($"[Focus] {controlType}  Name='{name}'  Class='{className}'  PID={SafePid(el)}");
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
            Console.WriteLine($"[Invoke] {controlType}  Name='{name}'  PID={SafePid(el)}");
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

            Console.WriteLine($"[Structure] {e.StructureChangeType}  On '{Safe(el, AutomationElement.NameProperty)}'  PID={SafePid(el)}");
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
            Console.WriteLine($"[PropertyChanged] {propName} -> {newVal}  (Name='{Safe(el, AutomationElement.NameProperty)}' PID={SafePid(el)})");
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
}