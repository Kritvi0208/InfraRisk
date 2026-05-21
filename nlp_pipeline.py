"""
End-to-End NLP Pipeline Example for InfraRisk AI
Complete workflow from contract document to risk assessment

Usage:
    python nlp_pipeline.py [contract_file.pdf]
"""

import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import NLP modules
from nlp_module import (
    CLAUSE_CATEGORIES,
    BenchmarkDatabase,
    ContractNER,
    ContractRiskScorer,
    LayoutLMParser,
    LegalBERTClassifier,
)


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}")


def create_sample_contract():
    """Create a sample contract for demonstration"""
    return """
    INFRASTRUCTURE PROJECT FINANCE AGREEMENT

    This Agreement entered into this 1st day of June, 2024

    PARTIES:
    - Sponsor: ABC Solar Energy Private Limited
    - Lender: Development Finance Corporation
    - Project Location: Tamil Nadu, India

    ARTICLE 1: DEFINITIONS

    1.1 "Sponsor" means ABC Solar Energy Private Limited, a company registered
    in India with corporate office at Bangalore.

    1.2 "Lender" means Development Finance Corporation, a multilateral
    development finance institution.

    1.3 "Project" means the 500 MW solar power generation facility located
    in Tamil Nadu, India with estimated capital cost of USD 300 Million.

    ARTICLE 2: FINANCING STRUCTURE

    2.1 Total Project Cost: USD 300 Million
    2.2 Senior Debt: USD 200 Million
    2.3 Equity Investment: USD 100 Million
    2.4 Financial Close: June 30, 2024

    SECTION 3: CREDIT TERMS

    3.1 Debt Tenor: 20 years (360 months)
    3.2 Interest Rate: SOFR + 2.5% per annum
    3.3 Spread: 250 basis points over SOFR
    3.4 Repayment: Annual bullet at end of tenor

    SECTION 4: FINANCIAL COVENANTS

    4.1 DSCR Maintenance: Borrower must maintain minimum DSCR of 1.25x
    throughout the loan tenor. Quarterly testing required.

    4.2 Debt Service Reserve Account: Borrower shall establish and maintain
    DSRA equal to 6 months of debt service.

    4.3 Interest Coverage Ratio: Borrower must maintain ICR above 2.5x
    calculated on annual basis.

    ARTICLE 5: FORCE MAJEURE

    5.1 Force Majeure Events: Subject to perpetual force majeure clause
    with unlimited scope including but not limited to:
    - Natural disasters and acts of god
    - War, terrorism, civil unrest
    - Pandemics and epidemics
    - Government actions and regulatory changes

    5.2 Effect of Force Majeure: Borrower may defer payment obligations
    without penalty during force majeure event of unlimited duration.

    ARTICLE 6: SUBORDINATION

    6.1 Equity Subordination: All equity contributions shall be
    perpetually subordinated to senior debt in the capital structure.

    6.2 No Step-Down: Equity shall remain subordinated throughout the
    entire loan tenor with no provisions for step-down or reduction.

    ARTICLE 7: GUARANTEES

    7.1 Parent Company Guarantee: Sponsor shall provide irrevocable
    guarantee covering all obligations throughout the tenor.

    7.2 Scope: Guarantee covers 100% of outstanding debt, accrued interest,
    and all costs and expenses.

    ARTICLE 8: TERMINATION RIGHTS

    8.1 Lender Termination: Lender may terminate upon any material breach
    of contract, covenant violation, or material adverse change in
    project performance.

    8.2 Sponsor Termination: Sponsor has limited early exit rights,
    subject to prepayment premium of 2% of outstanding debt.

    ARTICLE 9: CHANGE OF LAW

    9.1 The Project is subject to all changes in Indian law, regulations,
    and taxation. Any adverse change in law shall be borne entirely by
    the Borrower.

    ARTICLE 10: DISPUTE RESOLUTION

    10.1 Disputes shall be resolved through ICC Arbitration under
    English Law and London seat.

    10.2 Binding arbitration with single arbitrator for disputes under
    USD 5 Million, three arbitrators for larger disputes.

    ARTICLE 11: DEFAULT PROVISIONS

    11.1 Material Default: Failure to pay any amount when due; breach of
    financial covenants; material misrepresentation; insolvency or
    bankruptcy.

    11.2 Default Interest: Upon default, interest rate increases by 200
    basis points per annum.

    11.3 Acceleration: Upon default, entire outstanding debt becomes
    immediately due and payable.

    ARTICLE 12: REFINANCING

    12.1 Refinancing Provisions: Limited refinancing rights available only
    after Year 15, subject to approval and minimum DSCR of 1.5x.

    12.2 Prepayment: Early prepayment allowed with 2% penalty in Years
    1-10, 1.5% in Years 11-15, no penalty after Year 15.

    ARTICLE 13: STEP-DOWN PROVISIONS

    13.1 Optional Step-Down: Step-down of DSCR requirement from 1.25x to
    1.15x available after Year 10, subject to lender discretion and
    minimum debt service coverage of 1.5x.

    13.2 Conditions: Step-down conditioned on no covenant breach in prior
    3 years and maintenance of senior debt without material adverse changes.

    ARTICLE 14: BUYOUT OPTIONS

    14.1 Sponsor Buyout: Sponsor may buyout equity stake at any time at
    fair market value, subject to lender approval and minimum DSCR of 1.25x.

    14.2 Put/Call Rights: Call option allows sponsor to purchase lender
    interest after Year 8 at discounted rate if all covenants maintained.

    ARTICLE 15: EFFECTIVE DATE

    This Agreement shall be effective from June 1, 2024 and continue for
    the full tenor of the facility.

    IN WITNESS WHEREOF, the parties have executed this Agreement.

    For ABC Solar Energy Private Limited:
    _____________________________
    Date: June 1, 2024

    For Development Finance Corporation:
    _____________________________
    Date: June 1, 2024
    """


