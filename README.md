### Using a Virtual Environment (Recommended)
1. Create a virtual environment:

```bash
python3 -m venv venv
```

2. Activate it:
- On macOS/Linux:
```bash
source venv/bin/activate
```
- On Windows:
```bash
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Requirements
Install required Python packages:

```bash
pip install -r requirements.txt
```

### Usage

Run normally
```bash
python3 dl.py --max-pages 3
```

Run in dry mode
```bash
python3 dl.py --dry-run --max-pages 3
```
