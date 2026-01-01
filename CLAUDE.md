# CLAUDE.md - AI Assistant Guide for DawVert

## Project Overview

DawVert (DAW ConVERTer) is a project file converter that transforms music project files between various Digital Audio Workstation (DAW) formats. It supports conversion between professional DAWs (FL Studio, Ableton Live, LMMS, Reaper), tracker formats (MOD, XM, IT, S3M), web-based music tools, and retro/chiptune formats.

**License:** GPL-3.0-or-later

## Quick Start Commands

```bash
# Basic conversion
python3 dawvert_cmd.py -i <input_file> -ot <output_type> -o <output_file>

# With explicit input type (when auto-detect unavailable)
python3 dawvert_cmd.py -it jummbox -i song.json -ot flp -o out.flp

# With SoundFont for MIDI sources
python3 dawvert_cmd.py --soundfont "soundfont.sf2" -i song.mid -ot flp -o out.flp

# Run the UI version
python3 dawvert_ui.py
```

## Dependencies

**Required:**
```
varint, numpy, mido, lxml, chardet, av, beautifulsoup4, blackboxprotobuf, pypng
git+https://github.com/Perlence/rpp
```

**For UI:** `PyQt6`

**Optional:** `xmodits_py` (for extracting tracker samples)

External libraries (.dll/.so) available at: https://github.com/SatyrDiamond/DawVert-Libs

## Architecture Overview

### Core Components

```
DawVert/
├── dawvert_cmd.py          # CLI entry point
├── dawvert_ui.py           # PyQt6 GUI entry point
├── objects/
│   ├── core.py             # Main conversion orchestrator
│   └── convproj/           # Conversion project data model
│       └── project.py      # cvpj_project class
├── plugins/
│   ├── __init__.py         # Plugin system base classes
│   ├── input/              # Input format parsers
│   ├── output/             # Output format generators
│   ├── plugconv/           # DAW-to-DAW plugin converters
│   └── plugconv_ext/       # External plugin converters
└── functions_song/         # Project type conversion functions
```

### Project Type System

DawVert uses different internal project types based on how the source DAW organizes data:

| Type | Name | Description |
|------|------|-------------|
| `r` | Regular | Standard linear track-based projects |
| `ri` | RegularIndexed | Tracks with pattern/playlist indexing |
| `rm` | RegularMultiple | Multiple arrangement support |
| `rs` | RegularScened | Scene/clip-based arrangements |
| `m` | Multiple | Pattern-based projects (tracker-style) |
| `mi` | MultipleIndexed | Pattern-based with indexed instruments |
| `ms` | MultipleScened | Pattern-based with scene support |

### Plugin System

All plugins inherit from `plugins.base` and must implement:

```python
class my_plugin(plugins.base):
    def is_dawvert_plugin(self): return 'input'  # or 'output', 'plugconv', etc.
    def get_shortname(self): return 'my_format'
    def get_name(self): return 'My Format Name'
    def get_prop(self, in_dict):
        in_dict['file_ext'] = ['ext']
        in_dict['projtype'] = 'r'
        # ... other properties
```

#### Plugin Types

- **input**: Parse source files into `convproj_obj`
- **output**: Write `convproj_obj` to target format
- **plugconv**: Convert instrument/effect plugins between DAWs
- **plugconv_ext**: Convert to external plugins (VST/CLAP/VSTi)
- **audiofile**: Audio format handlers
- **audiocodec**: Audio encoding/decoding
- **audioconv**: Audio format conversion
- **extplugin**: External plugin wrappers

#### Plugin Sets

Input plugins are organized into sets:
- `main`: Primary supported formats
- `exper`: Experimental features
- `ai`: AI-based input (e.g., audio-to-MIDI)
- `gameres`, `gamespec`: Game-related formats
- `old`: Legacy/broken plugins

Output plugins:
- `main`: Stable outputs
- `wip`: Work-in-progress
- `old`: Legacy outputs

## Key Data Models

### Conversion Project (`objects/convproj/project.py`)

The central `cvpj_project` class holds:
- `type`: Project type (r, ri, m, mi, etc.)
- `track_data`: Dictionary of tracks
- `fxrack`: FX mixer channels
- `plugins`: Plugin instances
- `samplerefs`: Audio sample references
- `automation`: Automation data
- `params`: Project parameters (BPM, time signature)

### Tracks (`objects/convproj/tracks.py`)

Track types: `instrument`, `audio`, `fx`, `group`, `master`

Key properties:
- `visual`: Name, color, UI settings
- `placements`: Clips/notes/audio regions
- `plugslots`: Synth and effect plugin slots
- `params`: Track parameters (vol, pan, etc.)

### Plugin Data (`objects/convproj/plugin.py`)

