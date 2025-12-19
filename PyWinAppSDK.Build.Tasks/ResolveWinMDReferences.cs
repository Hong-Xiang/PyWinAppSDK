using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.Build.Framework;
using Microsoft.Build.Utilities;
using NuGet.Common;
using NuGet.ProjectModel;

namespace PyWinAppSDK.Build.Tasks
{
    /// <summary>
    /// MSBuild task that reads project.assets.json and resolves all WinMD files from NuGet packages.
    /// Distinguishes between direct and transitive dependencies.
    /// </summary>
    public class ResolveWinMDReferences : Task
    {
        /// <summary>
        /// Path to project.assets.json file. If not specified, uses $(ProjectAssetsFile) from MSBuild context.
        /// </summary>
        public string AssetsFilePath { get; set; }

        /// <summary>
        /// Optional: Only consider these packages as possible direct references (case-insensitive).
        /// If not specified, all direct dependencies from the lock file are used.
        /// </summary>
        public string[] InputPackages { get; set; }

        /// <summary>
        /// Optional: Package IDs to exclude from WinMD resolution along with all their transitive dependencies (case-insensitive).
        /// When a package is excluded, it and all packages that depend on it are excluded.
        /// </summary>
        public string[] ExcludePackages { get; set; }

        /// <summary>
        /// Optional: Folder patterns to include WinMDs from (e.g., "metadata", "metadata\10.0.18362.0")
        /// If not specified, all WinMDs are included. Patterns are matched against the relative path within the package.
        /// </summary>
        public string[] WinMDFolders { get; set; }

        /// <summary>
        /// Output: WinMD files from directly referenced packages
        /// </summary>
        [Output]
        public ITaskItem[] InputWinMD { get; set; }

        /// <summary>
        /// Output: WinMD files from transitive dependencies
        /// </summary>
        [Output]
        public ITaskItem[] ReferencedWinMD { get; set; }

