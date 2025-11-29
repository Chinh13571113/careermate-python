"""
Natural Language Processing module for extracting skills from free-form text

This module handles:
1. Skill extraction from resumes, job descriptions, or free-form text
2. Experience detection (years mentioned in text)
3. Text cleaning and preprocessing
"""

import re
from typing import List, Dict, Tuple, Optional


class SkillExtractor:
    """Extract skills and experience from free-form text"""
    
    def __init__(self, recommender=None):
        """
        Initialize skill extractor
        
        Args:
            recommender: CareerRecommender instance (to access skill patterns)
        """
        self.recommender = recommender
        
        # Known skills to search for in text
        self.known_skills = self._build_skill_database()
        
        # Experience patterns
        self.experience_patterns = [
            # Standard patterns with "experience" keyword
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            
            # Patterns with prepositions (in/with/of)
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:in|with|of)\s+',
            
            # Work-related patterns
            r'worked\s+(?:for\s+)?(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:professional|work)',
            
            # Short format patterns (e.g., "Python developer, 3 years" or "JavaScript, 4 yrs")
            r'(\d+)\+?\s*(?:years?|yrs?)[\s,\.;]+',  # Matches "3 years." or "4 yrs," etc.
            r',\s*(\d+)\+?\s*(?:years?|yrs?)',  # Matches ", 3 years" or ", 4 yrs"
            
            # Role + years patterns
            r'(?:developer|engineer|analyst|designer|manager|architect|lead|senior|junior)\s*,?\s*(\d+)\+?\s*(?:years?|yrs?)',
        ]
    
    def _build_skill_database(self) -> Dict[str, List[str]]:
        """
        Build comprehensive skill database from role patterns
        
        Returns:
            Dictionary mapping normalized skills to their variants
        """
        skills_db = {}
        
        # Programming Languages
        skills_db['python'] = ['python', 'python3', 'py', 'python programming']
        skills_db['javascript'] = ['javascript', 'js', 'ecmascript', 'es6', 'es2015']
        skills_db['typescript'] = ['typescript', 'ts']
        skills_db['java'] = ['java', 'java programming', 'core java', 'java se', 'java ee']
        skills_db['c#'] = ['c#', 'csharp', 'c sharp', 'c-sharp', 'dotnet']
        skills_db['go'] = ['go', 'golang', 'go programming']
        skills_db['rust'] = ['rust', 'rust programming']
        skills_db['ruby'] = ['ruby', 'rb', 'ruby programming']
        skills_db['php'] = ['php', 'php programming']
        skills_db['swift'] = ['swift', 'swift programming', 'swiftui']
        skills_db['kotlin'] = ['kotlin', 'kotlin programming']
        skills_db['c++'] = ['c++', 'cpp', 'c plus plus', 'cplusplus']
        skills_db['c'] = [' c ', 'c programming', 'ansi c']
        skills_db['scala'] = ['scala', 'scala programming']
        skills_db['r'] = [' r ', 'r programming', 'r language']
        skills_db['matlab'] = ['matlab']
        
        # Web Frameworks
        skills_db['django'] = ['django', 'django rest', 'drf', 'django framework']
        skills_db['flask'] = ['flask', 'flask framework']
        skills_db['fastapi'] = ['fastapi', 'fast api']
        skills_db['react'] = ['react', 'reactjs', 'react.js', 'react js']
        skills_db['angular'] = ['angular', 'angularjs', 'angular.js']
        skills_db['vue'] = ['vue', 'vuejs', 'vue.js', 'vue js']
        skills_db['next.js'] = ['nextjs', 'next.js', 'next js']
        skills_db['node.js'] = ['nodejs', 'node.js', 'node js', 'node']
        skills_db['express'] = ['express', 'expressjs', 'express.js']
        skills_db['spring'] = ['spring', 'spring boot', 'spring framework']
        skills_db['asp.net'] = ['asp.net', 'aspnet', 'asp net']
        
        # Databases
        skills_db['postgresql'] = ['postgresql', 'postgres', 'pg', 'psql', 'postgre sql']
        skills_db['mysql'] = ['mysql', 'my sql']
        skills_db['mongodb'] = ['mongodb', 'mongo', 'mongo db']
        skills_db['redis'] = ['redis', 'redis cache']
        skills_db['elasticsearch'] = ['elasticsearch', 'elastic search', 'es']
        skills_db['cassandra'] = ['cassandra', 'apache cassandra']
        skills_db['oracle'] = ['oracle', 'oracle db', 'oracle database']
        skills_db['sql server'] = ['sql server', 'mssql', 'ms sql']
        skills_db['dynamodb'] = ['dynamodb', 'dynamo db', 'dynamo']
        
        # DevOps & Cloud
        skills_db['docker'] = ['docker', 'docker container', 'containerization']
        skills_db['kubernetes'] = ['kubernetes', 'k8s', 'kube']
        skills_db['aws'] = ['aws', 'amazon web services', 'amazon aws']
        skills_db['azure'] = ['azure', 'microsoft azure', 'ms azure']
        skills_db['gcp'] = ['gcp', 'google cloud', 'google cloud platform']
        skills_db['terraform'] = ['terraform', 'tf']
        skills_db['ansible'] = ['ansible']
        skills_db['jenkins'] = ['jenkins', 'jenkins ci']
        skills_db['github actions'] = ['github actions', 'gh actions']
        skills_db['gitlab ci'] = ['gitlab ci', 'gitlab']
        skills_db['circleci'] = ['circleci', 'circle ci']
        
        # Data Science & ML
        skills_db['tensorflow'] = ['tensorflow', 'tensor flow', 'tf']
        skills_db['pytorch'] = ['pytorch', 'torch', 'py torch']
        skills_db['scikit-learn'] = ['scikit-learn', 'sklearn', 'scikit learn']
        skills_db['pandas'] = ['pandas', 'pandas library']
        skills_db['numpy'] = ['numpy', 'numpy library']
        skills_db['keras'] = ['keras']
        skills_db['spark'] = ['spark', 'apache spark', 'pyspark']
        skills_db['hadoop'] = ['hadoop', 'apache hadoop']
        skills_db['kafka'] = ['kafka', 'apache kafka']
        skills_db['airflow'] = ['airflow', 'apache airflow']
        skills_db['sql'] = ['sql', 'structured query language', 't-sql', 'pl/sql', 'pl sql']
        skills_db['tableau'] = ['tableau', 'tableau desktop', 'tableau server']
        skills_db['power bi'] = ['power bi', 'powerbi', 'power-bi']
        skills_db['excel'] = ['excel', 'microsoft excel', 'ms excel', 'advanced excel']
        skills_db['r'] = ['r programming', 'r language', 'r statistical']
        skills_db['sas'] = ['sas', 'sas programming']
        skills_db['jupyter'] = ['jupyter', 'jupyter notebook', 'jupyter lab']
        
        # Tools & Others
        skills_db['git'] = ['git', 'github', 'gitlab', 'version control']
        skills_db['linux'] = ['linux', 'unix']
        skills_db['rest api'] = ['rest api', 'restful api', 'rest', 'restful']
        skills_db['graphql'] = ['graphql', 'graph ql']
        skills_db['microservices'] = ['microservices', 'micro services']
        
        # Testing
        skills_db['pytest'] = ['pytest', 'py test']
        skills_db['jest'] = ['jest', 'jest testing']
        skills_db['selenium'] = ['selenium', 'selenium webdriver']
        skills_db['cypress'] = ['cypress', 'cypress testing']
        skills_db['junit'] = ['junit', 'j unit']
        
        return skills_db
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from free-form text
        
        Args:
            text: Free-form text (resume, job description, etc.)
        
        Returns:
            List of normalized skill names
        
        Examples:
            >>> extractor.extract_skills("I have 5 years experience with Python and Django")
            ['Python', 'Django']
            
            >>> extractor.extract_skills("Expert in React, Node.js, and PostgreSQL")
            ['React', 'Node.js', 'PostgreSQL']
        """
        if not text:
            return []
        
        # Normalize text
        text_lower = text.lower()
        
        found_skills = set()
        
        # Search for each known skill
        for normalized_skill, variants in self.known_skills.items():
            for variant in variants:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(variant) + r'\b'
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Capitalize first letter for display
                    display_name = normalized_skill.title()
                    
                    # Special cases for display names
                    if normalized_skill == 'c#':
                        display_name = 'C#'
                    elif normalized_skill == 'c++':
                        display_name = 'C++'
                    elif normalized_skill == 'node.js':
                        display_name = 'Node.js'
                    elif normalized_skill == 'next.js':
                        display_name = 'Next.js'
                    elif normalized_skill == 'vue':
                        display_name = 'Vue'
                    elif '.' in normalized_skill:
                        display_name = normalized_skill  # Keep dots
                    
                    found_skills.add(display_name)
                    break  # Found this skill, no need to check other variants
        
        return sorted(list(found_skills))
    
    def extract_experience(self, text: str) -> float:
        """
        Extract years of experience from text with context awareness
        
        Args:
            text: Free-form text
        
        Returns:
            Years of experience (float), defaults to 0 if not found
        
        Examples:
            >>> extractor.extract_experience("I have 5 years of experience")
            5.0
            
            >>> extractor.extract_experience("10+ years working with Python")
            10.0
            
            >>> extractor.extract_experience("Teacher for 10 years. Recently completed bootcamp.")
            0.0  # Career changer - unrelated experience
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Career changer indicators - if present, look for tech-specific experience only
        career_changer_indicators = [
            'bootcamp', 'recently completed', 'recently learned', 'transitioning',
            'career change', 'switching careers', 'new to', 'currently learning',
            'just completed', 'graduated', 'certificate', 'coursework',
            'self-taught', 'self taught'
        ]
        
        is_career_changer = any(indicator in text_lower for indicator in career_changer_indicators)
        
        # If career changer, look for tech-specific experience patterns only
        if is_career_changer:
            tech_experience_patterns = [
                r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:software|programming|coding|development|tech|developer|engineer)',
                r'(\d+)\+?\s*years?\s+(?:in|with)\s+(?:python|java|javascript|react|django|spring|node)',
                r'(\d+)\+?\s*years?\s+(?:professional|commercial)\s+experience',
            ]
            
            for pattern in tech_experience_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        years = float(match.group(1))
                        return years
                    except (ValueError, IndexError):
                        continue
            
            # No tech-specific experience found for career changer
            return 0.0
        
        # For non-career changers, use standard patterns
        for pattern in self.experience_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    years = float(match.group(1))
                    return years
                except (ValueError, IndexError):
                    continue
        
        # If no explicit number found, infer from seniority level keywords
        seniority_mapping = {
            # Senior levels (6+ years)
            'senior': 7.0,
            'sr.': 7.0,
            'sr ': 7.0,
            'lead': 9.0,
            'principal': 12.0,
            'staff': 10.0,
            'architect': 10.0,
            
            # Mid levels (3-5 years)
            'mid-level': 4.0,
            'mid level': 4.0,
            'intermediate': 4.0,
            
            # Junior levels (0-2 years)
            'junior': 1.0,
            'jr.': 1.0,
            'jr ': 1.0,
            'entry-level': 0.5,
            'entry level': 0.5,
            'intern': 0.0,
            'trainee': 0.0,
        }
        
        # Check for seniority keywords (only if not a career changer)
        for keyword, years in seniority_mapping.items():
            # Use word boundaries to avoid false matches
            if keyword in ['sr.', 'jr.', 'sr ', 'jr ']:
                # For abbreviations, check directly
                if keyword in text_lower:
                    return years
            else:
                # For full words, check with word boundaries
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    return years
        
        # Default to 0 if no experience mentioned
        return 0.0
    
    def parse_free_text(self, text: str) -> Dict[str, any]:
        """
        Parse free-form text to extract both skills and experience
        
        Args:
            text: Free-form text (resume, profile, etc.)
        
        Returns:
            Dictionary with 'skills' and 'experience_years'
        
        Example:
            >>> extractor.parse_free_text('''
            ... I'm a software developer with 7 years of experience.
            ... I work with Python, Django, PostgreSQL, and React.
            ... Also experienced with Docker and Kubernetes.
            ... ''')
            {
                'skills': ['Python', 'Django', 'PostgreSQL', 'React', 'Docker', 'Kubernetes'],
                'experience_years': 7.0
            }
        """
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        
        return {
            'skills': skills,
            'experience_years': experience
        }
    
    def get_extraction_confidence(self, text: str) -> Dict[str, any]:
        """
        Get extraction results with confidence metrics
        
        Args:
            text: Free-form text
        
        Returns:
            Dictionary with parsed data and confidence metrics
        """
        parsed = self.parse_free_text(text)
        
        # Calculate confidence metrics
        word_count = len(text.split())
        skill_count = len(parsed['skills'])
        
        # Confidence heuristics
        extraction_quality = 'good'
        if skill_count == 0:
            extraction_quality = 'poor'
        elif skill_count < 3:
            extraction_quality = 'fair'
        elif skill_count >= 5:
            extraction_quality = 'excellent'
        
        has_experience = parsed['experience_years'] > 0
        
        return {
            'parsed_data': parsed,
            'confidence_metrics': {
                'skills_found': skill_count,
                'experience_detected': has_experience,
                'text_length': word_count,
                'extraction_quality': extraction_quality
            }
        }


# Convenience function
def create_skill_extractor(recommender=None):
    """Create SkillExtractor instance"""
    return SkillExtractor(recommender)
