"""
Universal Factbook Data Loader
One centralized system that handles ALL Excel files dynamically
No need for individual loaders per section
"""

import pandas as pd
import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversalFactbookLoader:
    """
    Single data loader that handles ALL factbook Excel files
    Automatically detects data structure and provides consistent interface
    """
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize universal loader
        
        Args:
            data_directory: Directory containing all Excel files
        """
        self.data_directory = data_directory
        self.file_cache = {}
        self.last_scan = None
        
        # Factbook file mapping (from your factbook landing page)
        self.factbook_files = {
            # Tier 2 files
            'counselling': 'counselling.xlsx',
            'credits': 'credits.xlsx',
            'enrollment': 'enrolment_data.xlsx',
            'graduation': 'GraduationData.xlsx',
            'governance-admin': 'GovernenceAndAdmin.xlsx',
            'higher-faculty': 'HigherFaculty.xlsx',
            'hr-appointments': 'HrAppointments.xlsx',
            'hr-data': 'HrData.xlsx',
            'ojt-training': 'ojt_training_report.xlsx',
            'outreach': 'outreach_activities.xlsx',
            'programmes': 'ProgrammeOffering.xlsx',
            'student-labour': 'student_labour_report.xlsx',
            'teaching-load': 'Teaching Load.xlsx',
            
            # Tier 3 files  
            'debt-collection': 'debt_collection.xlsx',
            'endowment-funds': 'endowment_funds.xlsx',
            'financial-data': 'financial_data.xlsx',
            'gate-funding': 'gate_funding.xlsx',
            'income-units': 'income_generating_units.xlsx',
            'scholarships': 'scholarship_discount_tuition.xlsx',
            'subsidies': 'subsidies.xlsx'
        }
    
    def get_file_path(self, section_key: str) -> str:
        """Get full file path for a section"""
        filename = self.factbook_files.get(section_key)
        if not filename:
            raise ValueError(f"Unknown section: {section_key}")
        return os.path.join(self.data_directory, filename)
    
    def _file_was_modified(self, file_path: str) -> bool:
        """Check if file has been modified since last cache"""
        try:
            current_modified = os.path.getmtime(file_path)
            cached_time = self.file_cache.get(file_path, {}).get('last_modified', 0)
            return current_modified > cached_time
        except OSError:
            return True
    
    def _clean_numeric_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean numeric columns in any DataFrame"""
        df_clean = df.copy()
        
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                # Try to convert to numeric if it looks like numbers
                sample_values = df_clean[col].dropna().astype(str).head(10)
                if any(any(char.isdigit() for char in str(val)) for val in sample_values):
                    # Clean currency symbols, commas, spaces
                    df_clean[col] = df_clean[col].astype(str).str.replace(r'[\$,\s%]', '', regex=True)
                    df_clean[col] = df_clean[col].replace(['-', '', 'nan', 'None', 'null'], '0')
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='ignore')
        
        return df_clean
    
    def _detect_year_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detect year columns or values in any DataFrame"""
        year_patterns = []
        
        # Check column names
        for col in df.columns:
            col_str = str(col)
            if '20' in col_str and any(sep in col_str for sep in ['-', '/', '_']):
                year_patterns.append(col_str)
        
        # Check cell values for year patterns
        for col in df.columns:
            sample_values = df[col].dropna().astype(str).head(20)
            for val in sample_values:
                if '20' in val and any(sep in val for sep in ['-', '/', '_']) and len(val) > 7:
                    year_patterns.append(val)
                    break
        
        return sorted(list(set(year_patterns)))
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze any DataFrame and return its structure"""
        analysis = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'year_patterns': self._detect_year_patterns(df),
            'numeric_columns': [],
            'text_columns': [],
            'has_totals': False,
            'has_percentages': False
        }
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                analysis['numeric_columns'].append(col)
            elif pd.api.types.is_numeric_dtype(df[col]):
                analysis['numeric_columns'].append(col)
            else:
                analysis['text_columns'].append(col)
        
        # Check for common patterns
        df_str = df.astype(str).apply(lambda x: ' '.join(x)).str.lower()
        if any('total' in text for text in df_str):
            analysis['has_totals'] = True
        if any('%' in text for text in df_str):
            analysis['has_percentages'] = True
            
        return analysis
    
    def load_section_data(self, section_key: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load data for any factbook section
        
        Args:
            section_key: Section identifier (e.g., 'enrollment', 'financial-data')
            force_reload: Force reload even if cached
            
        Returns:
            Dictionary with all data and metadata for the section
        """
        file_path = self.get_file_path(section_key)
        
        # Check cache
        if not force_reload and not self._file_was_modified(file_path):
            cached_data = self.file_cache.get(file_path, {}).get('data')
            if cached_data:
                logger.info(f"Using cached data for {section_key}")
                return cached_data
        
        logger.info(f"Loading fresh data for {section_key} from {file_path}")
        
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return self._get_empty_response(section_key, f"File not found: {file_path}")
            
            # Read Excel file with all sheets
            excel_file = pd.ExcelFile(file_path)
            sheets_data = {}
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    if not df.empty:
                        # Clean the data
                        df_clean = self._clean_numeric_data(df)
                        
                        # Analyze structure
                        analysis = self._analyze_data_structure(df_clean)
                        
                        sheets_data[sheet_name] = {
                            'data': df_clean,
                            'analysis': analysis,
                            'raw_data': df  # Keep original for reference
                        }
                        
                        logger.info(f"Loaded sheet '{sheet_name}' with shape {df.shape}")
                        
                except Exception as e:
                    logger.warning(f"Could not load sheet '{sheet_name}': {e}")
            
            if not sheets_data:
                return self._get_empty_response(section_key, "No valid sheets found")
            
            # Create response
            response = {
                'section': section_key,
                'file_path': file_path,
                'sheets': sheets_data,
                'available_years': self._extract_all_years(sheets_data),
                'summary': self._create_summary(sheets_data),
                'loaded_at': datetime.now().isoformat(),
                'success': True
            }
            
            # Cache the result
            self.file_cache[file_path] = {
                'data': response,
                'last_modified': os.path.getmtime(file_path)
            }
            
            logger.info(f"Successfully loaded {section_key}")
            return response
            
        except Exception as e:
            logger.error(f"Error loading {section_key}: {e}")
            return self._get_empty_response(section_key, str(e))
    
    def _extract_all_years(self, sheets_data: Dict) -> List[str]:
        """Extract all year patterns from all sheets"""
        all_years = set()
        
        for sheet_info in sheets_data.values():
            years = sheet_info['analysis']['year_patterns']
            all_years.update(years)
        
        return sorted(list(all_years))
    
    def _create_summary(self, sheets_data: Dict) -> Dict[str, Any]:
        """Create summary of the data"""
        total_rows = sum(sheet['data'].shape[0] for sheet in sheets_data.values())
        total_sheets = len(sheets_data)
        
        return {
            'total_sheets': total_sheets,
            'total_rows': total_rows,
            'sheet_names': list(sheets_data.keys()),
            'has_numeric_data': any(sheet['analysis']['numeric_columns'] 
                                  for sheet in sheets_data.values()),
            'has_year_data': any(sheet['analysis']['year_patterns'] 
                               for sheet in sheets_data.values())
        }
    
    def _get_empty_response(self, section_key: str, error_message: str) -> Dict[str, Any]:
        """Return empty response structure"""
        return {
            'section': section_key,
            'file_path': self.get_file_path(section_key),
            'sheets': {},
            'available_years': [],
            'summary': {'total_sheets': 0, 'total_rows': 0, 'error': error_message},
            'loaded_at': datetime.now().isoformat(),
            'success': False,
            'error': error_message
        }
    
    def get_available_sections(self) -> List[str]:
        """Get list of all available factbook sections"""
        return list(self.factbook_files.keys())
    
    def get_section_summary(self, section_key: str) -> Dict[str, Any]:
        """Get quick summary of a section without loading full data"""
        file_path = self.get_file_path(section_key)
        
        try:
            if not os.path.exists(file_path):
                return {'exists': False, 'error': 'File not found'}
            
            # Quick scan without loading all data
            excel_file = pd.ExcelFile(file_path)
            
            return {
                'exists': True,
                'file_path': file_path,
                'sheet_names': excel_file.sheet_names,
                'file_size': os.path.getsize(file_path),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def reload_all_sections(self) -> Dict[str, bool]:
        """Force reload all sections - useful for admin refresh"""
        results = {}
        
        for section_key in self.factbook_files.keys():
            try:
                self.load_section_data(section_key, force_reload=True)
                results[section_key] = True
            except Exception as e:
                logger.error(f"Failed to reload {section_key}: {e}")
                results[section_key] = False
        
        return results
    
    def clear_cache(self):
        """Clear all cached data"""
        self.file_cache.clear()
        logger.info("Data cache cleared")


# Global instance - single loader for entire application
universal_loader = UniversalFactbookLoader()

# Convenience functions for easy use throughout the application
def load_factbook_section(section_key: str, force_reload: bool = False) -> Dict[str, Any]:
    """
    Load any factbook section data
    
    Examples:
        load_factbook_section('enrollment')
        load_factbook_section('financial-data')
        load_factbook_section('student-labour')
    """
    return universal_loader.load_section_data(section_key, force_reload)

def get_section_years(section_key: str) -> List[str]:
    """Get available years for any section"""
    data = load_factbook_section(section_key)
    return data.get('available_years', [])

def get_all_sections() -> List[str]:
    """Get list of all available factbook sections"""
    return universal_loader.get_available_sections()

def refresh_section(section_key: str) -> bool:
    """Force refresh a specific section"""
    try:
        universal_loader.load_section_data(section_key, force_reload=True)
        return True
    except Exception:
        return False

def get_section_info(section_key: str) -> Dict[str, Any]:
    """Get basic info about a section without loading full data"""
    return universal_loader.get_section_summary(section_key)