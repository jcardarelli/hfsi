import argparse
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import pdfplumber

OUTPUT_FILE = "dataset.csv"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up argument parser
argparser = argparse.ArgumentParser(description="Building Code Additions")
argparser.add_argument(
    "-b",
    "--base-document",
    required=True,
    type=str,
    help="Base building code document, e.g. 2022 CA Plumbing Code",
)
argparser.add_argument(
    "-c1",
    "--code1",
    required=True,
    type=str,
    help="Supplemental building code documents 1, e.g. 2022 SF Plumbing",
)
argparser.add_argument(
    "-c2",
    "--code2",
    required=True,
    type=str,
    help="Supplemental building code documents 2, e.g. 2022 Oakland Plumbing",
)
args = argparser.parse_args()


@dataclass
class CodeSection:
    number: str
    title: str
    content: str
    subsections: List["CodeSection"]
    page_number: int


@dataclass
class ParsedCode:
    jurisdiction: str
    sections: List[CodeSection]
    source_file: str
    parse_date: datetime


class BuildingCodeParser:
    def __init__(self):
        self.output_dir = Path("parsed_codes")
        self.output_dir.mkdir(exist_ok=True)

    def clean_text(self, text: str) -> str:
        """Clean extracted PDF text"""
        # Remove multiple spaces
        text = re.sub(r"\s+", " ", text)
        # Remove page numbers
        text = re.sub(r"\b\d+\b\s*$", "", text)
        # Remove footer/header artifacts
        text = re.sub(r"(?i)(chapter|section).*?\n", "", text)
        return text.strip()

    def extract_section_number(self, text: str) -> Optional[str]:
        """Extract section number from text"""
        pattern = r"(?:Section\s+)?(\d+(?:\.\d+)*)"
        match = re.search(pattern, text)

        if match:
            return match.group(1)
        else:
            return None

    def is_section_header(self, text: str) -> bool:
        """Determine if text is a section header"""
        patterns = [
            r"^\d+(?:\.\d+)*\s+[A-Z]",  # Starts with number followed by capital letter
            r"^Section\s+\d+(?:\.\d+)*",  # Starts with "Section" followed by number
            r"^\d+(?:\.\d+)*\s*—\s*[A-Z]",  # Number followed by em dash and capital letter
            r"^\d{4}[A-Za-z]\.\d+\.\d+$",
        ]
        return any(re.match(pattern, text.strip()) for pattern in patterns)

    def parse_pdf(self, pdf_path: str, jurisdiction: str) -> ParsedCode:
        """Parse building code PDF and extract structured content"""
        logger.info(f"Parsing {jurisdiction} building code from {pdf_path}")
        sections = []
        current_section = None
        current_text = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()

                    # Split text into lines
                    lines = text.split("\n")

                    for line in lines:
                        line = self.clean_text(line)

                        if self.is_section_header(line):
                            # Save previous section if exists
                            if current_section:
                                current_section.content = "\n".join(current_text)
                                sections.append(current_section)

                            # Start new section
                            section_number = self.extract_section_number(line)
                            if section_number:  # Only create section if number is found
                                current_section = CodeSection(
                                    number=section_number,
                                    title=line,
                                    content="",
                                    subsections=[],
                                    page_number=page.page_number,
                                )
                                current_text = []
                        elif (
                            current_section
                        ):  # Only append text if we have a current section
                            current_text.append(line)

                # Add final section
                if current_section:
                    current_section.content = "\n".join(current_text)
                    sections.append(current_section)

        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {e}")
            raise

        return ParsedCode(
            jurisdiction=jurisdiction,
            sections=sections,
            source_file=pdf_path,
            parse_date=datetime.now(),
        )


