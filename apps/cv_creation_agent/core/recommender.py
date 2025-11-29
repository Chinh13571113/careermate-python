"""
Refined Career Recommendation System

A clean, simple system that recommends roles and positions based on:
- User's skills and technologies
- Years of experience
- Programming languages they know

Data source: Stack Overflow Developer Survey
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import re


class CareerRecommender:
    """
    Simple, effective career recommendation engine based on real-world data
    """
    
    # Common role categories and their typical skill requirements
    ROLE_PATTERNS = {
        'Backend Developer': {
            'languages': ['Python', 'Java', 'C#', 'Go', 'Ruby', 'PHP', 'Rust'],
            'technologies': ['Django', 'Flask', 'FastAPI', 'Spring', 'Node.js', 'Express', '.NET', 'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Docker', 'REST API', 'GraphQL'],
            'keywords': ['backend', 'server', 'api', 'database', 'microservices']
        },
        'Frontend Developer': {
            'languages': ['JavaScript', 'TypeScript', 'HTML', 'CSS'],
            'technologies': ['React', 'Vue', 'Angular', 'Next.js', 'Svelte', 'Tailwind', 'Bootstrap', 'Webpack', 'Vite', 'SCSS', 'jQuery'],
            'keywords': ['frontend', 'ui', 'ux', 'web', 'responsive', 'component']
        },
        'Full Stack Developer': {
            'languages': ['JavaScript', 'TypeScript', 'Python', 'Java'],
            'technologies': ['React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring', 'PostgreSQL', 'MongoDB', 'Docker', 'AWS', 'REST API'],
            'keywords': ['fullstack', 'full-stack', 'frontend', 'backend', 'end-to-end']
        },
        'Data Scientist': {
            'languages': ['Python', 'R', 'SQL', 'Julia'],
            'technologies': ['pandas', 'numpy', 'scikit-learn', 'TensorFlow', 'PyTorch', 'Jupyter', 'Matplotlib', 'seaborn', 'Keras', 'XGBoost', 'SciPy'],
            'keywords': ['data', 'analytics', 'machine learning', 'statistics', 'visualization', 'model']
        },
        'Data Engineer': {
            'languages': ['Python', 'SQL', 'Java', 'Scala'],
            'technologies': ['Apache Spark', 'Airflow', 'Kafka', 'Hadoop', 'ETL', 'PostgreSQL', 'BigQuery', 'Snowflake', 'Redshift', 'dbt', 'Docker', 'Kubernetes'],
            'keywords': ['data pipeline', 'etl', 'data warehouse', 'big data', 'streaming']
        },
        'DevOps Engineer': {
            'languages': ['Python', 'Bash', 'Go', 'PowerShell'],
            'technologies': ['Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions', 'Terraform', 'Ansible', 'AWS', 'Azure', 'GCP', 'Linux', 'Nginx', 'Prometheus', 'Grafana'],
            'keywords': ['devops', 'ci/cd', 'infrastructure', 'automation', 'deployment', 'monitoring']
        },
        'Mobile Developer': {
            'languages': ['Swift', 'Kotlin', 'Java', 'JavaScript', 'TypeScript', 'Dart'],
            'technologies': ['React Native', 'Flutter', 'iOS', 'Android', 'Xcode', 'Android Studio', 'Firebase', 'Redux'],
            'keywords': ['mobile', 'ios', 'android', 'app', 'native']
        },
        'Machine Learning Engineer': {
            'languages': ['Python', 'C++', 'Java'],
            'technologies': ['TensorFlow', 'PyTorch', 'scikit-learn', 'Keras', 'MLflow', 'Kubeflow', 'Docker', 'AWS SageMaker', 'Azure ML', 'FastAPI', 'ONNX'],
            'keywords': ['machine learning', 'deep learning', 'neural network', 'model deployment', 'mlops']
        },
        'Cloud Engineer': {
            'languages': ['Python', 'Go', 'JavaScript', 'PowerShell'],
            'technologies': ['AWS', 'Azure', 'GCP', 'Terraform', 'CloudFormation', 'Lambda', 'S3', 'EC2', 'Kubernetes', 'Docker', 'Serverless'],
            'keywords': ['cloud', 'aws', 'azure', 'gcp', 'infrastructure', 'scalability']
        },
        'QA Engineer': {
            'languages': ['Python', 'JavaScript', 'Java'],
            'technologies': ['Selenium', 'Pytest', 'Jest', 'Cypress', 'JUnit', 'Postman', 'JMeter', 'Jenkins', 'TestNG'],
            'keywords': ['testing', 'qa', 'quality', 'automation', 'test cases', 'bug']
        },
        'Security Engineer': {
            'languages': ['Python', 'C', 'C++', 'Go', 'Bash'],
            'technologies': ['OWASP', 'Burp Suite', 'Metasploit', 'Wireshark', 'Nmap', 'Kali Linux', 'Splunk', 'IDS/IPS', 'Firewall'],
            'keywords': ['security', 'penetration', 'vulnerability', 'encryption', 'cybersecurity']
        },
        'Database Administrator': {
            'languages': ['SQL', 'Python', 'PowerShell', 'Bash'],
            'technologies': ['PostgreSQL', 'MySQL', 'Oracle', 'SQL Server', 'MongoDB', 'Redis', 'Backup', 'Replication', 'Performance Tuning'],
            'keywords': ['database', 'dba', 'sql', 'performance', 'backup', 'optimization']
        }
    }
    
    # Experience level thresholds
    EXPERIENCE_LEVELS = {
        'Junior': (0, 2),
        'Mid-Level': (2, 5),
        'Senior': (5, 10),
        'Lead': (10, float('inf'))
    }
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the recommender
        
        Args:
            data_path: Optional path to Stack Overflow dataset
        """
        self.data_path = data_path
        self.df = None
        
        if data_path and Path(data_path).exists():
            try:
                self.df = pd.read_csv(data_path)
                print(f"✅ Loaded dataset: {len(self.df)} records")
            except Exception as e:
                print(f"⚠️  Could not load dataset: {e}")
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name for better matching"""
        skill = skill.strip().lower()
        
        # Common variations
        normalizations = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'nodejs': 'node.js',
            'reactjs': 'react',
            'vuejs': 'vue',
            'nextjs': 'next.js',
            'postgresql': 'postgres',
            'mongo': 'mongodb',
            'k8s': 'kubernetes',
            'tf': 'tensorflow',
            'scikit': 'scikit-learn',
            'sklearn': 'scikit-learn',
            'html/css': 'html',
            'c++': 'cpp',
            'c#': 'csharp',
        }
        
        return normalizations.get(skill, skill)
    
    def calculate_skill_match(self, user_skills: List[str], role_requirements: Dict) -> float:
        """
        Calculate how well user's skills match a role
        
        Returns: Match score between 0 and 1
        """
        normalized_user_skills = [self.normalize_skill(s) for s in user_skills]
        
        # Check language matches
        language_matches = 0
        role_languages = [self.normalize_skill(lang) for lang in role_requirements['languages']]
        for skill in normalized_user_skills:
            if skill in role_languages:
                language_matches += 1
        
        # Check technology matches
        tech_matches = 0
        role_techs = [self.normalize_skill(tech) for tech in role_requirements['technologies']]
        for skill in normalized_user_skills:
            if skill in role_techs:
                tech_matches += 1
        
        # Calculate score
        total_matches = language_matches + tech_matches
        if total_matches == 0:
            return 0.0
        
        # Weight languages higher than technologies
        score = (language_matches * 1.5 + tech_matches) / (len(role_languages) + len(role_techs)) * 2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_experience_level(self, years: float) -> str:
        """Determine experience level from years"""
        for level, (min_years, max_years) in self.EXPERIENCE_LEVELS.items():
            if min_years <= years < max_years:
                return level
        return 'Junior'
    
    def recommend_roles(
        self,
        skills: List[str],
        experience_years: float = 0,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Recommend roles based on skills and experience
        
        Args:
            skills: List of user's skills (languages, frameworks, tools)
            experience_years: Years of professional experience
            top_n: Number of recommendations to return
        
        Returns:
            List of role recommendations with confidence scores
        """
        if not skills:
            return []
        
        experience_level = self.get_experience_level(experience_years)
        
        # Calculate match score for each role
        recommendations = []
        for role_name, requirements in self.ROLE_PATTERNS.items():
            match_score = self.calculate_skill_match(skills, requirements)
            
            if match_score > 0:  # Only include roles with some match
                # Get matching and missing skills
                normalized_user_skills = [self.normalize_skill(s) for s in skills]
                role_all_skills = (
                    [self.normalize_skill(s) for s in requirements['languages']] +
                    [self.normalize_skill(s) for s in requirements['technologies']]
                )
                
                matching_skills = [s for s in skills if self.normalize_skill(s) in role_all_skills]
                missing_skills = [
                    s for s in requirements['languages'][:3] + requirements['technologies'][:5]
                    if self.normalize_skill(s) not in normalized_user_skills
                ]
                
                recommendations.append({
                    'role': role_name,
                    'position': f"{experience_level} {role_name}",
                    'confidence': round(match_score, 2),
                    'experience_level': experience_level,
                    'matching_skills': matching_skills,
                    'suggested_skills': missing_skills[:5],  # Top 5 skills to learn
                    'description': self._get_role_description(role_name, experience_level)
                })
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations[:top_n]
    
    def _get_role_description(self, role: str, level: str) -> str:
        """Generate role description based on experience level"""
        descriptions = {
            'Backend Developer': f"{level} backend developer focusing on server-side logic, databases, and APIs",
            'Frontend Developer': f"{level} frontend developer creating user interfaces and web experiences",
            'Full Stack Developer': f"{level} full-stack developer working on both frontend and backend",
            'Data Scientist': f"{level} data scientist analyzing data and building predictive models",
            'Data Engineer': f"{level} data engineer building data pipelines and infrastructure",
            'DevOps Engineer': f"{level} DevOps engineer managing infrastructure and CI/CD pipelines",
            'Mobile Developer': f"{level} mobile developer creating iOS and Android applications",
            'Machine Learning Engineer': f"{level} ML engineer deploying and optimizing machine learning models",
            'Cloud Engineer': f"{level} cloud engineer designing and managing cloud infrastructure",
            'QA Engineer': f"{level} QA engineer ensuring software quality through testing",
            'Security Engineer': f"{level} security engineer protecting systems and data",
            'Database Administrator': f"{level} DBA managing and optimizing database systems"
        }
        return descriptions.get(role, f"{level} software professional")
    
    def get_skill_insights(self, skills: List[str]) -> Dict:
        """
        Get insights about user's skill profile
        
        Returns insights like skill categories, strengths, etc.
        """
        if not skills:
            return {'error': 'No skills provided'}
        
        # Categorize skills
        categories = {
            'languages': [],
            'frontend': [],
            'backend': [],
            'database': [],
            'devops': [],
            'data_science': [],
            'mobile': []
        }
        
        for skill in skills:
            normalized = self.normalize_skill(skill)
            
            # Categorize
            if any(normalized == self.normalize_skill(lang) 
                   for role_req in self.ROLE_PATTERNS.values() 
                   for lang in role_req['languages']):
                categories['languages'].append(skill)
            
            if any(normalized == self.normalize_skill(tech)
                   for tech in self.ROLE_PATTERNS['Frontend Developer']['technologies']):
                categories['frontend'].append(skill)
            
            if any(normalized == self.normalize_skill(tech)
                   for tech in self.ROLE_PATTERNS['Backend Developer']['technologies']):
                categories['backend'].append(skill)
            
            if normalized in ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'oracle']:
                categories['database'].append(skill)
            
            if any(normalized == self.normalize_skill(tech)
                   for tech in self.ROLE_PATTERNS['DevOps Engineer']['technologies']):
                categories['devops'].append(skill)
            
            if any(normalized == self.normalize_skill(tech)
                   for tech in self.ROLE_PATTERNS['Data Scientist']['technologies']):
                categories['data_science'].append(skill)
            
            if any(normalized == self.normalize_skill(tech)
                   for tech in self.ROLE_PATTERNS['Mobile Developer']['technologies']):
                categories['mobile'].append(skill)
        
        # Determine primary focus
        category_counts = {k: len(v) for k, v in categories.items() if v}
        primary_focus = max(category_counts, key=category_counts.get) if category_counts else 'general'
        
        return {
            'total_skills': len(skills),
            'skill_categories': {k: v for k, v in categories.items() if v},
            'primary_focus': primary_focus,
            'is_full_stack': len(categories['frontend']) > 0 and len(categories['backend']) > 0,
            'has_data_skills': len(categories['data_science']) > 0,
            'has_devops_skills': len(categories['devops']) > 0
        }


def create_recommender(data_path: Optional[str] = None) -> CareerRecommender:
    """
    Factory function to create a recommender instance
    
    If no data_path provided, looks for the default dataset location
    """
    if data_path is None:
        # Try to find the default dataset
        possible_paths = [
            Path(__file__).parent / 'data' / 'stackoverflow_cv_training_dataset.csv',
            Path.cwd() / 'apps' / 'cv_creation_agent' / 'data' / 'stackoverflow_cv_training_dataset.csv'
        ]
        
        for path in possible_paths:
            if path.exists():
                data_path = str(path)
                break
    
    return CareerRecommender(data_path)
