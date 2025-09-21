# Seeds

Database seeding and document processing scripts.

## Available Scripts

### Database Seeding
- `seed_database.py` - Main database seeding script
- `seed_data.py` - Alternative seeding approach
- `simple_seed.py` - Simple seed data creation

### Document Processing
- `process_single.py` - Process individual funding documents
- `process_batch.py` - Batch process multiple documents
- `process_documents.py` - Main document processing script
- `process_docs.py` - Alternative document processor
- `process_docs_fixed.py` - Fixed version of document processor

## Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Seed database with funding programs
python seeds/seed_database.py

# Process documents for a specific funding program
python seeds/process_single.py "Funding Program Name"

# Process all documents
python seeds/process_batch.py
```

## Data Location

Documents should be placed in the `data/` directory with the following structure:
```
data/
├── funding_program_1/
│   ├── document1.pdf
│   └── document2.pdf
└── funding_program_2/
    └── document.pdf
```