class NLPPipeline:
    """Complete NLP processing pipeline"""

    def __init__(self):
        """Initialize all components"""
        self.parser = LayoutLMParser(verbose=False)
        self.ner = ContractNER()
        self.classifier = LegalBERTClassifier()
        self.scorer = ContractRiskScorer()
        self.benchmark_db = None

    def process_contract(self, contract_text):
        """Process contract through complete pipeline"""

        print_header("PHASE 1: DOCUMENT PARSING")
        logger.info("Starting document parsing...")

        # Parse document
        self.parser.document_text = contract_text
        sections = self.parser.extract_sections()
        clauses = self.parser.resolve_nested_clauses()
        self.parser.build_clause_graph()
        entities = self.parser.extract_entity_regions()

        print(f"✓ Extracted {len(sections)} sections")
        print(f"✓ Identified {len(clauses)} clauses")
        print(f"✓ Found {len(entities)} entity references")

        print_section("Sections Identified")
        for section_key, section in list(sections.items())[:5]:
            print(f"  • {section_key}: {section.title}")

        print_section("Sample Entities")
        for entity in entities[:8]:
            print(f"  • [{entity.entity_type}] {entity.text} ({entity.confidence:.2f})")

        # Save parsing results
        with open("phase1_parsing.json", "w") as f:
            f.write(self.parser.to_json())
        print(f"\n✓ Parsing results saved to phase1_parsing.json")

        print_header("PHASE 2: ENTITY EXTRACTION")
        logger.info("Extracting named entities...")

        extraction = self.ner.extract_all(contract_text)

        print_section("Sponsors Identified")
        for sponsor, confidence in extraction.sponsors:
            print(f"  • {sponsor} ({confidence:.2%})")

        print_section("Lenders Identified")
        for lender, confidence in extraction.lenders:
            print(f"  • {lender} ({confidence:.2%})")

        print_section("Financial Amounts")
        for amount, currency, confidence in extraction.amounts[:10]:
            print(f"  • {currency} {amount} ({confidence:.2%})")

        print_section("Key Dates")
        for date, date_type, confidence in extraction.dates[:5]:
            print(f"  • {date} ({date_type})")

        # Save extraction results
        extraction_dict = self.ner.to_dict(extraction)
        with open("phase2_extraction.json", "w") as f:
            json.dump(extraction_dict, f, indent=2)
        print(f"\n✓ Extraction results saved to phase2_extraction.json")

        print_header("PHASE 3: CLAUSE CLASSIFICATION")
        logger.info("Classifying clauses...")

        clause_classifications = {}
        classification_details = []

        for clause_key, clause in clauses.items():
            label_id, category, confidence = self.classifier.classify_clause(
                clause.text
            )

            if label_id not in clause_classifications:
                clause_classifications[label_id] = []
            clause_classifications[label_id].append(confidence)

            classification_details.append(
                {
                    "clause_id": clause_key,
                    "clause_number": clause.number,
                    "category_id": label_id,
                    "category": category,
                    "confidence": confidence,
                    "text_preview": clause.text[:80],
                }
            )

        print(f"✓ Classified {len(clauses)} clauses")

        print_section("Classification Summary by Category")
        for category_id in sorted(clause_classifications.keys()):
            category_name = CLAUSE_CATEGORIES.get(category_id, "Unknown")
            confidences = clause_classifications[category_id]
            avg_confidence = sum(confidences) / len(confidences)
            print(
                f"  • [{category_id:2d}] {category_name:30s} "
                f"Count: {len(confidences):2d}, Avg Conf: {avg_confidence:.2%}"
            )

        # Save classification results
        with open("phase3_classification.json", "w") as f:
            json.dump(classification_details, f, indent=2)
        print(f"\n✓ Classification results saved to phase3_classification.json")

        print_header("PHASE 4: RISK SCORING")
        logger.info("Scoring contract risks...")

        # Build clause severity scores
        clause_scores = {}
        score_details = []

        for clause_key, clause in clauses.items():
            label_id, category, _ = self.classifier.classify_clause(clause.text)
            severity = self.scorer.score_clause(label_id, clause.text)

            if label_id not in clause_scores:
                clause_scores[label_id] = []
            clause_scores[label_id].append(severity)

            score_details.append(
                {
                    "clause_id": clause_key,
                    "category": category,
                    "severity": severity,
                    "text_preview": clause.text[:80],
                }
            )

        # Flag problematic covenants
        covenant_clauses = [
            (label_id, clause.text)
            for label_id, clause in zip(
                [self.classifier.classify_clause(c.text)[0] for c in clauses.values()],
                clauses.values(),
            )
            if label_id == 5
        ]

        covenants = self.scorer.flag_covenants(covenant_clauses)
        bottlenecks = self.scorer.identify_bottleneck_terms(
            [
                (self.classifier.classify_clause(c.text)[0], c.text)
                for c in clauses.values()
            ]
        )

        # Generate comprehensive risk report
        risk_report = self.scorer.generate_risk_report(clause_scores)

        print_section("Overall Risk Assessment")
        print(f"  Project Risk Score: {risk_report['project_risk_score']:.2f}/5.0")
        print(f"  Risk Level: {risk_report['risk_level']}")

        print_section("Risk by Category")
        for category, details in risk_report["category_breakdown"].items():
            severity_bar = "█" * int(details["average_severity"] * 2)
            print(
                f"  • {category:30s} {severity_bar:10s} {details['average_severity']:.2f}/5.0"
            )

        if risk_report["key_risks"]:
            print_section("Key Risks Requiring Attention")
            for risk in risk_report["key_risks"]:
                print(f"  ⚠ {risk['category']}")
                print(f"    Action: {risk['action']}")

        if covenants:
            print_section(f"Restricted Covenants ({len(covenants)})")
            for covenant in covenants[:5]:
                print(
                    f"  • Severity {covenant['severity']}/5: {covenant['text_preview']}"
                )

        if bottlenecks:
            print_section(f"Financing Bottlenecks ({len(bottlenecks)})")
            for bottleneck in bottlenecks[:5]:
                print(f"  • {bottleneck['category']}: {bottleneck['description']}")

        # Save risk scoring results
        risk_report_complete = {
            "risk_report": risk_report,
            "clause_scores_detail": score_details,
            "covenants": covenants,
            "bottlenecks": bottlenecks,
        }
        with open("phase4_risk_scoring.json", "w") as f:
            json.dump(risk_report_complete, f, indent=2)
        print(f"\n✓ Risk scoring results saved to phase4_risk_scoring.json")

        print_header("PHASE 5: BENCHMARK COMPARISON")
        logger.info("Loading benchmark database...")

        self.benchmark_db = BenchmarkDatabase("phase5_benchmarks.db")
        count = self.benchmark_db.load_transaction_benchmarks(sample_size=100)
        print(f"✓ Loaded {count} benchmark transactions")

        # Extract project details for comparison
        project_sector = (
            "Solar"
            if any("solar" in clause.text.lower() for clause in clauses.values())
            else "Power"
        )
        current_contract = {
            "project_sector": project_sector,
            "debt_tenor": 20,
            "debt_amount": 200,
        }

        # Compare against benchmarks
        comparison = self.benchmark_db.compare_against_benchmark(current_contract)
        statistics = self.benchmark_db.compute_term_statistics()

        print_section("Benchmark Statistics")
        print(
            f"  Total Benchmarks: {statistics.get('by_country', {}) and len(statistics['by_country'])}"
        )

        if "debt_amount" in statistics:
            stats = statistics["debt_amount"]
            print(f"\n  Debt Amount ($ Millions):")
            print(f"    Average: ${stats['average']:.1f}M")
            print(f"    Range: ${stats['min']:.1f}M - ${stats['max']:.1f}M")

        if "debt_tenor" in statistics:
            stats = statistics["debt_tenor"]
            print(f"\n  Debt Tenor (Years):")
            print(f"    Average: {stats['average']:.1f} years")
            print(f"    Range: {stats['min']} - {stats['max']} years")

        if "spread_bps" in statistics:
            stats = statistics["spread_bps"]
            print(f"\n  Spread (basis points):")
            print(f"    Average: {stats['average']:.0f} bps")
            print(f"    Range: {stats['min']:.0f} - {stats['max']:.0f} bps")

        print_section("Current Contract vs Benchmark")
        if "deviations" in comparison:
            for deviation in comparison["deviations"]:
                status_icon = "✓" if deviation["status"] == "NORMAL" else "⚠"
                print(
                    f"  {status_icon} {deviation['metric']:20s} "
                    f"Current: {deviation['current']}, "
                    f"Benchmark: {deviation['benchmark_avg']:.1f}, "
                    f"Deviation: {deviation['deviation_percent']:+.1f}%"
                )

        # Save benchmark results
        benchmark_results = {
            "statistics": statistics,
            "comparison": comparison,
        }
        with open("phase5_benchmarks.json", "w") as f:
            json.dump(benchmark_results, f, indent=2, default=str)
        print(f"\n✓ Benchmark results saved to phase5_benchmarks.json")

        # Generate final summary
        print_header("FINAL ASSESSMENT SUMMARY")

        summary = {
            "contract_analysis": {
                "sections": len(sections),
                "clauses": len(clauses),
                "entities": len(entities),
            },
            "entity_extraction": {
                "sponsors": len(extraction.sponsors),
                "lenders": len(extraction.lenders),
                "amounts": len(extraction.amounts),
                "dates": len(extraction.dates),
            },
            "classification": {
                "total_clauses": len(clause_classifications),
                "categories_found": len(clause_classifications),
            },
            "risk_assessment": {
                "project_risk_score": risk_report["project_risk_score"],
                "risk_level": risk_report["risk_level"],
                "key_risks_count": len(risk_report["key_risks"]),
            },
            "benchmark_comparison": {
                "benchmarks_loaded": count,
                "deviations_found": len(comparison.get("deviations", [])),
            },
        }

        print("\n PROCESSING SUMMARY")
        print("─" * 70)
        for phase, metrics in summary.items():
            print(f"\n  {phase}:")
            for metric, value in metrics.items():
                print(f"    • {metric}: {value}")

        # Save summary
        with open("ANALYSIS_SUMMARY.json", "w") as f:
            json.dump(summary, f, indent=2)
        print("\n✓ Summary saved to ANALYSIS_SUMMARY.json")

        # Cleanup
        self.benchmark_db.close()

        print_header("COMPLETE ✓")
        print("\nAll analysis files generated:")
        print("  • phase1_parsing.json")
        print("  • phase2_extraction.json")
        print("  • phase3_classification.json")
        print("  • phase4_risk_scoring.json")
        print("  • phase5_benchmarks.json")
        print("  • ANALYSIS_SUMMARY.json")

        return summary


def main():
    """Main entry point"""
    print_header("INFRARISKAI - NLP PIPELINE")
    print("End-to-End Contract Intelligence Processing\n")

    # Use sample contract
    contract_text = create_sample_contract()

    # Initialize pipeline
    pipeline = NLPPipeline()

    try:
        # Process contract
        summary = pipeline.process_contract(contract_text)

        print("\n✓ Pipeline execution completed successfully!")
        print(
            f"\nProject Risk Score: {summary['risk_assessment']['project_risk_score']:.2f}/5.0"
        )
        print(f"Risk Level: {summary['risk_assessment']['risk_level']}")

        return 0

    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        print(f"\n✗ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
