# MAS Training Audio Generator - TODO List

This document tracks the progress of code quality improvements and feature enhancements for the MAS Training Audio Generator project.

---

## 1. Separation of Concerns

### Description
Break down the audio module into smaller, focused modules for better organization and maintainability.

### TODO
- [ ] Create `audio_synthesis.py` for basic audio generation (sine waves, silence)
- [ ] Create `audio_effects.py` for audio processing (resampling, clipping)
- [ ] Create `tts_engine.py` to encapsulate text-to-speech logic
- [ ] Refactor `audio.py` to orchestrate these modules

### DONE
- ✅ Created `audio_cache.py` with `AudioCache` class
- ✅ Separated caching logic from audio generation
- ✅ Eliminated global state in `audio.py`

### Impact
Better code organization, easier to test individual components, clearer dependencies.

---

## 2. Type Safety Improvements

### Description
Add comprehensive type hints throughout the codebase for better IDE support and early error detection.

### TODO
- [ ] Add type hints to `TestConfig` class methods
- [ ] Add return type hints to all helper functions
- [ ] Use `TypedDict` for complex dictionary structures
- [ ] Add `Protocol` definitions for dependency injection interfaces
- [ ] Run `mypy` for static type checking
- [ ] Add type checking to CI/CD pipeline

### DONE
- ✅ Added type hints to all functions in `intervals.py`
- ✅ Added type hints to all functions in `audio.py`
- ✅ Added type hints to `AudioCache` class
- ✅ Added `Optional[str]` for nullable parameters

### Impact
Catch type errors at development time, better IDE autocomplete, self-documenting code.

---

## 3. Configuration Management

### Description
Improve configuration handling with validation, file support, and environment variables.

### TODO
- [ ] **[NECESSARY]** Split `TestConfig` class into separate configuration classes to separate functional and technical aspects (e.g., `AudioConfig` for technical audio parameters, `TestScenarioConfig` for functional test parameters)
- [ ] Add JSON/YAML configuration file support
- [ ] Add environment variable support (e.g., `MAS_CACHE_DIR`)
- [ ] Create `ConfigLoader` class for loading from multiple sources
- [ ] Add configuration schema validation (using `pydantic` or `marshmallow`)
- [ ] Support configuration profiles (e.g., "quick", "standard", "comprehensive")
- [ ] Add `--config` CLI flag to load from file

### DONE
- ✅ Added validation in `TestConfig.__init__()`
- ✅ Raises `ConfigurationError` for invalid values
- ✅ Added `_validate_positive()` method
- ✅ Added comprehensive docstrings

### Impact
More flexible configuration, easier deployment, better validation.

---

## 4. Error Handling Improvements

### Description
Enhance error handling with better context, recovery strategies, and user-friendly messages.

### TODO
- [ ] Add retry logic for TTS failures
- [ ] Add graceful degradation (fallback to silence if TTS fails completely)
- [ ] Add error context (which interval, what operation)
- [ ] Add error recovery suggestions in exception messages
- [ ] Add error reporting/telemetry (optional)
- [ ] Add validation for file paths (writable directories, etc.)

### DONE
- ✅ Created custom exception hierarchy (`MASError`, `ConfigurationError`, etc.)
- ✅ Added specific exceptions for different error types
- ✅ Added error handling in `AudioCache` class
- ✅ Added `AudioGenerationError` for file writing failures

### Impact
Better error messages, more robust application, easier debugging.

---

## 5. Dependency Injection

### Description
Implement proper dependency injection for better testability and flexibility.

### TODO
- [ ] Create dependency injection container
- [ ] Use constructor injection for all dependencies
- [ ] Create factory functions for creating configured instances
- [ ] Add interfaces/protocols for mockable dependencies
- [ ] Refactor tests to use dependency injection
- [ ] Consider using a DI framework (e.g., `dependency-injector`)

### DONE
- ✅ `AudioCache` passed as parameter instead of global access
- ✅ `TestConfig` passed to `generate_audio_file()`
- ✅ Removed global state from `audio.py`

### Impact
Easier unit testing, better code modularity, clearer dependencies.

---

## 6. Logging Improvements

### Description
Replace print statements with structured logging throughout the codebase.

### TODO
- [ ] Replace remaining `print()` statements in `print_intervals_table()` with logging
- [ ] Add log levels consistently (DEBUG, INFO, WARNING, ERROR)
- [ ] Add log file output option
- [ ] Add structured logging (JSON format) option
- [ ] Add correlation IDs for tracking operations
- [ ] Add performance logging (timing for each operation)
- [ ] Add log rotation configuration

### DONE
- ✅ Added `logging` module imports to all modules
- ✅ Created logger instances in each module
- ✅ Replaced print() with logger calls in `audio.py`
- ✅ Added logging in `intervals.py`
- ✅ Added `setup_logging()` function in `mas_main.py`
- ✅ Added `--verbose` flag for DEBUG level logging

