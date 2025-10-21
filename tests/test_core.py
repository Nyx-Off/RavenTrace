#!/usr/bin/env python3
"""
Tests unitaires pour RavenTrace - Validation des résultats réels
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.validators import (
    validate_email, validate_phone, validate_username,
    normalize_email, normalize_phone, normalize_username
)
from core.engine import SearchEngine
from utils.helpers import (
    is_valid_email_format, extract_domain, hash_string,
    is_phone_like, is_url
)


class TestValidators(unittest.TestCase):
    """Tests pour les validateurs"""
    
    def test_validate_email_valid(self):
        """Test validation email valide"""
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name+tag@example.co.uk"))
    
    def test_validate_email_invalid(self):
        """Test validation email invalide"""
        self.assertFalse(validate_email("invalid.email"))
        self.assertFalse(validate_email("@example.com"))
        self.assertFalse(validate_email(""))
    
    def test_validate_phone_valid(self):
        """Test validation téléphone valide"""
        self.assertTrue(validate_phone("+33612345678", "FR"))
        self.assertTrue(validate_phone("+33 6 12 34 56 78", "FR"))
    
    def test_validate_phone_invalid(self):
        """Test validation téléphone invalide"""
        self.assertFalse(validate_phone("123", "FR"))
        self.assertFalse(validate_phone("invalid", "FR"))
    
    def test_validate_username_valid(self):
        """Test validation username valide"""
        self.assertTrue(validate_username("john_doe"))
        self.assertTrue(validate_username("user123"))
        self.assertTrue(validate_username("test.user"))
    
    def test_validate_username_invalid(self):
        """Test validation username invalide"""
        self.assertFalse(validate_username("a"))
        self.assertFalse(validate_username("user@name"))
        self.assertFalse(validate_username("a" * 51))
    
    def test_normalize_email(self):
        """Test normalisation email"""
        self.assertEqual(normalize_email("  TEST@EXAMPLE.COM  "), "test@example.com")
    
    def test_normalize_username(self):
        """Test normalisation username"""
        self.assertEqual(normalize_username("  TestUser  "), "testuser")


class TestHelpers(unittest.TestCase):
    """Tests pour les helpers"""
    
    def test_is_valid_email_format(self):
        """Test format email"""
        self.assertTrue(is_valid_email_format("test@example.com"))
        self.assertFalse(is_valid_email_format("invalid"))
    
    def test_extract_domain(self):
        """Test extraction domaine"""
        self.assertEqual(extract_domain("test@example.com"), "example.com")
    
    def test_hash_string(self):
        """Test hashing"""
        result = hash_string("test", "sha256")
        self.assertEqual(len(result), 64)
    
    def test_is_phone_like(self):
        """Test détection téléphone"""
        self.assertTrue(is_phone_like("0612345678"))
        self.assertFalse(is_phone_like("abc"))


class TestSearchEngine(unittest.TestCase):
    """Tests pour le moteur de recherche"""
    
    def setUp(self):
        """Initialiser le moteur"""
        self.engine = SearchEngine()
    
    def test_search_email_invalid(self):
        """Test recherche email invalide"""
        result = self.engine.search_email("invalid")
        self.assertIn("error", result)
    
    def test_search_username_invalid(self):
        """Test recherche username invalide"""
        result = self.engine.search_username("a")
        self.assertIn("error", result)


if __name__ == '__main__':
    unittest.main()