        public override bool Execute()
        {
            try
            {
                if (string.IsNullOrEmpty(AssetsFilePath))
                {
                    Log.LogError("AssetsFilePath not specified. Pass $(ProjectAssetsFile) or set explicitly.");
                    return false;
                }

                if (!File.Exists(AssetsFilePath))
                {
                    Log.LogError($"Assets file not found: {AssetsFilePath}");
                    return false;
                }

                var lockFile = LockFileUtilities.GetLockFile(AssetsFilePath, NullLogger.Instance);
                if (lockFile == null)
                {
                    Log.LogError("Failed to read lock file");
                    return false;
                }

                var packageRoot = lockFile.PackageFolders.FirstOrDefault()?.Path;
                if (string.IsNullOrEmpty(packageRoot))
                {
                    Log.LogError("Package root not found in lock file");
                    return false;
                }

                if (!packageRoot.EndsWith(Path.DirectorySeparatorChar.ToString()))
                {
                    packageRoot += Path.DirectorySeparatorChar;
                }

                // Determine direct dependencies
                // Get direct dependencies from all dependency groups
                var directDeps = lockFile.ProjectFileDependencyGroups
                    .SelectMany(g => g.Dependencies)
                    .Select(d => d.Split(' ', '/')[0])  // Handle "PackageId >= version" or "PackageId/version"
                    .Where(d => !string.IsNullOrEmpty(d))
                    .ToList();

                Log.LogMessage(MessageImportance.Low, 
                    $"Direct dependencies from lock file: {string.Join(", ", directDeps)}");

                // Filter by InputPackages if specified (only those that are actually referenced)
                HashSet<string> directIds;
                if (InputPackages != null && InputPackages.Length > 0)
                {
                    var inputPackageSet = new HashSet<string>(InputPackages, StringComparer.OrdinalIgnoreCase);
                    var filteredDeps = directDeps.Where(d => inputPackageSet.Contains(d)).ToList();
                    directIds = new HashSet<string>(filteredDeps, StringComparer.OrdinalIgnoreCase);
                    
                    Log.LogMessage(MessageImportance.Low, 
                        $"Filtered direct dependencies by InputPackages: {string.Join(", ", filteredDeps)}");
                }
                else
                {
                    directIds = new HashSet<string>(directDeps, StringComparer.OrdinalIgnoreCase);
                }

                var excludePackageSet = new HashSet<string>(
                    ExcludePackages ?? Array.Empty<string>(),
                    StringComparer.OrdinalIgnoreCase);

                // Build exclusion set: packages to exclude + all their transitive dependencies
                var allExcludedPackages = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                if (excludePackageSet.Count > 0)
                {
                    // Build dependency map from targets (not libraries directly)
                    var dependencyMap = new Dictionary<string, List<string>>(StringComparer.OrdinalIgnoreCase);
                    var target = lockFile.Targets.FirstOrDefault();
                    if (target != null)
                    {
                        foreach (var lib in target.Libraries)
                        {
                            var deps = lib.Dependencies
                                .Select(d => d.Id)
                                .ToList();
                            dependencyMap[lib.Name] = deps;
                        }
                    }

                    // For each excluded package, recursively add all its dependencies
                    void AddExcludedPackageRecursive(string pkgId)
                    {
                        if (allExcludedPackages.Contains(pkgId))
                            return;

                        allExcludedPackages.Add(pkgId);

                        if (dependencyMap.TryGetValue(pkgId, out var deps))
                        {
                            foreach (var dep in deps)
                            {
                                AddExcludedPackageRecursive(dep);
                            }
                        }
                    }

                    foreach (var excludePkg in excludePackageSet)
                    {
                        AddExcludedPackageRecursive(excludePkg);
                    }

                    Log.LogMessage(MessageImportance.Low,
                        $"Excluded packages (including transitive): {string.Join(", ", allExcludedPackages)}");
                }

                var includeFolders = WinMDFolders ?? Array.Empty<string>();
                var hasIncludeFolders = includeFolders.Length > 0;

                var inputWinMDs = new List<ITaskItem>();
                var referencedWinMDs = new List<ITaskItem>();

                // Process all libraries
                foreach (var lib in lockFile.Libraries)
                {
                    var pkgId = lib.Name;
                    var pkgVersion = lib.Version.ToNormalizedString();
                    var isDirect = directIds.Contains(pkgId);

                    // Skip excluded packages (including transitive exclusions)
                    if (allExcludedPackages.Contains(pkgId))
                    {
                        continue;
                    }

                    // Find WinMD files
                    var winmdFiles = lib.Files
                        .Where(f => f.EndsWith(".winmd", StringComparison.OrdinalIgnoreCase))
                        .ToList();

                    // Filter by folder patterns if specified
                    if (hasIncludeFolders)
                    {
                        winmdFiles = winmdFiles.Where(f =>
                        {
                            var folderPath = Path.GetDirectoryName(f).Replace('/', Path.DirectorySeparatorChar);
                            
                            // Check if folder path matches any pattern exactly
                            return includeFolders.Any(pattern =>
                            {
                                var normalizedPattern = pattern.Replace('/', Path.DirectorySeparatorChar).Replace('\\', Path.DirectorySeparatorChar);
                                return folderPath.Equals(normalizedPattern, StringComparison.OrdinalIgnoreCase);
                            });
                        }).ToList();
                    }

                    if (winmdFiles.Count == 0)
                    {
                        continue;
                    }

                    foreach (var file in winmdFiles)
                    {
                        var relative = file.Replace('/', Path.DirectorySeparatorChar);
                        var fullPath = Path.Combine(packageRoot, pkgId.ToLowerInvariant(), pkgVersion, relative);

                        var item = new TaskItem(fullPath);
                        item.SetMetadata("PackageId", pkgId);
                        item.SetMetadata("PackageVersion", pkgVersion);
                        item.SetMetadata("IsDirect", isDirect.ToString());
                        item.SetMetadata("RelativePath", file);

                        if (isDirect)
                        {
                            inputWinMDs.Add(item);
                        }
                        else
                        {
                            referencedWinMDs.Add(item);
                        }
                    }
                }

                InputWinMD = inputWinMDs.ToArray();
                ReferencedWinMD = referencedWinMDs.ToArray();

                var totalWinMDs = inputWinMDs.Count + referencedWinMDs.Count;
                var packageCount = lockFile.Libraries.Count(l => 
                    !allExcludedPackages.Contains(l.Name) && 
                    l.Files.Any(f => f.EndsWith(".winmd", StringComparison.OrdinalIgnoreCase)));
                
                var excludedCount = allExcludedPackages.Count > 0 ? lockFile.Libraries.Count(l => 
                    allExcludedPackages.Contains(l.Name) && 
                    l.Files.Any(f => f.EndsWith(".winmd", StringComparison.OrdinalIgnoreCase))) : 0;
                
                Log.LogMessage(MessageImportance.High,
                    $"Resolved {totalWinMDs} WinMDs from {packageCount} packages (Direct: {inputWinMDs.Count}, Transitive: {referencedWinMDs.Count}{(excludedCount > 0 ? $", Excluded: {excludedCount} packages" : "")})");

                return true;
            }
            catch (Exception ex)
            {
                Log.LogErrorFromException(ex, showStackTrace: true);
                return false;
            }
        }
    }
}