Plugins use category/type/subtype identification:
- `native:daw_name:plugin_name` - DAW-native plugins
- `external:vst2:plugin_name` - VST2 plugins
- `universal:synth-osc` - Universal sampler/synth

## File Naming Conventions

### Input Plugins (`plugins/input/`)
- `r_*.py` - Regular project type
- `ri_*.py` - RegularIndexed
- `m_*.py` - Multiple (pattern-based)
- `mi_*.py` - MultipleIndexed
- `ms_*.py` - MultipleScened

### Plugin Conversion (`plugins/plugconv/`)
Format: `source__direction_target.py`
- `flstudio__n_lmms.py` - FL Studio native to LMMS native
- `universal__v_directx.py` - Universal to DirectX
- `n_` = native plugins, `v_` = VST/external

### Functions
- `functions/` - General utility functions
- `functions_compat/` - Compatibility transformations
- `functions_song/` - Project type conversions
- `functions_plugin/` - Plugin-specific utilities
- `functions_plugin_ext/` - External plugin parameters

## Data Files

### Dataset Files (`data_main/dataset/`)
`.dset` files containing:
- Instrument/sample mappings
- Color schemes
- Parameter definitions

### Plugin Translations (`data_main/plugts/`)
Plugin parameter translation tables between DAWs.

## Common Development Tasks

### Adding a New Input Format

1. Create `plugins/input/{type}_{shortname}.py`
2. Implement required methods:
   - `is_dawvert_plugin()` -> `'input'`
   - `get_shortname()`, `get_name()`
   - `get_prop()` - set file extensions, project type
   - `detect()` - for autodetection (optional)
   - `parse(convproj_obj, input_file, dv_config)` - main parsing

3. Use `objects/file_proj/` for file format parsing if complex

### Adding a New Output Format

1. Create `plugins/output/{shortname}.py`
2. Implement:
   - `gettype()` - return expected input project type
   - `parse(convproj_obj, output_file)` - main generation

### Adding Plugin Conversion

1. Create `plugins/plugconv/{source}__{n|v}_{target}.py`
2. Define conversion between plugin parameter sets
3. Register in `get_prop()` with `in_plugins`, `out_plugins`

## FX Routing Types

The converter handles different FX routing models:
- `none` - No FX routing
- `rack` - FL Studio-style FX rack
- `groupreturn` - Ableton-style groups/returns
- `route` - Reaper-style flexible routing

Conversions between these are in `functions_compat/fxchange.py`.

## Configuration

### `__config/config.ini`
```ini
[soundfont2]
gm = "path/to/gm.sf2"
gs = "path/to/gs.sf2"
xg = "path/to/xg.sf2"
mt32 = "path/to/mt32.sf2"

[extplug_cat]
foss = 1      # Enable FOSS plugin conversions
nonfree = 1   # Enable non-free plugin conversions
shareware = 1
old = 0
```

### Runtime Directories
- `__samples_extracted/` - Samples extracted from project files
- `__samples_downloaded/` - Downloaded samples
- `__samples_generated/` - Generated audio (wave tables, etc.)
- `__samples_converted/` - Format-converted samples

## Code Style Notes

- Files use tabs for indentation
- SPDX license headers: `# SPDX-FileCopyrightText: 2024 SatyrDiamond`
- Logging via Python's `logging` module with named loggers
- Type hints are minimal; code is dynamically typed

## Testing

No formal test suite exists. Manual testing with sample project files is the current approach.

To verify a conversion:
1. Convert a known project file
2. Open the output in the target DAW
3. Compare tracks, instruments, automation, and audio

## Common Pitfalls

1. **Project type mismatch**: Input type must be convertible to output type
2. **Missing autodetect**: Some formats require explicit `-it` flag
3. **Plugin dependencies**: Some conversions need external plugin data
4. **Sample paths**: External samples need correct path configuration
5. **Platform differences**: VST paths differ between Windows/Linux

## Debugging

Enable verbose logging:
```python
# In objects/core.py, loggers are set to INFO by default
# Set to DEBUG for more detail:
logger_core.setLevel(logging.DEBUG)
```

Use `-pq` flag to show only plugin conversion logs.

## Contributing Guidelines

1. Follow existing file naming conventions
2. Add SPDX headers to new files
3. Use existing data structures from `objects/convproj/`
4. Test with multiple project files before submitting
5. Document new formats in `docs/input_plugins.md` or `docs/output_plugins.md`

## External Resources

- **GitHub:** https://github.com/SatyrDiamond/DawVert
- **GitLab:** https://gitlab.com/SatyrDiamond/DawVert
- **Codeberg:** https://codeberg.org/SatyrDiamond/DawVert
- **Discord:** https://discord.gg/SWkR6Z9pQC
- **External Libraries:** https://github.com/SatyrDiamond/DawVert-Libs
