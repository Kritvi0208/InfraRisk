# NLP & Contract Intelligence API Documentation

## Phase 4: Complete NLP Module for InfraRisk AI

### Table of Contents
1. [Overview](#overview)
2. [Document Parsing (LayoutLM)](#document-parsing-layoutlm)
3. [Named Entity Recognition (NER)](#named-entity-recognition-ner)
4. [Legal-BERT Clause Classification](#legal-bert-clause-classification)
5. [Risk Scoring](#risk-scoring)
6. [Benchmark Database](#benchmark-database)
7. [End-to-End Example](#end-to-end-example)

---

## Overview

The NLP module provides comprehensive infrastructure contract analysis through:
- **Document Parsing**: Extract structured information from PDFs with clause hierarchy
- **Entity Recognition**: Identify sponsors, lenders, amounts, dates
- **Clause Classification**: Categorize into 12 risk classes
- **Risk Scoring**: Assess severity and aggregate to project level
- **Benchmarking**: Compare against 1,000+ comparable transactions

**Module**: `nlp_module.py`
**Python**: 3.8+
**Dependencies**: `transformers`, `spacy`, `pdfplumber` (optional)

---

## Document Parsing (LayoutLM)

### Class: `LayoutLMParser`

Parses infrastructure contracts with spatial layout preservation and clause hierarchy.

#### Initialization
```python
from nlp_module import LayoutLMParser

parser = LayoutLMParser(verbose=True)
```

#### Methods

##### `load_pdf_document(path: str) -> str`
Load and extract text from PDF or text file.

**Parameters:**
- `path` (str): File path to PDF or text document

**Returns:**
- Document text as string

**Example:**
```python
text = parser.load_pdf_document("contract.pdf")
print(f"Loaded {len(text)} characters")
```

##### `extract_sections() -> Dict[str, Section]`
Identify contract sections (Definitions, Terms, Covenants).

**Returns:**
- Dictionary with section keys and Section objects

**Example:**
```python
sections = parser.extract_sections()
for section_key, section in sections.items():
    print(f"{section_key}: {section.title}")
```

##### `resolve_nested_clauses() -> Dict[str, Clause]`
Handle nested clause numbering like "14.3(b)(ii)".

**Returns:**
- Dictionary with clause keys and Clause objects

**Example:**
```python
clauses = parser.resolve_nested_clauses()
print(f"Found {len(clauses)} clauses")
```

##### `build_clause_graph() -> Dict[str, List[str]]`
Create cross-reference network between clauses.

**Returns:**
- Dictionary mapping clause to referenced clauses

**Example:**
```python
references = parser.build_clause_graph()
# Shows which clauses reference which others
```

##### `extract_entity_regions() -> List[EntityRegion]`
Identify entities: sponsor, lender, amounts, dates, locations.

**Returns:**
- List of EntityRegion objects with confidence scores

**Example:**
```python
entities = parser.extract_entity_regions()
for entity in entities:
    print(f"{entity.entity_type}: {entity.text} ({entity.confidence:.2f})")
```

##### `to_json() -> str`
Export parsed structure to JSON.

**Returns:**
- JSON string with complete document structure

##### `get_clause_by_number(clause_number: str) -> Optional[Clause]`
Retrieve specific clause by number.

**Parameters:**
- `clause_number` (str): Clause identifier (e.g., "14.3(b)")

**Returns:**
- Clause object or None

##### `get_entities_by_type(entity_type: str) -> List[EntityRegion]`
Filter entities by type.

**Parameters:**
- `entity_type` (str): "SPONSOR", "LENDER", "AMOUNT", "DATE", "LOCATION"

**Returns:**
- List of matching entities

---

## Named Entity Recognition (NER)

### Class: `ContractNER`

Custom NER for infrastructure contracts with transformer support.

#### Initialization
```python
from nlp_module import ContractNER

ner = ContractNER(use_transformer=True)
```

#### Methods

##### `train_custom_ner(training_data: List[Tuple[str, Dict]]) -> float`
Train on labeled contract corpus.

**Parameters:**
- `training_data`: List of (text, entities) tuples

**Returns:**
- Training accuracy (F1 score)

**Example:**
```python
data = [
    ("ABC Infrastructure Inc", {"entities": [(0, 22, "SPONSOR")]}),
    ("Development Bank", {"entities": [(0, 16, "LENDER")]}),
]
accuracy = ner.train_custom_ner(data)
print(f"Accuracy: {accuracy:.4f}")  # Target: >0.85
```

##### `extract_sponsors(text: str) -> List[Tuple[str, float]]`
Extract sponsor/company names.

**Parameters:**
- `text` (str): Contract text

**Returns:**
- List of (sponsor_name, confidence) tuples

**Example:**
```python
sponsors = ner.extract_sponsors(contract_text)
# [("ABC Solar Inc", 0.95), ("XYZ Power Ltd", 0.92)]
```

##### `extract_lenders(text: str) -> List[Tuple[str, float]]`
Extract lender information.

**Returns:**
- List of (lender_name, confidence) tuples

##### `extract_amounts(text: str) -> List[Tuple[str, str, float]]`
Extract financial amounts with currency.

**Returns:**
- List of (amount, currency, confidence) tuples

**Example:**
```python
amounts = ner.extract_amounts(text)
# [("250", "USD", 0.88), ("100", "EUR", 0.92)]
```

##### `extract_dates(text: str) -> List[Tuple[str, str, float]]`
Extract milestone dates.

**Returns:**
- List of (date, date_type, confidence) tuples

##### `extract_project_details(text: str) -> List[Tuple[str, str, float]]`
Extract location and sector.

**Returns:**
- List of (location, sector, confidence) tuples

##### `extract_all(text: str) -> EntityExtraction`
Complete extraction.

**Returns:**
- EntityExtraction object with all entities

**Example:**
```python
extraction = ner.extract_all(contract_text)
print(f"Sponsors: {extraction.sponsors}")
print(f"Lenders: {extraction.lenders}")
print(f"Amounts: {extraction.amounts}")
```

---

## Legal-BERT Clause Classification

### Class: `LegalBERTClassifier`

Classify clauses into 12 infrastructure risk categories.

#### Initialization
```python
from nlp_module import LegalBERTClassifier

classifier = LegalBERTClassifier()
```

#### Clause Categories (12)

| ID | Category | Risk Level |
|----|----------|-----------|
| 1 | Force Majeure | High |
| 2 | Termination Rights | High |
| 3 | Change of Law | Medium |
| 4 | Refinancing Provisions | Low |
| 5 | Covenant Violations | High |
| 6 | Parent Company Guarantees | High |
| 7 | Subordination | Critical |
| 8 | Step-Down Provisions | Low |
| 9 | Buyout Options | Low |
| 10 | Put/Call Rights | Low |
| 11 | Dispute Resolution | Medium |
| 12 | Default Definitions | High |

#### Methods

##### `load_pretrained_legal_bert() -> bool`
Load pre-trained Legal-BERT model.

**Returns:**
- True if successful

##### `fine_tune_on_infrastructure_contracts(training_data, epochs=3) -> Dict`
Fine-tune on infrastructure corpus.

**Parameters:**
- `training_data`: List of (text, label_id) tuples
- `epochs`: Training epochs (default: 3)

**Returns:**
- Metrics dictionary with F1, accuracy, loss

**Example:**
```python
data = [
    ("Perpetual force majeure clause", 1),
    ("Termination rights for sponsor", 2),
    ("Financial covenant DSCR > 1.25", 5),
]
metrics = classifier.fine_tune_on_infrastructure_contracts(data)
print(f"F1 Score: {metrics['f1_score']:.4f}")  # Target: >0.92
```

##### `classify_clause(text: str) -> Tuple[int, str, float]`
Classify single clause.

**Parameters:**
- `text` (str): Clause text

**Returns:**
- (label_id, category_name, confidence) tuple

**Example:**
```python
label_id, category, confidence = classifier.classify_clause(
    "The Sponsor must maintain DSCR above 1.25x at all times"
)
print(f"{category}: {confidence:.2f}")  # Covenant Violations: 0.95
```

##### `classify_batch(texts: List[str]) -> List[Tuple[int, str, float]]`
Classify multiple clauses.

**Returns:**
- List of classification tuples

---

## Risk Scoring

### Class: `ContractRiskScorer`

Score clauses and aggregate to project level (1-5 scale).

#### Severity Scale

| Score | Level | Description |
|-------|-------|------------|
| 5 | Critical | Deal-blocking risk |
| 4 | High | Highly restrictive |
| 3 | Medium | Standard terms |
| 2 | Low | Favorable terms |
| 1 | Minimal | Highly favorable |

#### Initialization
```python
from nlp_module import ContractRiskScorer

scorer = ContractRiskScorer()
```

#### Methods

##### `score_clause(category_id: int, text: str) -> int`
Score individual clause (1-5).

**Parameters:**
- `category_id`: Clause category ID (1-12)
- `text`: Clause text

**Returns:**
- Severity score 1-5

**Example:**
```python
score = scorer.score_clause(7, "Perpetual subordination of equity")
# Returns 5 (Deal-blocking)
```

##### `aggregate_project_risk(clause_scores: Dict) -> float`
Aggregate to project level.

**Parameters:**
- `clause_scores`: Dict mapping category_id to list of scores

**Returns:**
- Weighted project risk (1-5)

**Example:**
```python
scores = {
    1: [4, 4],        # Force majeure
    5: [4, 3, 4],     # Covenants
    7: [5],           # Subordination
}
project_risk = scorer.aggregate_project_risk(scores)
print(f"Project Risk: {project_risk:.2f}")  # 4.12
```

##### `flag_covenants(clauses: List[Tuple[int, str]]) -> List[Dict]`
Identify restrictive covenants.

**Returns:**
- List of flagged covenants with details

##### `identify_bottleneck_terms(clauses: List[Tuple[int, str]]) -> List[Dict]`
Identify financing bottlenecks.

**Returns:**
- List of bottleneck terms

##### `generate_risk_report(clause_scores: Dict) -> Dict`
Generate complete risk report.

**Returns:**
- Report with project score, breakdown, and key risks

**Example:**
```python
report = scorer.generate_risk_report(scores)
print(f"Overall Risk: {report['project_risk_score']}")
print(f"Level: {report['risk_level']}")
for risk in report['key_risks']:
    print(f"  - {risk['category']}: {risk['action']}")
```

---

## Benchmark Database

### Class: `BenchmarkDatabase`

Maintain and query 1,000+ comparable transactions.

#### Initialization
```python
from nlp_module import BenchmarkDatabase

db = BenchmarkDatabase("benchmarks.db")
```

#### Methods

##### `load_transaction_benchmarks(sample_size: int = 1000) -> int`
Load benchmark transactions.

**Parameters:**
- `sample_size`: Number of transactions to load

**Returns:**
- Number successfully loaded

**Example:**
```python
count = db.load_transaction_benchmarks(sample_size=1000)
print(f"Loaded {count} benchmarks")
```

##### `extract_benchmark_terms(transaction_id: int) -> Dict`
Extract key terms from transaction.

**Returns:**
- Dictionary with debt, tenor, spread, DSCR, etc.

##### `compare_against_benchmark(current_contract: Dict) -> Dict`
Compare contract against benchmarks.

**Parameters:**
- `current_contract`: Dict with project_sector, debt_tenor, etc.

**Returns:**
- Comparison with deviations

**Example:**
```python
contract = {
    "project_sector": "Solar",
    "debt_tenor": 22,
    "debt_amount": 200,
}
comparison = db.compare_against_benchmark(contract)
for deviation in comparison['deviations']:
    print(f"{deviation['metric']}: "
          f"{deviation['deviation_percent']:.1f}% "
          f"{deviation['status']}")
```

##### `compute_term_statistics() -> Dict`
Compute benchmark statistics.

**Returns:**
- Distribution statistics for all key terms

**Example:**
```python
stats = db.compute_term_statistics()
print(f"Avg Debt: ${stats['debt_amount']['average']}M")
print(f"Avg Tenor: {stats['debt_tenor']['average']} years")
print(f"Avg Spread: {stats['spread_bps']['average']} bps")
```

##### `close()`
Close database connection.

---

## End-to-End Example

Complete pipeline from document to risk assessment:

```python
from nlp_module import (
    LayoutLMParser, ContractNER, LegalBERTClassifier,
    ContractRiskScorer, BenchmarkDatabase
)

# 1. Parse Document
parser = LayoutLMParser(verbose=True)
text = parser.load_pdf_document("contract.pdf")
sections = parser.extract_sections()
clauses = parser.resolve_nested_clauses()
entities = parser.extract_entity_regions()

print(f"✓ Extracted {len(sections)} sections, {len(clauses)} clauses")

# 2. Extract Entities
ner = ContractNER()
extraction = ner.extract_all(text)

print(f"✓ Found {len(extraction.sponsors)} sponsors")
print(f"✓ Found {len(extraction.lenders)} lenders")
print(f"✓ Found {len(extraction.amounts)} amounts")

# 3. Classify Clauses
classifier = LegalBERTClassifier()
clause_classifications = {}

for clause_key, clause in clauses.items():
    label_id, category, confidence = classifier.classify_clause(clause.text)
    if label_id not in clause_classifications:
        clause_classifications[label_id] = []
    clause_classifications[label_id].append(confidence)

print(f"✓ Classified {len(clauses)} clauses")

# 4. Score Risks
scorer = ContractRiskScorer()

# Build clause severity scores
clause_scores = {}
for clause_key, clause in clauses.items():
    label_id, _, _ = classifier.classify_clause(clause.text)
    severity = scorer.score_clause(label_id, clause.text)
    
    if label_id not in clause_scores:
        clause_scores[label_id] = []
    clause_scores[label_id].append(severity)

# Generate risk report
report = scorer.generate_risk_report(clause_scores)

print(f"\n{'='*50}")
print(f"PROJECT RISK ASSESSMENT")
print(f"{'='*50}")
print(f"Overall Risk Score: {report['project_risk_score']:.2f}/5.0")
print(f"Risk Level: {report['risk_level']}")
print(f"\nCategory Breakdown:")
for category, details in report['category_breakdown'].items():
    print(f"  {category}:")
    print(f"    Avg Severity: {details['average_severity']:.2f}")
    print(f"    Weight: {details['weight']:.1%}")

if report['key_risks']:
    print(f"\nKey Risks Identified:")
    for risk in report['key_risks']:
        print(f"  ⚠ {risk['category']}: {risk['action']}")

# 5. Compare Against Benchmarks
db = BenchmarkDatabase("benchmarks.db")
db.load_transaction_benchmarks(sample_size=1000)

current_contract = {
    "project_sector": extraction.projects[0][1] if extraction.projects else "Solar",
    "debt_tenor": 20,
    "debt_amount": 200,
}

comparison = db.compare_against_benchmark(current_contract)
print(f"\nBenchmark Comparison ({comparison['benchmark_count']} transactions):")
for deviation in comparison['deviations']:
    print(f"  {deviation['metric']}: "
          f"{deviation['deviation_percent']:+.1f}% "
          f"[{deviation['status']}]")

db.close()

print(f"\n✓ Complete pipeline executed successfully!")
```

---

## Performance Metrics

### Target Accuracies
- **NER F1 Score**: > 0.85
- **Clause Classification F1 Score**: > 0.92
- **Benchmark Database**: 1,000+ transactions
- **End-to-End Processing**: < 30 seconds per contract

### Supported Languages
- English (primary)
- Can be extended to other languages

### Contract Types Supported
- Project Finance Agreements
- Loan Agreements
- Guarantees and Securities
- Technical Specifications
- Operations & Maintenance Contracts

---

## Error Handling

All classes include robust error handling:

```python
try:
    parser = LayoutLMParser()
    text = parser.load_pdf_document("contract.pdf")
except FileNotFoundError:
    print("Contract file not found")
except Exception as e:
    print(f"Error: {str(e)}")

try:
    db = BenchmarkDatabase("benchmarks.db")
    stats = db.compute_term_statistics()
finally:
    db.close()
```

---

## Advanced Configuration

### Custom Weights for Risk Scoring
```python
scorer = ContractRiskScorer()
# Modify weights for specific use cases
scorer.clause_weights[7] = 0.25  # Increase subordination weight
project_risk = scorer.aggregate_project_risk(clause_scores)
```

### Transformer Model Selection
```python
classifier = LegalBERTClassifier(
    model_name="legal-bert-base-uncased",  # Different BERT model
    num_labels=12
)
```

### Database Queries
```python
db = BenchmarkDatabase("benchmarks.db")
# Query by sector
db.cursor.execute(
    "SELECT AVG(spread_bps) FROM transactions WHERE project_sector = ?",
    ("Solar",)
)
avg_spread = db.cursor.fetchone()[0]
```

---

## API Version
**v1.0.0** - Phase 4 Release

## Last Updated
2024

## Support
For issues or questions, refer to DAY4_PROGRESS.md and test suite examples.
