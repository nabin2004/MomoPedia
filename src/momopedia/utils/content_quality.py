"""
Content Quality and Validation Utilities
Advanced algorithms for scoring content quality, cultural authenticity, and accuracy
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import nltk
from collections import Counter
import requests
from urllib.parse import urlparse


@dataclass
class QualityScore:
    """Comprehensive quality score for content"""
    overall: float
    cultural_authenticity: float
    factual_accuracy: float
    writing_quality: float
    citation_quality: float
    completeness: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'overall': self.overall,
            'cultural_authenticity': self.cultural_authenticity,
            'factual_accuracy': self.factual_accuracy,
            'writing_quality': self.writing_quality,
            'citation_quality': self.citation_quality,
            'completeness': self.completeness
        }

class ContentValidator:
    """Validate and score content quality"""
    
    def __init__(self):
        # Load word lists and patterns
        self.cultural_keywords = self._load_cultural_keywords()
        self.quality_indicators = self._load_quality_indicators()
        self.citation_patterns = self._compile_citation_patterns()
        
    def _load_cultural_keywords(self) -> Dict[str, List[str]]:
        """Load cultural keywords for different regions"""
        return {
            'nepal': ['kathmandu', 'sherpa', 'himalaya', 'nepal', 'nepali', 'tibetan', 'yak'],
            'tibet': ['lhasa', 'tibet', 'tibetan', 'monastery', 'buddhist', 'yak', 'barley'],
            'india': ['darjeeling', 'sikkim', 'indian', 'hindi', 'spices', 'curry'],
            'china': ['chinese', 'dim sum', 'dumpling', 'soy sauce', 'ginger'],
            'general': ['traditional', 'authentic', 'cultural', 'heritage', 'recipe', 'family']
        }
    
    def _load_quality_indicators(self) -> Dict[str, List[str]]:
        """Load indicators for writing quality"""
        return {
            'positive': [
                'traditional', 'authentic', 'cultural', 'heritage', 'centuries',
                'originated', 'techniques', 'methods', 'preparation', 'ingredients'
            ],
            'academic': [
                'according to', 'research shows', 'studies indicate', 'evidence suggests',
                'documented', 'recorded', 'historical', 'archaeological'
            ],
            'descriptive': [
                'delicate', 'savory', 'aromatic', 'tender', 'flavorful', 'texture',
                'appearance', 'golden', 'steamed', 'crispy'
            ]
        }
    
    def _compile_citation_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for detecting citations"""
        patterns = [
            r'\[[0-9]+\]',  # [1], [2], etc.
            r'\([^)]*[0-9]{4}[^)]*\)',  # (Author, 2023)
            r'https?://[^\s<>"{}|\\^`\[\]]+',  # URLs
            r'doi:[0-9a-zA-Z\./\-_]+',  # DOI
            r'ISBN[:\s]*[0-9\-X]+',  # ISBN
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def validate_content(self, content: str, metadata: Dict[str, Any] = None) -> QualityScore:
        """Comprehensive content validation and scoring"""
        if not content or len(content.strip()) < 100:
            return QualityScore(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        # Individual score components
        cultural_score = self._score_cultural_authenticity(content, metadata)
        writing_score = self._score_writing_quality(content)
        citation_score = self._score_citation_quality(content)
        completeness_score = self._score_completeness(content, metadata)
        
        # Factual accuracy requires external validation (placeholder for now)
        factual_score = self._score_factual_accuracy(content)
        
        # Calculate weighted overall score
        weights = {
            'cultural': 0.25,
            'writing': 0.25,
            'citation': 0.20,
            'completeness': 0.20,
            'factual': 0.10
        }
        
        overall = (
            cultural_score * weights['cultural'] +
            writing_score * weights['writing'] +
            citation_score * weights['citation'] +
            completeness_score * weights['completeness'] +
            factual_score * weights['factual']
        )
        
        return QualityScore(
            overall=overall,
            cultural_authenticity=cultural_score,
            factual_accuracy=factual_score,
            writing_quality=writing_score,
            citation_quality=citation_score,
            completeness=completeness_score
        )
    
    def _score_cultural_authenticity(self, content: str, metadata: Dict[str, Any] = None) -> float:
        """Score cultural authenticity based on appropriate terminology and context"""
        content_lower = content.lower()
        total_score = 0.0
        checks = 0
        
        # Check for cultural keywords
        region = metadata.get('region', 'general') if metadata else 'general'
        if region in self.cultural_keywords:
            cultural_words = self.cultural_keywords[region]
            found_words = sum(1 for word in cultural_words if word in content_lower)
            total_score += min(found_words / len(cultural_words), 1.0)
            checks += 1
        
        # Check for general cultural indicators
        general_words = self.cultural_keywords['general']
        found_general = sum(1 for word in general_words if word in content_lower)
        total_score += min(found_general / len(general_words), 1.0)
        checks += 1
        
        # Check for cultural sensitivity indicators
        sensitivity_indicators = ['traditional', 'heritage', 'cultural significance', 'authentic']
        found_sensitivity = sum(1 for indicator in sensitivity_indicators if indicator in content_lower)
        total_score += min(found_sensitivity / len(sensitivity_indicators), 1.0)
        checks += 1
        
        # Penalize for potentially inappropriate terms
        inappropriate_terms = ['exotic', 'strange', 'weird', 'primitive']
        penalty = sum(0.1 for term in inappropriate_terms if term in content_lower)
        total_score = max(0, total_score - penalty)
        
        return total_score / checks if checks > 0 else 0.0
    
    def _score_writing_quality(self, content: str) -> float:
        """Score writing quality based on various linguistic factors"""
        # Basic metrics
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        
        if not words or not sentences:
            return 0.0
        
        total_score = 0.0
        checks = 0
        
        # 1. Word count appropriateness (500-2000 words ideal)
        word_count = len(words)
        if 500 <= word_count <= 2000:
            word_score = 1.0
        elif 300 <= word_count < 500 or 2000 < word_count <= 3000:
            word_score = 0.8
        elif 100 <= word_count < 300 or 3000 < word_count <= 5000:
            word_score = 0.6
        else:
            word_score = 0.3
        
        total_score += word_score
        checks += 1
        
        # 2. Sentence length variety
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            length_variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            
            # Good variety in sentence lengths
            if 10 <= avg_length <= 25 and 20 <= length_variance <= 100:
                sentence_score = 1.0
            elif 8 <= avg_length <= 30 and 10 <= length_variance <= 150:
                sentence_score = 0.8
            else:
                sentence_score = 0.6
        else:
            sentence_score = 0.0
        
        total_score += sentence_score
        checks += 1
        
        # 3. Vocabulary richness (unique words / total words)
        unique_words = len(set(word.lower() for word in words))
        vocabulary_richness = unique_words / len(words) if words else 0
        
        if vocabulary_richness >= 0.6:
            vocab_score = 1.0
        elif vocabulary_richness >= 0.5:
            vocab_score = 0.8
        elif vocabulary_richness >= 0.4:
            vocab_score = 0.6
        else:
            vocab_score = 0.4
        
        total_score += vocab_score
        checks += 1
        
        # 4. Quality indicators presence
        positive_indicators = self.quality_indicators['positive']
        academic_indicators = self.quality_indicators['academic']
        descriptive_indicators = self.quality_indicators['descriptive']
        
        content_lower = content.lower()
        positive_count = sum(1 for indicator in positive_indicators if indicator in content_lower)
        academic_count = sum(1 for indicator in academic_indicators if indicator in content_lower)
        descriptive_count = sum(1 for indicator in descriptive_indicators if indicator in content_lower)
        
        indicator_score = min((positive_count + academic_count + descriptive_count) / 10, 1.0)
        total_score += indicator_score
        checks += 1
        
        return total_score / checks if checks > 0 else 0.0
    
    def _score_citation_quality(self, content: str) -> float:
        """Score the quality and presence of citations"""
        total_citations = 0
        quality_score = 0.0
        
        for pattern in self.citation_patterns:
            matches = pattern.findall(content)
            citation_count = len(matches)
            total_citations += citation_count
            
            # Different citation types have different quality scores
            if pattern.pattern.startswith('https?://'):  # URLs
                # Check URL quality
                for url in matches:
                    domain = urlparse(url).netloc.lower()
                    if any(trusted in domain for trusted in ['wikipedia', 'britannica', '.edu', '.gov']):
                        quality_score += 1.0
                    elif any(excluded in domain for excluded in ['pinterest', 'facebook', 'instagram']):
                        quality_score += 0.2
                    else:
                        quality_score += 0.6
            
            elif 'doi:' in pattern.pattern.lower():  # DOI
                quality_score += citation_count * 1.0
            
            elif '[0-9]+' in pattern.pattern:  # Numbered citations
                quality_score += citation_count * 0.8
            
            else:  # Other citation formats
                quality_score += citation_count * 0.6
        
        # Normalize score
        if total_citations == 0:
            return 0.0
        
        # Expected citation density: 1-3 citations per 100 words
        words = len(content.split())
        expected_citations = max(1, words // 100)
        
        citation_density_score = min(total_citations / expected_citations, 1.0)
        citation_quality_score = quality_score / total_citations
        
        return (citation_density_score + citation_quality_score) / 2
    
    def _score_completeness(self, content: str, metadata: Dict[str, Any] = None) -> float:
        """Score content completeness based on expected sections"""
        content_lower = content.lower()
        
        # Expected sections for a momo article
        expected_sections = [
            'origin', 'history', 'preparation', 'ingredients', 'recipe', 'method',
            'cultural', 'significance', 'regional', 'variations', 'serving'
        ]
        
        # Check for section presence
        found_sections = sum(1 for section in expected_sections if section in content_lower)
        section_score = found_sections / len(expected_sections)
        
        # Check for comprehensive coverage
        comprehensive_indicators = [
            'ingredients', 'preparation', 'history', 'cultural', 'traditional',
            'methods', 'techniques', 'variations', 'regions'
        ]
        
        found_indicators = sum(1 for indicator in comprehensive_indicators if indicator in content_lower)
        comprehensiveness_score = min(found_indicators / len(comprehensive_indicators), 1.0)
        
        # Check minimum content requirements
        word_count = len(content.split())
        length_score = 1.0 if word_count >= 500 else word_count / 500
        
        return (section_score + comprehensiveness_score + length_score) / 3
    
    def _score_factual_accuracy(self, content: str) -> float:
        """Placeholder for factual accuracy scoring (would need external fact-checking)"""
        # This would integrate with fact-checking APIs or databases
        # For now, return a basic score based on presence of factual indicators
        
        factual_indicators = [
            'according to', 'research', 'study', 'evidence', 'documented',
            'century', 'year', 'originated', 'developed', 'traditional method'
        ]
        
        content_lower = content.lower()
        found_indicators = sum(1 for indicator in factual_indicators if indicator in content_lower)
        
        return min(found_indicators / len(factual_indicators), 1.0)

class ContentEnhancer:
    """Enhance content quality through automated improvements"""
    
    def __init__(self):
        self.validator = ContentValidator()
    
    def suggest_improvements(self, content: str, metadata: Dict[str, Any] = None) -> List[str]:
        """Generate suggestions for improving content quality"""
        suggestions = []
        quality_score = self.validator.validate_content(content, metadata)
        
        # Cultural authenticity suggestions
        if quality_score.cultural_authenticity < 0.7:
            region = metadata.get('region', 'general') if metadata else 'general'
            suggestions.append(
                f"Consider adding more culturally specific terms and context for {region}. "
                f"Include traditional preparation methods and cultural significance."
            )
        
        # Writing quality suggestions
        if quality_score.writing_quality < 0.7:
            word_count = len(content.split())
            if word_count < 500:
                suggestions.append("Content is too short. Add more detailed information about preparation methods, history, and cultural context.")
            elif word_count > 2000:
                suggestions.append("Content is quite lengthy. Consider condensing or breaking into sections for better readability.")
            
            suggestions.append("Improve sentence variety and use more descriptive language about taste, texture, and appearance.")
        
        # Citation suggestions
        if quality_score.citation_quality < 0.6:
            suggestions.append("Add more reliable sources and citations. Include academic sources, cultural institutions, or reputable culinary websites.")
        
        # Completeness suggestions
        if quality_score.completeness < 0.7:
            suggestions.append("Include more comprehensive coverage of ingredients, preparation methods, cultural significance, and regional variations.")
        
        return suggestions
    
    def auto_enhance_content(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Automatically enhance content with basic improvements"""
        enhanced_content = content
        
        # Add section headers if missing
        if 'ingredients' in content.lower() and '## Ingredients' not in enhanced_content:
            enhanced_content = re.sub(
                r'(ingredients?)', 
                r'## Ingredients', 
                enhanced_content, 
                count=1, 
                flags=re.IGNORECASE
            )
        
        # Improve formatting for lists
        enhanced_content = re.sub(
            r'^(\d+\.\s*)', 
            r'\n\1', 
            enhanced_content, 
            flags=re.MULTILINE
        )
        
        # Add emphasis to important terms
        important_terms = ['traditional', 'authentic', 'cultural heritage', 'originated']
        for term in important_terms:
            if term in enhanced_content.lower():
                enhanced_content = re.sub(
                    f'\\b{term}\\b', 
                    f'**{term}**', 
                    enhanced_content, 
                    count=1, 
                    flags=re.IGNORECASE
                )
        
        return enhanced_content

# Global instances
content_validator = ContentValidator()
content_enhancer = ContentEnhancer()

def validate_content(content: str, metadata: Dict[str, Any] = None) -> QualityScore:
    """Global function to validate content quality"""
    return content_validator.validate_content(content, metadata)

def enhance_content(content: str, metadata: Dict[str, Any] = None) -> Tuple[str, List[str]]:
    """Global function to enhance content and get suggestions"""
    enhanced = content_enhancer.auto_enhance_content(content, metadata)
    suggestions = content_enhancer.suggest_improvements(enhanced, metadata)
    return enhanced, suggestions