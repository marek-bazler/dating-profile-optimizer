# Dating Profile Optimizer

A comprehensive desktop application that uses local AI models to optimize your dating profile. Upload your photos, provide some basic information about yourself, and let AI help you create an attractive dating profile with the best photo selection and compelling description.

## Features

- **Photo Analysis**: AI-powered analysis of your photos to determine attractiveness scores
- **Smart Photo Selection**: Automatically selects your top 5 photos for dating apps
- **Profile Description Generation**: Creates engaging, personalized dating profile descriptions
- **Local AI Processing**: All processing happens locally for complete privacy
- **Comprehensive Logging**: Detailed logs for troubleshooting and monitoring
- **User-Friendly GUI**: Easy-to-use interface with step-by-step workflow

## AI Models Used

- **Text Generation**: Microsoft DialoGPT for creating engaging profile descriptions
- **Image Analysis**: Salesforce BLIP for photo captioning and analysis
- **Sentiment Analysis**: Cardiff NLP RoBERTa for optimizing content tone

## Installation

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd dating-profile-optimizer
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

### Alternative Installation Methods

**Method 1: Using setup.py (Recommended for development)**
```bash
# Install in development mode (editable install)
pip install -e .

# Run the application
python main.py
# or
dating-profile-optimizer
```

**Method 2: Using the launcher script**
```bash
# Direct execution with launcher
python run.py
```

**Method 3: Using Make (Linux/macOS)**
```bash
# Setup and run in one command
make setup
make run
```

**Method 4: Full development setup**
```bash
# Install with development dependencies
make dev-setup

# Run the application
make run
```

## Testing

The application includes a comprehensive test suite with 80%+ code coverage.

### Running Tests

**Quick test run:**
```bash
python run_tests.py
```

**Using Make (recommended):**
```bash
# Run tests with coverage report
make test-coverage

# Run simple tests
make test

# Setup development environment
make dev-setup
```

**Manual test execution:**
```bash
# Run with pytest (if installed)
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Run custom test runner
python -m tests.test_runner
```

### Test Coverage

The test suite covers:
- **Model Manager**: AI model loading, profile generation, image analysis (90%+ coverage)
- **GUI Components**: User interface logic and interactions (85%+ coverage)
- **Utilities**: Logging, file handling, error management (95%+ coverage)
- **Integration**: End-to-end workflows and data flow (80%+ coverage)

### Test Reports

After running tests with coverage, you can view detailed reports:
- **Terminal**: Coverage summary displayed after test run
- **HTML Report**: Open `htmlcov/index.html` in your browser for detailed coverage

### Development Testing

For development, use the Make commands:
```bash
# Install dev dependencies and run tests
make dev-setup
make test-coverage

# Format and lint code
make format
make lint

# Clean up generated files
make clean
```

## Usage

### Running the Application

**Option 1: Direct execution**
```bash
python main.py
```

**Option 2: Using the launcher script**
```bash
python run.py
```
The `run.py` script provides additional startup logging and error handling.

**Option 3: After installation with setup.py**
```bash
# If installed with pip install -e .
dating-profile-optimizer
```

**Option 4: Using Make commands**
```bash
make run
```

### Application Workflow

#### Step 1: Load AI Models
- Launch the application using any of the methods above
- Go to the "Setup & Models" tab
- Click "Load AI Models" (this may take a few minutes on first run)
- Wait for all models to download and load (~2-3 GB total)

#### Step 2: Upload and Analyze Photos
- Go to the "Photo Selection" tab
- Click "Select Photos" to upload your photos (JPG, PNG, etc.)
- Click "Analyze Photos" to get AI analysis and attractiveness scores
- Review the results and rankings

#### Step 3: Fill Profile Information
- Go to the "Profile Info" tab
- Fill in your basic information (age, occupation, location)
- Add your interests, hobbies, and personality description
- Describe what you're looking for in a partner
- Choose your preferred profile style (humorous, romantic, etc.)
- Click "Save Information"

#### Step 4: Generate Results
- Go to the "Results" tab
- Click "Generate Final Results"
- Review your optimized profile with top 5 photos and AI-generated description
- Click "Export Results" to save to files in the `exports/` directory

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended for better performance)
- **Storage**: 5GB free space for models and data
- **GPU**: Optional but recommended for faster processing

## Privacy & Security

- All processing is done locally on your machine
- No data is sent to external servers
- Your photos and information remain completely private
- Models are downloaded once and stored locally

## Troubleshooting

### Common Issues

1. **Models fail to load**:
   - Ensure you have sufficient RAM and storage space
   - Check your internet connection for initial model downloads
   - Review logs in the "Setup & Models" tab

