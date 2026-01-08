# Copilot Instructions for mdkits

## Architecture Overview
mdkits is a Python CLI toolkit for molecular dynamics (MD) and density functional theory (DFT) analysis. It uses:
- **MDAnalysis** for trajectory processing and analysis
- **ASE** for atomic structure manipulation and modeling
- **Click** for command-line interface with subcommands: `md`, `dft`, `build`, `convert`, `extract`, `data`, `plot`

Key modules:
- `md_cli/`: MD analysis tools (density, RDF, MSD, hydrogen bonds, etc.)
- `dft_cli/`: DFT property analysis (PDOS, cube files)
- `build_cli/`: Structure modeling (bulk, surface, interface, supercell)
- `cli/`: General utilities (convert, extract, data processing, plotting)
- `util/`: Shared utilities (geometry, MDA/ASE wrappers, CP2K parsing)

## Development Workflow
- **Setup**: `poetry install` (manages dependencies and virtual environment)
- **Testing/Linting**: `tox` (runs pytest, isort, pylint across Python 3.11)
- **Building**: `poetry build` (creates distribution packages)
- **Publishing**: `poetry publish` (uploads to PyPI)

## Code Patterns
- **CLI Commands**: Each subcommand is a separate module with `main` function decorated with `@click.command()`. Add to parent group via `cli.add_command(module.main)`.
- **MD Analysis**: Inherit from `MDAnalysis.analysis.base.AnalysisBase`. Implement `single_frame()` and `_conclude()` methods. Use `self.atomgroup.select_atoms()` for selections. Common options added via `md_cli.setting.common_setting` decorator.
- **Structure Handling**: Use ASE `Atoms` objects for modeling. Convert between formats with `ase.io.read/write()`.
- **Configuration**: YAML configs in `config/settings.yml`. Access via `mdkits.config`.
- **Utilities**: Import from `mdkits.util.*` (e.g., `numpy_geo` for geometry, `encapsulated_mda` for MDA wrappers, `cp2k_input_parsing` for CP2K inputs, `arg_type` for custom Click types like `FrameRange` and `Cell`).
- **Output**: Use `mdkits.util.out_err` for consistent error handling. Default output filenames follow `analysis_type.dat` pattern. Use `os_operation.default_file_name` for default input file detection.

## Examples
- **Adding MD command**: Create `md_cli/new_analysis.py` with class inheriting `AnalysisBase`, add `main` click command decorated with `@common_setting`, import and add to `md_cli.py`.
- **ASE modeling**: Use `ase.build.bulk()` for crystals, `ase.build.surface()` for slabs. Export with `ase.io.write('file.cif', atoms)`.
- **MDAnalysis selections**: Use MDA selection language: `"name O and prop z < 10"` for oxygen atoms below z=10.
- **Custom types**: Use `arg_type.FrameRange` for frame ranges (e.g., `1:10:2`), `arg_type.Cell` for lattice parameters (e.g., `10,10,10` or `10,10,10,90,90,90`).

## Dependencies
Pinned versions in `pyproject.toml`. Key: MDAnalysis>=2.8.0, ASE>=3.22.1, numpy>=1.26.4. Dev tools: pytest, pylint, isort.

## Conventions
- Line length: 120 chars (pylint config)
- Imports: Sorted with isort
- Warnings: Suppress with `warnings.filterwarnings("ignore")` in analysis scripts
- File extensions: `.xyz` for trajectories, `.cif` for structures, `.dat` for data output</content>
<parameter name="filePath">d:\script\mdkits\.github\copilot-instructions.md