### Impact
Better production debugging, configurable log levels, structured log analysis.

---

## 7. Testing Improvements

### Description
Expand test coverage and add different types of tests.

### TODO
- [ ] Add unit tests for `AudioCache` class
- [ ] Add unit tests for `TestConfig` validation
- [ ] Add edge case tests (zero values, negative values, very large values)
- [ ] Add integration tests for full workflow
- [ ] Add performance benchmarks (track regression)
- [ ] Add property-based tests (using `hypothesis`)
- [ ] Add test fixtures for common configurations
- [ ] Add mocking for TTS engine in tests
- [ ] Measure and improve code coverage (target: >90%)
- [ ] Add continuous integration tests

### DONE
- ✅ All 21 tests passing (17 intervals, 4 audio)
- ✅ Tests verify cache functionality
- ✅ Tests verify performance improvement (74%)
- ✅ Tests verify results match with/without cache

### Impact
Higher code quality, catch regressions early, confidence in refactoring.

---

## 8. Constants Extraction

### Description
Centralize all magic numbers and configuration values.

### TODO
- [ ] Review all modules for remaining magic numbers
- [ ] Add constants for interval calculation thresholds
- [ ] Add constants for file naming patterns
- [ ] Document the meaning of each constant
- [ ] Consider using `Enum` for categorical constants
- [ ] Add units to constant names (e.g., `DURATION_SECONDS`)

### DONE
- ✅ Created `constants.py` module
- ✅ Extracted `AudioConstants` (sample rate, frequencies, durations)
- ✅ Extracted `SampleLimits` (16-bit audio limits)
- ✅ Extracted `CacheConstants` (cache directory defaults)
- ✅ All audio.py magic numbers replaced with constants

### Impact
Easier configuration changes, self-documenting code, no magic numbers.

---

## 9. Documentation

### Description
Add comprehensive documentation for users and developers.

### TODO
- [ ] Add module-level docstrings to all modules
- [ ] Add class-level docstrings with examples
- [ ] Create developer guide (architecture, design decisions)
- [ ] Create user guide (installation, usage, troubleshooting)
- [ ] Add inline comments for complex algorithms
- [ ] Generate API documentation (using Sphinx)
- [ ] Add README badges (build status, coverage, version)
- [ ] Add CONTRIBUTING.md guide
- [ ] Add examples/ directory with sample scripts
- [ ] Create architecture diagrams

### DONE
- ✅ Added comprehensive docstrings to all functions
- ✅ Added Args/Returns/Raises sections
- ✅ Created `REFACTORING_SUMMARY.md`
- ✅ Created this `TODO.md` file
- ✅ Updated README.md (if exists)

### Impact
Easier onboarding, better maintainability, clearer API usage.

---

## 10. Code Organization

### Description
Improve project structure and organization.

### TODO
- [ ] Move CLI code to separate `cli/` module
- [ ] Create `models/` directory for data classes
- [ ] Create `services/` directory for business logic
- [ ] Create `utils/` directory for helper functions
- [ ] Add `__init__.py` files with public API exports
- [ ] Create `requirements-dev.txt` for development dependencies
- [ ] Add `setup.py` or `pyproject.toml` for packaging
- [ ] Add `.gitignore` file
- [ ] Add `.editorconfig` for consistent formatting
- [ ] Create `scripts/` directory for utility scripts

### DONE
- ✅ Organized code into `src/` directory
- ✅ Created `tests/` directory for tests
- ✅ Separated concerns into modules (audio, intervals, config)
- ✅ Created specialized modules (audio_cache, constants, exceptions)

### Impact
Better project structure, easier navigation, clearer module boundaries.

---

## Additional Future Improvements

### 11. Performance Optimization

#### TODO
- [ ] Profile code to find bottlenecks
- [ ] Optimize audio generation algorithms
- [ ] Use NumPy for array operations (faster than lists)
- [ ] Consider parallel processing for multiple intervals
- [ ] Add memory profiling to prevent leaks
- [ ] Optimize cache storage (compression, binary format)
- [ ] Add lazy loading for large audio files

#### DONE
- ✅ Implemented caching system (74% performance improvement)

---

### 12. Async/Await Support

#### TODO
- [ ] Convert TTS operations to async
- [ ] Add async file I/O operations
- [ ] Use `asyncio` for concurrent audio generation
- [ ] Add progress callbacks for long operations
- [ ] Add cancellation support for long-running operations

#### DONE
- None yet

---

### 13. Progress Indicators

#### TODO
- [ ] Add progress bars using `tqdm` or `rich`
- [ ] Show percentage complete during generation
- [ ] Show estimated time remaining
- [ ] Add visual feedback for cache operations
- [ ] Add colored output for different log levels

#### DONE
- None yet

---

### 14. Audio Quality Improvements

