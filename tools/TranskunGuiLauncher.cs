using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows.Forms;

internal static class TranskunGuiLauncher
{
    private static int Main(string[] args)
    {
        string root = AppDomain.CurrentDomain.BaseDirectory;
        string script = Path.Combine(root, "app", "gui", "transkun_gui.py");
        string[] candidates = new[]
        {
            Path.Combine(root, "runtime", "venv", "Scripts", "pythonw.exe"),
            Path.Combine(root, "runtime", "venv", "Scripts", "python.exe"),
            Path.Combine(root, "runtime", "python", "pythonw.exe"),
            Path.Combine(root, "runtime", "python", "python.exe")
        };

        string python = null;
        foreach (string candidate in candidates)
        {
            if (File.Exists(candidate))
            {
                python = candidate;
                break;
            }
        }

        if (python == null || !File.Exists(script))
        {
            MessageBox.Show(
                "Missing Transkun GUI runtime files. Please extract the full package again.",
                "Transkun Windows OneClick",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
            return 1;
        }

        try
        {
            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = python,
                Arguments = Quote(script) + BuildArgumentString(args),
                WorkingDirectory = root,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            Process.Start(startInfo);
            return 0;
        }
        catch (Exception exc)
        {
            MessageBox.Show(
                "Failed to start Transkun GUI:\n" + exc.Message,
                "Transkun Windows OneClick",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
            return 1;
        }
    }

    private static string BuildArgumentString(string[] args)
    {
        if (args == null || args.Length == 0)
        {
            return "";
        }

        StringBuilder builder = new StringBuilder();
        foreach (string arg in args)
        {
            builder.Append(' ');
            builder.Append(Quote(arg));
        }
        return builder.ToString();
    }

    private static string Quote(string value)
    {
        return "\"" + value.Replace("\"", "\\\"") + "\"";
    }
}
