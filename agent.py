#!/usr/bin/env python3
"""
Landing Page Analysis Agent

Example usage:
    python agent.py https://example.com all
    python agent.py https://example.com ui
    python agent.py https://example.com ux
"""

import sys
import argparse
import logging
from typing import Optional, Literal, NoReturn

from parser import Parser
from openai_module import OpenAIModule, UI_PROMPT, UX_PROMPT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnalysisAgent:
    """Agent for analyzing landing pages using different modes."""
    
    def __init__(self) -> None:
        """Initialize parser and OpenAI module instances."""
        self.parser = Parser()
        self.openai = OpenAIModule()

    def analyze_page(self, url: str, mode: Literal["ui", "ux", "all"] = "ui") -> None:
        """
        Analyze webpage content based on specified mode.
        
        Args:
            url (str): URL of the webpage to analyze
            mode (Literal["ui", "ux", "all"]): Analysis mode to use
            
        Raises:
            Exception: If any error occurs during analysis
        """
        try:
            # Get page content
            logger.info(f"Fetching content from {url}")
            content = self.parser.parse_website(url)
            if not content:
                logger.error("Failed to fetch or parse website content")
                return

            # Perform analysis based on mode
            if mode in ["ui", "all"]:
                self._print_separator("UI Analysis")
                ui_analysis = self.openai.query_llm(UI_PROMPT, content)
                print(ui_analysis)

            if mode in ["ux", "all"]:
                self._print_separator("UX Analysis")
                ux_analysis = self.openai.query_llm(UX_PROMPT, content)
                print(ux_analysis)

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            raise

    @staticmethod
    def _print_separator(title: str) -> None:
        """Print a separator with title."""
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}\n")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Analyze landing page UI/UX based on content.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "url",
        help="URL of the landing page to analyze"
    )
    
    parser.add_argument(
        "--mode",
        choices=["ui", "ux", "all"],
        default="ui",
        help="Analysis mode (default: ui)"
    )
    
    return parser.parse_args()


def main() -> Optional[NoReturn]:
    """Main function to run the analysis."""
    try:
        args = parse_arguments()
        agent = AnalysisAgent()
        agent.analyze_page(args.url, args.mode)
        return None
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 