2. **Photo analysis errors**:
   - Ensure photos are in supported formats (JPG, PNG, etc.)
   - Check that image files are not corrupted
   - Try with smaller image files if memory issues occur

3. **Performance issues**:
   - Close other applications to free up RAM
   - Consider using GPU acceleration if available
   - Process fewer photos at once

### Logs

Application logs are automatically saved in the `logs/` directory with timestamps. Check these files for detailed error information and troubleshooting.

## File Structure

```
dating-profile-optimizer/
├── main.py                 # Main application entry point
├── run.py                  # Alternative launcher with enhanced logging
├── setup.py               # Package installation and distribution setup
├── run_tests.py           # Test runner script
├── requirements.txt        # Python dependencies
├── test_requirements.txt   # Testing dependencies
├── Makefile               # Build, test, and development commands
├── pytest.ini             # Test configuration
├── .gitignore             # Git ignore rules
├── README.md              # This documentation
├── src/                   # Source code
│   ├── __init__.py
│   ├── gui/               # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window
│   │   ├── model_loader.py     # AI model loading interface
│   │   ├── photo_selector.py   # Photo upload and analysis
│   │   └── profile_generator.py # Profile information input
│   ├── models/            # AI model management
│   │   ├── __init__.py
│   │   └── model_manager.py    # Core AI model handling
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── logger.py           # Logging configuration
├── tests/                 # Comprehensive test suite
│   ├── __init__.py
│   ├── test_logger.py          # Logger utility tests
│   ├── test_model_manager.py   # AI model tests
│   ├── test_gui_components.py  # GUI component tests
│   ├── test_main_app.py        # Main application tests
│   ├── test_integration.py     # Integration tests
│   ├── test_photo_selector_advanced.py # Advanced PhotoSelector tests
│   └── test_runner.py          # Custom test runner
├── logs/                  # Application logs (auto-generated)
├── exports/               # Generated results (auto-generated)
├── models/                # Downloaded AI models (auto-generated)
└── htmlcov/               # Coverage reports (generated by tests)
```

### Key Files Explained

- **`main.py`**: Primary application entry point with basic error handling
- **`run.py`**: Enhanced launcher with detailed startup logging and path management
- **`setup.py`**: Package configuration for installation, distribution, and console scripts
- **`Makefile`**: Development commands for testing, formatting, and project management

## Package Management

### Using setup.py

The `setup.py` file provides professional package management:

**Development Installation:**
```bash
# Install in editable/development mode
pip install -e .

# This allows you to:
# - Run the app with: dating-profile-optimizer
# - Make code changes without reinstalling
# - Use the package in other Python projects
```

**Production Installation:**
```bash
# Install as a regular package
pip install .

# Or build and install from wheel
python setup.py bdist_wheel
pip install dist/dating_profile_optimizer-1.0.0-py3-none-any.whl
```

**Package Information:**
- Package name: `dating-profile-optimizer`
- Version: `1.0.0`
- Console script: `dating-profile-optimizer` command
- Python compatibility: 3.8+

### Using run.py

The `run.py` launcher provides enhanced startup:

```bash
python run.py
```

**Features:**
- Enhanced error handling and user-friendly messages
- Automatic path configuration for imports
- Startup logging and diagnostics
- Graceful handling of keyboard interrupts

## Development

### Code Quality

The project maintains high code quality standards:
- **80%+ test coverage** across all components
- **Comprehensive error handling** and logging
- **Modular architecture** for easy maintenance
- **Type hints** and documentation throughout

### Development Workflow

**Setup development environment:**
```bash
# Clone and setup
git clone <repository-url>
cd dating-profile-optimizer

# Install in development mode
pip install -e .

# Install development dependencies
make dev-setup
```

**Development commands:**
```bash
# Run the application
make run
# or
python run.py
# or
dating-profile-optimizer

# Run tests with coverage
make test-coverage

# Format code
make format

# Lint code
make lint

# Clean generated files
make clean
```

### Contributing

This is a personal project focused on helping users create better dating profiles while maintaining complete privacy through local AI processing.

If you want to contribute:
1. Fork the repository
2. Create a feature branch
3. Install in development mode: `pip install -e .`
4. Add tests for new functionality
5. Ensure all tests pass: `make test-coverage`
6. Format code: `make format`
7. Submit a pull request

### Testing Guidelines

When adding new features:
- Write unit tests with 80%+ coverage
- Include integration tests for new workflows
- Test error conditions and edge cases
- Mock external dependencies (GUI, AI models)
- Update documentation

## License

This project is for personal use. Please respect the terms of service of the AI models used.

## Disclaimer

This application is designed to help optimize dating profiles using AI analysis. Results may vary, and the effectiveness of generated content depends on many factors. Always review and personalize the generated content before using it on dating platforms.