class CodeComparator:
    def __init__(self):
        self.parser = BuildingCodeParser()

    def compare_sections(self, section1: CodeSection, section2: CodeSection) -> Dict:
        """Compare two code sections and identify differences"""
        # Calculate similarity ratio
        similarity = SequenceMatcher(None, section1.content, section2.content).ratio()

        comparison = {
            "section_number": section1.number,
            "similarity": similarity,
            "sf_title": section1.title,
            "oakland_title": section2.title,
            "differences": [],
        }

        # Compare content using difflib
        s = SequenceMatcher(None, section1.content, section2.content)
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag != "equal":
                difference = {
                    "type": tag,
                    "sf_text": section1.content[i1:i2],
                    "oakland_text": section2.content[j1:j2],
                    "location": {
                        "sf_page": section1.page_number,
                        "oakland_page": section2.page_number,
                    },
                }
                comparison["differences"].append(difference)

        return comparison

    def compare_codes(self, sf_code: ParsedCode, oakland_code: ParsedCode) -> Dict:
        """Compare building codes between SF and Oakland"""
        comparisons = []

        # Match sections by number and compare
        for sf_section in sf_code.sections:
            matching_section = next(
                (s for s in oakland_code.sections if s.number == sf_section.number),
                None,
            )

            if matching_section:
                comparison = self.compare_sections(sf_section, matching_section)
                comparisons.append(comparison)
            else:
                comparisons.append(
                    {
                        "section_number": sf_section.number,
                        "similarity": 0.0,
                        "sf_title": sf_section.title,
                        "oakland_title": "N/A",
                        "differences": [
                            {
                                "type": "sf_only",
                                "sf_text": sf_section.content,
                                "oakland_text": "",
                                "location": {
                                    "sf_page": sf_section.page_number,
                                    "oakland_page": None,
                                },
                            }
                        ],
                    }
                )

        # Find sections unique to Oakland
        for oakland_section in oakland_code.sections:
            if not any(s.number == oakland_section.number for s in sf_code.sections):
                comparisons.append(
                    {
                        "section_number": oakland_section.number,
                        "similarity": 0.0,
                        "sf_title": "N/A",
                        "oakland_title": oakland_section.title,
                        "differences": [
                            {
                                "type": "oakland_only",
                                "sf_text": "",
                                "oakland_text": oakland_section.content,
                                "location": {
                                    "sf_page": None,
                                    "oakland_page": oakland_section.page_number,
                                },
                            }
                        ],
                    }
                )

        return {"timestamp": datetime.now().isoformat(), "comparisons": comparisons}


def generate_report(comparison_results: Dict) -> tuple[str, pd.DataFrame]:
    """Generate human-readable report and summary DataFrame from comparison results"""
    report = "Building Code Comparison: San Francisco vs Oakland\n"
    report += f"Generated on: {comparison_results['timestamp']}\n\n"

    # Prepare data for DataFrame
    summary_data = []

    for comparison in comparison_results["comparisons"]:
        report += f"\nSection {comparison['section_number']}:\n"
        report += "=" * 40 + "\n"
        report += f"Similarity: {comparison['similarity']:.1%}\n"
        report += f"SF Title: {comparison['sf_title']}\n"
        report += f"Oakland Title: {comparison['oakland_title']}\n\n"

        # Add to summary data
        summary_data.append(
            {
                "Section": comparison["section_number"],
                "Similarity": f"{comparison['similarity']:.1%}",
                "Differences": len(comparison["differences"]),
                "SF_Title": comparison["sf_title"],
                "Oakland_Title": comparison["oakland_title"],
            }
        )

        for diff in comparison["differences"]:
            if diff["type"] == "sf_only":
                report += "Unique to San Francisco:\n"
                report += f"Page {diff['location']['sf_page']}:\n"
                report += diff["sf_text"] + "\n\n"
            elif diff["type"] == "oakland_only":
                report += "Unique to Oakland:\n"
                report += f"Page {diff['location']['oakland_page']}:\n"
                report += diff["oakland_text"] + "\n\n"
            else:
                report += f"Difference Type: {diff['type']}\n"
                report += f"SF Text (Page {diff['location']['sf_page']}):\n{diff['sf_text']}\n"
                report += f"Oakland Text (Page {diff['location']['oakland_page']}):\n{diff['oakland_text']}\n\n"

    return report, pd.DataFrame(summary_data)


def main():
    # Initialize parser and comparator
    parser = BuildingCodeParser()
    comparator = CodeComparator()

    try:
        # Parse PDFs
        state_building_code = parser.parse_pdf(args.base_document, "State")
        city1_building_code = parser.parse_pdf(args.code1, "City 1")
        city2_building_code = parser.parse_pdf(args.code2, "City 2")

        with open(OUTPUT_FILE, "w") as f:
            f.write("location, section\n")
            for section in state_building_code.sections:
                f.write("state, {}\n".format(section.number))
            for section in city1_building_code.sections:
                f.write("city 1, {}\n".format(section.number))
            for section in city2_building_code.sections:
                f.write("city 2, {}\n".format(section.number))

        print(f"finished writing CSV to {OUTPUT_FILE}")

    except Exception as e:
        logger.error(f"Error during comparison: {e}")
        raise


if __name__ == "__main__":
    main()
