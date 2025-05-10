# tinypilot
![TinyPilot Main Interface](assets/main-tinypilot.png)

Local app that helps you learn [TinyGrad](https://github.com/tinygrad/tinygrad) and updates you on the bounties!

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script to update and index all data:
```bash
python main.py
```

This will:
1. Update the tinygrad repository
2. Update available bounties
3. Scrape tutorials
4. Index and embed all data for semantic search

## Dependencies

- chromadb: Vector database for storing embeddings
- sentence-transformers: For generating text embeddings
- beautifulsoup4: For web scraping
- trafilatura: For content extraction
- pandas: For data handling
- requests: For HTTP requests