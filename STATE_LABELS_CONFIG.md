# State Labels Script Configuration

## Environment Variables

The `stateLables.py` script now supports the following environment variables:

### Required Configuration
- `MONGO_URL`: MongoDB connection string (defaults to config.py setting)
- `DB_NAME`: Database name (defaults to config.py setting)

### Optional Configuration
- `LABELS_COLLECTION`: Labels collection name (default: "labels")
- `STATES_COLLECTION`: States collection name (default: "states") 
- `STATES_LABELS_JSON`: Path to JSON file (default: "states_with_labels.json")

## Usage Examples

### 1. Using Command Line Arguments (Highest Priority)
```bash
python stateLables.py --mongo-url "mongodb://localhost:27017/" --db-name "india" --json-file "states_with_labels.json"
```

### 2. Using Environment Variables
```bash
export MONGO_URL="mongodb://localhost:27017/"
export DB_NAME="india"
export LABELS_COLLECTION="labels"
export STATES_COLLECTION="states"
export STATES_LABELS_JSON="states_with_labels.json"
python stateLables.py
```

### 3. Using .env File
Create a `.env` file with:
```
MONGO_URL=mongodb://localhost:27017/
DB_NAME=india
LABELS_COLLECTION=labels
STATES_COLLECTION=states
STATES_LABELS_JSON=states_with_labels.json
```

Then run:
```bash
python stateLables.py
```

### 4. Using Defaults from config.py
Just run:
```bash
python stateLables.py
```

### 5. Dry Run Mode (Test without making changes)
```bash
python stateLables.py --dry-run
```

### 6. Help and Options
```bash
python stateLables.py --help
```

## JSON File Format

The script expects a JSON file with this format:
```json
[
  {
    "name": "Maharashtra",
    "labels": ["Culture", "Heritage", "Beaches", "Modern City"]
  },
  {
    "name": "Rajasthan", 
    "labels": ["Desert", "Culture", "Royalty", "Heritage"]
  }
]
```

## Features

- ✅ **Command-line argument support** (highest priority)
- ✅ **Environment variable configuration**
- ✅ **Connection testing** with detailed error messages
- ✅ **Error handling** for all operations
- ✅ **Configurable collection names**
- ✅ **Configurable JSON file path**
- ✅ **Detailed logging** and progress updates
- ✅ **Dry-run mode** for testing without making changes
- ✅ **Graceful error handling** with exit codes
- ✅ **Priority system**: CLI args > env vars > config defaults
