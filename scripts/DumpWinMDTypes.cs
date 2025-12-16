// Single-file CLI that uses NuGet.ProjectModel to read project.assets.json,
// list resolved packages, and dump their WinMD files.
#:package Nuget.ProjectModel

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using NuGet.ProjectModel;
using NuGet.Common;

throw new NotImplementedException("This script is a placeholder for demonstration purposes.");

if (args.Length < 1)
{
    Console.WriteLine("Usage: dotnet run -- <path-to-project.assets.json> [output.json]");
    return;
}

var assetsPath = Path.GetFullPath(args[0]);
var outputPath = args.Length > 1 ? Path.GetFullPath(args[1]) : Path.Combine(Environment.CurrentDirectory, "winmd_dump.json");

if (!File.Exists(assetsPath))
{
    Console.Error.WriteLine($"assets file not found: {assetsPath}");
    return;
}

var lockFile = LockFileUtilities.GetLockFile(assetsPath, NullLogger.Instance);
if (lockFile == null)
{
    Console.Error.WriteLine("failed to read lock file");
    return;
}

var packageRoot = lockFile.PackageFolders.FirstOrDefault()?.Path;
if (string.IsNullOrEmpty(packageRoot))
{
    Console.Error.WriteLine("package root not found in lock file");
    return;
}

// Normalize package root to ensure trailing directory separator.
if (!packageRoot.EndsWith(Path.DirectorySeparatorChar))
{
    packageRoot += Path.DirectorySeparatorChar;
}

// Determine direct (top-level) package ids from the first dependency group.
var directIds = new HashSet<string>(
    lockFile.ProjectFileDependencyGroups
        .SelectMany(g => g.Dependencies)
        .Select(d => d.Split('/')[0]),
    StringComparer.OrdinalIgnoreCase);

// Choose the first target (most builds have one per framework/RID).
var target = lockFile.Targets.FirstOrDefault();
if (target == null)
{
    Console.Error.WriteLine("no targets found in lock file");
    return;
}

var packages = new List<PackageWinmdInfo>();

foreach (var lib in target.Libraries)
{
    var pkgId = lib.Name;
    var pkgVersion = lib.Version.ToNormalizedString();
    var packageWinmds = new List<string>();

    // Collect compile-time and runtime WinMDs.
    CollectWinmds(lib.CompileTimeAssemblies, pkgId, pkgVersion, packageRoot, packageWinmds);
    CollectWinmds(lib.RuntimeAssemblies, pkgId, pkgVersion, packageRoot, packageWinmds);
    CollectWinmds(lib.RuntimeTargets, pkgId, pkgVersion, packageRoot, packageWinmds);

    if (packageWinmds.Count == 0)
    {
        continue;
    }

    packages.Add(new PackageWinmdInfo
    {
        PackageId = pkgId,
        Version = pkgVersion,
        IsDirect = directIds.Contains(pkgId),
        WinmdFiles = packageWinmds.Distinct(StringComparer.OrdinalIgnoreCase).OrderBy(p => p).ToList()
    });
}

var jsonOptions = new JsonSerializerOptions { WriteIndented = true };
var output = JsonSerializer.Serialize(packages.OrderBy(p => p.PackageId), jsonOptions);
File.WriteAllText(outputPath, output);

Console.WriteLine($"Packages with WinMDs: {packages.Count}");
Console.WriteLine($"Output: {outputPath}");

static void CollectWinmds(IEnumerable<LockFileItem> items, string pkgId, string pkgVersion, string pkgRoot, List<string> bucket)
{
    foreach (var item in items)
    {
        if (!item.Path.EndsWith(".winmd", StringComparison.OrdinalIgnoreCase))
        {
            continue;
        }

        // Build full path: <pkgRoot>/<id>/<version>/<relative>
        var relative = item.Path.Replace('/', Path.DirectorySeparatorChar);
        var full = Path.Combine(pkgRoot, pkgId.ToLowerInvariant(), pkgVersion, relative);
        bucket.Add(full);
    }
}

record PackageWinmdInfo
{
    public string PackageId { get; init; }
    public string Version { get; init; }
    public bool IsDirect { get; init; }
    public List<string> WinmdFiles { get; init; }
}
