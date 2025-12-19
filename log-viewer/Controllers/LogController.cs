using Microsoft.AspNetCore.Mvc;
using System.Text.RegularExpressions;

namespace LogViewer.Controllers;

[ApiController]
[Route("api")]
public class LogController : ControllerBase
{
    private const string LOG_DIR = "/var/log/remote";

    [HttpGet("files")]
    public IActionResult GetFiles()
    {
        var files = new List<object>();

        if (Directory.Exists(LOG_DIR))
        {
            var logFiles = Directory.GetFiles(LOG_DIR, "*.log", SearchOption.AllDirectories);
            
            foreach (var filepath in logFiles)
            {
                var fileInfo = new FileInfo(filepath);
                var relativePath = Path.GetRelativePath(LOG_DIR, filepath);
                
                files.Add(new
                {
                    path = relativePath,
                    full_path = filepath,
                    size = fileInfo.Length,
                    modified = fileInfo.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                });
            }
        }

        // Sort by modification time (newest first)
        files = files.OrderByDescending(f => ((dynamic)f).modified).ToList();

        return Ok(new { files });
    }

    [HttpGet("logs")]
    public IActionResult GetLogs(
        [FromQuery] string file = "all-remote.log",
        [FromQuery] int lines = 100,
        [FromQuery] string search = "",
        [FromQuery] string level = "")
    {
        // Build full path
        var fullPath = file.StartsWith("/") ? file : Path.Combine(LOG_DIR, file);

        // Security check - ensure path is within LOG_DIR
        var absolutePath = Path.GetFullPath(fullPath);
        var absoluteLogDir = Path.GetFullPath(LOG_DIR);
        
        if (!absolutePath.StartsWith(absoluteLogDir))
        {
            return StatusCode(403, new { error = "Invalid file path" });
        }

        var logs = ReadLogFile(fullPath, lines, search, level);

        return Ok(new
        {
            file,
            count = logs.Count,
            logs
        });
    }

    [HttpGet("stats")]
    public IActionResult GetStats()
    {
        var files = new List<FileInfo>();

        if (Directory.Exists(LOG_DIR))
        {
            var logFiles = Directory.GetFiles(LOG_DIR, "*.log", SearchOption.AllDirectories);
            files = logFiles.Select(f => new FileInfo(f)).ToList();
        }

        var totalSize = files.Sum(f => f.Length);

        return Ok(new
        {
            total_files = files.Count,
            total_size = totalSize,
            total_size_mb = Math.Round(totalSize / 1024.0 / 1024.0, 2)
        });
    }

    private List<object> ReadLogFile(string filepath, int lines, string search, string level)
    {
        if (!System.IO.File.Exists(filepath))
        {
            return new List<object>();
        }

        try
        {
            var allLines = System.IO.File.ReadAllLines(filepath);
            
            // Get last N lines
            var recentLines = allLines.Length > lines 
                ? allLines.TakeLast(lines).ToArray() 
                : allLines;

            var parsedLines = new List<object>();

            foreach (var line in recentLines)
            {
                if (string.IsNullOrWhiteSpace(line))
                    continue;

                var parsed = ParseSyslogLine(line);

                // Apply filters
                if (!string.IsNullOrEmpty(search) && 
                    !parsed.Raw.Contains(search, StringComparison.OrdinalIgnoreCase))
                    continue;

                if (!string.IsNullOrEmpty(level) && 
                    !parsed.Raw.Contains(level, StringComparison.OrdinalIgnoreCase))
                    continue;

                parsedLines.Add(new
                {
                    timestamp = parsed.Timestamp,
                    hostname = parsed.Hostname,
                    tag = parsed.Tag,
                    message = parsed.Message,
                    raw = parsed.Raw
                });
            }

            return parsedLines;
        }
        catch (Exception ex)
        {
            return new List<object>
            {
                new
                {
                    timestamp = "",
                    hostname = "",
                    tag = "",
                    message = $"Error reading file: {ex.Message}",
                    raw = ""
                }
            };
        }
    }

    private SyslogEntry ParseSyslogLine(string line)
    {
        try
        {
            // RFC 3164 format: <priority>timestamp hostname tag: message
            // or simplified: timestamp hostname tag: message
            var pattern = @"(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+?):\s*(.*)";
            var match = Regex.Match(line.Trim(), pattern);

            if (match.Success)
            {
                return new SyslogEntry
                {
                    Timestamp = match.Groups[1].Value,
                    Hostname = match.Groups[2].Value,
                    Tag = match.Groups[3].Value,
                    Message = match.Groups[4].Value,
                    Raw = line.Trim()
                };
            }
            else
            {
                // If parsing fails, return raw line
                return new SyslogEntry
                {
                    Timestamp = "",
                    Hostname = "",
                    Tag = "",
                    Message = line.Trim(),
                    Raw = line.Trim()
                };
            }
        }
        catch
        {
            return new SyslogEntry
            {
                Timestamp = "",
                Hostname = "",
                Tag = "",
                Message = line.Trim(),
                Raw = line.Trim()
            };
        }
    }

    private class SyslogEntry
    {
        public string Timestamp { get; set; } = "";
        public string Hostname { get; set; } = "";
        public string Tag { get; set; } = "";
        public string Message { get; set; } = "";
        public string Raw { get; set; } = "";
    }
}
