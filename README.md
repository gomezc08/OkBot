# OkBot

A comprehensive UI Automation (UIA) bot framework that combines C# UIA listeners with AI-powered JSON schema generation for intelligent UI automation and testing.

## 🚀 Features

- **UIA Event Listener**: C# application that captures UI automation events in real-time
- **AI-Powered Schema Generation**: Uses OpenAI GPT models to automatically generate JSON schemas from UIA event data
- **Intelligent Event Analysis**: Automatically infers data structures and validation rules
- **Cross-Platform Support**: Works on Windows with .NET Framework
- **Extensible Architecture**: Modular design for easy customization and extension

## 🛠️ Prerequisites

- **Python 3.7+** with pip
- **.NET Framework 4.7.2+** (for UIA listener)
- **OpenAI API Key** for schema generation
- **Windows OS** (required for UIA automation)

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd OkBot
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# or
.\venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 Usage

### Generate JSON Schema from UIA Data

1. **Prepare UIA Event Data**: Place your UIA log files in `src/create_json_schema/resources/`
   - `uia_log.json` - Raw UIA event data
   - `listener_data_examples.json` - Example event structures
   - `format_templates.md` - Format specifications

2. **Run Schema Generation**:
```bash
# From project root
python .\src\create_json_schema\generate_json_schema.py

# Or from the script directory
cd src/create_json_schema
python generate_json_schema.py
```

3. **Generated Output**: The script will create:
   - `generated_schema.json` - Complete JSON Schema (Draft 2020-12)
   - `result.json` - Full API response for debugging

### UIA Event Listener

1. **Build the C# Project**:
```bash
cd src/uia_listener
dotnet build
```

2. **Run the Listener**:
```bash
dotnet run
```

## 📋 Generated Schema Features

The AI-generated JSON schema includes:

- **Event Type Validation**: StructureChanged, Focus, PropertyChanged
- **Conditional Requirements**: Different required fields based on event type
- **Type Safety**: Proper data type definitions and constraints
- **Pattern Validation**: Regex patterns for control types and properties
- **Comprehensive Coverage**: All major UIA event properties and structures

## 🔧 Configuration

### OpenAI API Settings
- **Model**: gpt-4o-mini (configurable in `generate_json_schema.py`)
- **Temperature**: 0.1 (focused, deterministic output)
- **Max Tokens**: 4000 (adjustable for complex schemas)

### Schema Requirements
Customize schema generation by editing `src/create_json_schema/resources/schema_requirements.md`

## 🧪 Testing

Test the generated schema with your UIA event data:
```python
import json
from jsonschema import validate 

# Load your schema and data
with open('generated_schema.json') as f:
    schema = json.load(f)

with open('your_uia_events.json') as f:
    events = json.load(f)

# Validate
validate(instance=events, schema=schema)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Support

For issues and questions:
- Check the generated logs and error messages
- Verify your OpenAI API key and quota
- Ensure all required files are present in the resources directory

## 🔮 Future Enhancements

- [ ] Support for additional UIA event types
- [ ] Real-time schema validation
- [ ] Integration with UI testing frameworks
- [ ] Cross-platform UIA support
- [ ] Schema versioning and migration tools
