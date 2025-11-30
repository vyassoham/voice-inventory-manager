"""
Fuzzy Matching Module

Provides fuzzy string matching for item names and commands.

Uses Levenshtein distance for similarity scoring.
"""

from typing import List, Optional, Tuple
from fuzzywuzzy import fuzz, process


class FuzzyMatcher:
    """
    Fuzzy string matcher for flexible item name matching.
    """

    def __init__(self, threshold: int = 80):
        """
        Initialize fuzzy matcher.

        Args:
            threshold: Minimum similarity score (0-100) to consider a match
        """
        self.threshold = threshold

    def find_best_match(
        self,
        query: str,
        choices: List[str],
        threshold: Optional[int] = None
    ) -> Optional[str]:
        """
        Find the best matching string from choices.

        Args:
            query: Query string
            choices: List of strings to match against
            threshold: Override default threshold

        Returns:
            Best matching string or None if no good match
        """
        if not choices:
            return None

        threshold = threshold or self.threshold

        # Use fuzzywuzzy to find best match
        result = process.extractOne(query, choices, scorer=fuzz.ratio)

        if result and result[1] >= threshold:
            return result[0]

        return None

    def find_matches(
        self,
        query: str,
        choices: List[str],
        limit: int = 5,
        threshold: Optional[int] = None
    ) -> List[Tuple[str, int]]:
        """
        Find multiple matching strings.

        Args:
            query: Query string
            choices: List of strings to match against
            limit: Maximum number of matches to return
            threshold: Override default threshold

        Returns:
            List of (match, score) tuples
        """
        if not choices:
            return []

        threshold = threshold or self.threshold

        # Get top matches
        results = process.extract(query, choices, scorer=fuzz.ratio, limit=limit)

        # Filter by threshold
        return [(match, score) for match, score in results if score >= threshold]

    def similarity_score(self, str1: str, str2: str) -> int:
        """
        Calculate similarity score between two strings.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score (0-100)
        """
        return fuzz.ratio(str1, str2)

    def partial_similarity_score(self, str1: str, str2: str) -> int:
        """
        Calculate partial similarity score (substring matching).

        Args:
            str1: First string
            str2: Second string

        Returns:
            Partial similarity score (0-100)
        """
        return fuzz.partial_ratio(str1, str2)

    def token_sort_similarity(self, str1: str, str2: str) -> int:
        """
        Calculate similarity with token sorting (word order independent).

        Args:
            str1: First string
            str2: Second string

        Returns:
            Token sort similarity score (0-100)
        """
        return fuzz.token_sort_ratio(str1, str2)

    def is_match(self, str1: str, str2: str, threshold: Optional[int] = None) -> bool:
        """
        Check if two strings match above threshold.

        Args:
            str1: First string
            str2: Second string
            threshold: Override default threshold

        Returns:
            True if match, False otherwise
        """
        threshold = threshold or self.threshold
        return self.similarity_score(str1, str2) >= threshold