#### TODO
- [ ] Add fade in/fade out for beeps
- [ ] Improve resampling algorithm (use `scipy.signal.resample`)
- [ ] Add anti-aliasing filters
- [ ] Support different audio formats (MP3, OGG)
- [ ] Add audio normalization
- [ ] Add dynamic range compression
- [ ] Test with professional audio quality tools

#### DONE
- ✅ Basic sine wave generation
- ✅ Simple linear interpolation for resampling

---

### 15. CLI Improvements

#### TODO
- [ ] Add `--version` flag
- [ ] Add `--list-voices` to show available TTS voices
- [ ] Add `--preview` mode (generate short sample)
- [ ] Add `--dry-run` to show what would be generated
- [ ] Add `--format` option for output format
- [ ] Add tab completion for bash/zsh
- [ ] Add interactive mode with prompts
- [ ] Add `--quiet` flag to suppress non-error output

#### DONE
- ✅ Comprehensive argparse CLI with 11 options
- ✅ `--help` with clear descriptions
- ✅ `--verbose` flag for debug logging
- ✅ `--output` / `-o` for custom output file
- ✅ `--enable-cache` / `--no-cache` for cache control

---

### 16. CI/CD Pipeline

#### TODO
- [ ] Set up GitHub Actions workflow
- [ ] Add automated testing on push/PR
- [ ] Add code coverage reporting (Codecov)
- [ ] Add linting checks (flake8, pylint)
- [ ] Add type checking (mypy)
- [ ] Add security scanning (bandit)
- [ ] Add automated releases
- [ ] Add version tagging
- [ ] Add changelog generation

#### DONE
- None yet

---

### 17. Pre-commit Hooks

#### TODO
- [ ] Set up pre-commit framework
- [ ] Add black for code formatting
- [ ] Add isort for import sorting
- [ ] Add flake8 for linting
- [ ] Add mypy for type checking
- [ ] Add trailing whitespace removal
- [ ] Add docstring validation
- [ ] Add commit message linting

#### DONE
- None yet

---

### 18. Packaging and Distribution

#### TODO
- [ ] Create `setup.py` with proper metadata
- [ ] Add entry point for command-line usage
- [ ] Publish to PyPI
- [ ] Create Docker image
- [ ] Add installation instructions
- [ ] Create release notes template
- [ ] Add version bumping automation
- [ ] Create distribution packages (wheel, sdist)

#### DONE
- ✅ Basic `setup.py` exists

---

### 19. Audio Format Support

#### TODO
- [ ] Add MP3 export using `pydub`
- [ ] Add OGG export
- [ ] Add FLAC export for lossless quality
- [ ] Add format auto-detection from file extension
- [ ] Add bitrate/quality options
- [ ] Support 24-bit audio
- [ ] Support stereo output

#### DONE
- ✅ WAV format (16-bit, mono, 44.1kHz)

---

### 20. Configuration Profiles

#### TODO
- [ ] Add "beginner" profile (slower speeds, shorter duration)
- [ ] Add "intermediate" profile (medium speeds)
- [ ] Add "advanced" profile (faster speeds, longer duration)
- [ ] Add "custom" profile loaded from file
- [ ] Add `--profile` CLI flag
- [ ] Add profile validation
- [ ] Document each profile's characteristics

#### DONE
- None yet

---

## Priority Matrix

### High Priority (Next Sprint)
1. ✅ Separation of Concerns - AudioCache (DONE)
2. ✅ Type Safety - Core modules (DONE)
3. ✅ Constants Extraction (DONE)
4. ✅ Logging Improvements - Basic setup (DONE)
5. Testing Improvements - Add more tests
6. Documentation - Complete user guide

### Medium Priority (Following Sprints)
7. Configuration Management - File support
8. Error Handling - Retry logic
9. Performance Optimization - NumPy integration
10. CLI Improvements - Version, preview mode
11. Code Organization - Better structure

### Low Priority (Future)
12. Async/Await Support
13. Progress Indicators
14. Audio Quality Improvements
15. CI/CD Pipeline
16. Packaging and Distribution
17. Audio Format Support
18. Configuration Profiles

---

## How to Use This Document

1. **Check TODO items** before starting new work
2. **Move items to DONE** when completed
3. **Add new items** as they are identified
4. **Update priorities** based on user feedback
5. **Link to issues/PRs** for tracking

---

## Recent Completed Work

### Refactoring Sprint (November 2025)
- ✅ Created 3 new modules (audio_cache, constants, exceptions)
- ✅ Refactored 4 existing modules (config, intervals, audio, mas_main)
- ✅ Eliminated all global state
- ✅ Added type hints throughout
- ✅ Added structured logging
- ✅ Added input validation
- ✅ All 21 tests passing
- ✅ Maintained 74% cache performance improvement

---

*Last Updated: November 28, 2025*
