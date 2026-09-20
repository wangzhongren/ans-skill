# PowerShell scaffold for ANS five-layer source tree
# Run from project root during bootstrap.

$dirs = @(
    "src/interface",
    "src/pipelines",
    "src/services/abstract",
    "src/services/public",
    "src/services/impl",
    "src/providers/abstract",
    "src/providers/public",
    "src/providers/impl",
    "src/models",
    "test",
    "docs/design",
    "docs/feature",
    "docs/change",
    "docs/fix"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}