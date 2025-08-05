#!/usr/bin/env python3
"""
Comprehensive linting script for HA Visualiser.
Checks Python and JavaScript code for unused variables, methods, and other issues.
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set

class LintRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues_found = 0
        self.warnings_found = 0
        
    def run_python_lint(self) -> bool:
        """Run Python linting with pylint."""
        print("🐍 Running Python linting...")
        
        python_files = [
            "custom_components/ha_visualiser/__init__.py",
            "custom_components/ha_visualiser/graph_service.py", 
            "custom_components/ha_visualiser/websocket_api.py",
            "custom_components/ha_visualiser/config_flow.py"
        ]
        
        success = True
        
        for file_path in python_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue
                
            print(f"  Checking {file_path}...")
            
            try:
                # Run pylint
                result = subprocess.run([
                    sys.executable, '-m', 'pylint', 
                    str(full_path),
                    '--rcfile=.pylintrc',
                    '--output-format=json'
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.stdout:
                    try:
                        issues = json.loads(result.stdout)
                        self._process_pylint_issues(file_path, issues)
                    except json.JSONDecodeError:
                        # Fallback to text output
                        if result.stdout.strip():
                            print(f"    {result.stdout}")
                            
                if result.returncode != 0 and result.stderr:
                    print(f"    ❌ Pylint error: {result.stderr}")
                    success = False
                    
            except FileNotFoundError:
                print(f"    ⚠️  pylint not found, trying manual analysis...")
                self._manual_python_analysis(full_path)
                
        return success
    
    def _process_pylint_issues(self, file_path: str, issues: List[Dict]):
        """Process pylint JSON output."""
        if not issues:
            print(f"    ✅ No issues found")
            return
            
        error_count = 0
        warning_count = 0
        
        for issue in issues:
            severity = issue.get('type', 'unknown')
            message = issue.get('message', '')
            line = issue.get('line', 0)
            symbol = issue.get('symbol', '')
            
            if severity in ['error', 'fatal']:
                print(f"    ❌ Line {line}: {message} ({symbol})")
                error_count += 1
                self.issues_found += 1
            elif severity in ['warning', 'refactor', 'convention']:
                print(f"    ⚠️  Line {line}: {message} ({symbol})")
                warning_count += 1
                self.warnings_found += 1
                
        if error_count == 0 and warning_count == 0:
            print(f"    ✅ No significant issues found")
        else:
            print(f"    📊 Found {error_count} errors, {warning_count} warnings")
    
    def _manual_python_analysis(self, file_path: Path):
        """Manual Python analysis for unused variables and methods."""
        print(f"    🔍 Running manual analysis...")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Find unused imports
            unused_imports = self._find_unused_imports(content)
            if unused_imports:
                print(f"    ⚠️  Potentially unused imports: {', '.join(unused_imports)}")
                self.warnings_found += len(unused_imports)
                
            # Find unused methods
            unused_methods = self._find_unused_methods(content)
            if unused_methods:
                print(f"    ⚠️  Potentially unused methods: {', '.join(unused_methods)}")
                self.warnings_found += len(unused_methods)
                
            # Find unused variables
            unused_vars = self._find_unused_variables(content)
            if unused_vars:
                print(f"    ⚠️  Potentially unused variables: {', '.join(unused_vars)}")
                self.warnings_found += len(unused_vars)
                
            if not unused_imports and not unused_methods and not unused_vars:
                print(f"    ✅ No obvious unused items found")
                
        except Exception as e:
            print(f"    ❌ Error during manual analysis: {e}")
            self.issues_found += 1
    
    def _find_unused_imports(self, content: str) -> List[str]:
        """Find potentially unused imports."""
        lines = content.split('\n')
        imports = []
        
        # Find import statements
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # Extract import names
                if line.startswith('from '):
                    # from module import name1, name2
                    match = re.search(r'from\s+\S+\s+import\s+(.+)', line)
                    if match:
                        import_list = match.group(1)
                        for item in import_list.split(','):
                            item = item.strip().split(' as ')[0]  # Handle 'as' aliases
                            if item and not item.startswith('*'):
                                imports.append(item)
                else:
                    # import module
                    match = re.search(r'import\s+(.+)', line)
                    if match:
                        import_list = match.group(1)
                        for item in import_list.split(','):
                            item = item.strip().split(' as ')[0]  # Handle 'as' aliases
                            if item:
                                imports.append(item.split('.')[-1])  # Get last part for usage check
        
        # Check which imports are used
        unused = []
        for imp in imports:
            if imp not in ['_LOGGER', 'DOMAIN']:  # Skip common constants
                # Simple usage check - look for the import name in the rest of the file
                if content.count(imp) <= 1:  # Only appears in import line
                    unused.append(imp)
                    
        return unused
    
    def _find_unused_methods(self, content: str) -> List[str]:
        """Find potentially unused methods."""
        lines = content.split('\n')
        methods = []
        
        # Find method definitions
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('def ') or line.startswith('async def '):
                match = re.search(r'def\s+(\w+)', line)
                if match:
                    method_name = match.group(1)
                    if not method_name.startswith('_') or method_name.startswith('__'):
                        # Skip private methods and magic methods
                        continue
                    methods.append(method_name)
        
        # Check usage
        unused = []
        for method in methods:
            if method.startswith('_') and not method.startswith('__'):
                # For private methods, check if they're called anywhere
                call_pattern = f'{method}('
                if content.count(call_pattern) <= 1:  # Only definition
                    unused.append(method)
                    
        return unused
    
    def _find_unused_variables(self, content: str) -> List[str]:
        """Find potentially unused variables."""
        # This is a simplified check - could be enhanced
        unused = []
        
        # Look for variable assignments that are never used
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Simple pattern for variable assignment
            match = re.match(r'\s*(\w+)\s*=\s*', line)
            if match:
                var_name = match.group(1)
                if not var_name.startswith('_') and var_name.islower():
                    # Check if used elsewhere
                    if content.count(var_name) <= 1:
                        unused.append(var_name)
                        
        return unused
    
    def run_javascript_lint(self) -> bool:
        """Run JavaScript linting with ESLint."""
        print("🌐 Running JavaScript linting...")
        
        js_files = [
            "custom_components/ha_visualiser/www/ha-visualiser-panel.js"
        ]
        
        success = True
        
        for file_path in js_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue
                
            print(f"  Checking {file_path}...")
            
            try:
                # Try ESLint first
                result = subprocess.run([
                    'npx', 'eslint', str(full_path), '--format=json'
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.stdout:
                    try:
                        eslint_output = json.loads(result.stdout)
                        self._process_eslint_issues(file_path, eslint_output)
                    except json.JSONDecodeError:
                        if result.stdout.strip():
                            print(f"    {result.stdout}")
                            
                if result.returncode != 0 and result.stderr:
                    if "command not found" in result.stderr or "not found" in result.stderr:
                        print(f"    ⚠️  ESLint not found, running manual analysis...")
                        self._manual_javascript_analysis(full_path)
                    else:
                        print(f"    ❌ ESLint error: {result.stderr}")
                        success = False
                        
            except FileNotFoundError:
                print(f"    ⚠️  ESLint not found, running manual analysis...")
                self._manual_javascript_analysis(full_path)
                
        return success
    
    def _process_eslint_issues(self, file_path: str, eslint_output: List[Dict]):
        """Process ESLint JSON output."""
        if not eslint_output:
            print(f"    ✅ No issues found")
            return
            
        for file_result in eslint_output:
            messages = file_result.get('messages', [])
            
            if not messages:
                print(f"    ✅ No issues found")
                continue
                
            error_count = 0
            warning_count = 0
            
            for message in messages:
                severity = message.get('severity', 1)
                msg = message.get('message', '')
                line = message.get('line', 0)
                rule_id = message.get('ruleId', '')
                
                if severity == 2:  # Error
                    print(f"    ❌ Line {line}: {msg} ({rule_id})")
                    error_count += 1
                    self.issues_found += 1
                else:  # Warning
                    print(f"    ⚠️  Line {line}: {msg} ({rule_id})")
                    warning_count += 1
                    self.warnings_found += 1
                    
            print(f"    📊 Found {error_count} errors, {warning_count} warnings")
    
    def _manual_javascript_analysis(self, file_path: Path):
        """Manual JavaScript analysis for unused variables and functions."""
        print(f"    🔍 Running manual analysis...")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Find unused functions
            unused_functions = self._find_unused_js_functions(content)
            if unused_functions:
                print(f"    ⚠️  Potentially unused functions: {', '.join(unused_functions)}")
                self.warnings_found += len(unused_functions)
                
            # Find unused variables
            unused_vars = self._find_unused_js_variables(content)
            if unused_vars:
                print(f"    ⚠️  Potentially unused variables: {', '.join(unused_vars)}")
                self.warnings_found += len(unused_vars)
                
            # Check for console.log statements
            console_logs = content.count('console.log')
            if console_logs > 0:
                print(f"    ℹ️  Found {console_logs} console.log statements (consider removing for production)")
                
            if not unused_functions and not unused_vars:
                print(f"    ✅ No obvious unused items found")
                
        except Exception as e:
            print(f"    ❌ Error during manual analysis: {e}")
            self.issues_found += 1
    
    def _find_unused_js_functions(self, content: str) -> List[str]:
        """Find potentially unused JavaScript functions."""
        functions = []
        
        # Find function declarations and expressions
        function_patterns = [
            r'function\s+(\w+)',  # function name() {}
            r'(\w+)\s*=\s*function',  # name = function() {}
            r'(\w+)\s*=\s*\([^)]*\)\s*=>'  # name = () => {}
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, content)
            functions.extend(matches)
        
        # Check usage
        unused = []
        for func in functions:
            if func not in ['constructor', 'connectedCallback', 'disconnectedCallback']:
                # Count occurrences (definition + calls)
                call_pattern = f'{func}('
                if content.count(call_pattern) <= 1:  # Only definition
                    unused.append(func)
                    
        return unused
    
    def _find_unused_js_variables(self, content: str) -> List[str]:
        """Find potentially unused JavaScript variables."""
        unused = []
        
        # Look for variable declarations
        var_patterns = [
            r'(?:let|const|var)\s+(\w+)',
            r'(\w+)\s*='
        ]
        
        variables = set()
        for pattern in var_patterns:
            matches = re.findall(pattern, content)
            variables.update(matches)
        
        # Check usage
        for var in variables:
            if len(var) > 1 and var.islower():  # Skip single chars and constants
                if content.count(var) <= 1:  # Only declaration
                    unused.append(var)
                    
        return unused
    
    def run_all_lints(self) -> bool:
        """Run all linting checks."""
        print("🔍 HA Visualiser Linting Suite")
        print("=" * 60)
        
        python_success = self.run_python_lint()
        print()
        js_success = self.run_javascript_lint()
        
        print("\n" + "=" * 60)
        print(f"🏁 Linting Results:")
        print(f"   Issues: {self.issues_found}")
        print(f"   Warnings: {self.warnings_found}")
        
        if self.issues_found == 0:
            print("✅ No critical issues found!")
            return True
        else:
            print("❌ Critical issues found - please review")
            return False

def main():
    """Main entry point."""
    runner = LintRunner()
    success = runner.run_all_lints()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())