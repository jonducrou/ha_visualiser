#!/usr/bin/env python3
"""
Simple standalone linting script for HA Visualiser.
No external dependencies required - focuses on unused variables/methods.
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict

class SimpleASTAnalyzer(ast.NodeVisitor):
    """AST analyzer to find unused variables and methods."""
    
    def __init__(self):
        self.defined_functions = set()
        self.called_functions = set()
        self.defined_variables = set()
        self.used_variables = set()
        self.imported_names = set()
        self.used_imports = set()
        self.class_methods = defaultdict(set)
        self.method_calls = defaultdict(set)
        self.current_class = None
        
    def visit_FunctionDef(self, node):
        if self.current_class:
            self.class_methods[self.current_class].add(node.name)
        else:
            self.defined_functions.add(node.name)
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        if self.current_class:
            self.class_methods[self.current_class].add(node.name)
        else:
            self.defined_functions.add(node.name)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called_functions.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                if self.current_class:
                    self.method_calls[self.current_class].add(node.func.attr)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined_variables.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.used_variables.add(node.id)
            if node.id in self.imported_names:
                self.used_imports.add(node.id)
        self.generic_visit(node)
        
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            self.imported_names.add(name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names.add(name)
        self.generic_visit(node)

class SimpleLinter:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues_found = 0
        self.warnings_found = 0
        
    def analyze_python_file(self, file_path: Path) -> Dict:
        """Analyze a Python file for unused items."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            analyzer = SimpleASTAnalyzer()
            analyzer.visit(tree)
            
            results = {
                'unused_imports': analyzer.imported_names - analyzer.used_imports,
                'unused_functions': analyzer.defined_functions - analyzer.called_functions,
                'unused_variables': set(),
                'unused_methods': set()
            }
            
            # Find unused variables (basic heuristic)
            for var in analyzer.defined_variables:
                if var not in analyzer.used_variables and not var.startswith('_'):
                    results['unused_variables'].add(var)
                    
            # Find unused methods
            for class_name, methods in analyzer.class_methods.items():
                called = analyzer.method_calls.get(class_name, set())
                unused = methods - called
                # Filter out special methods and common patterns
                unused = {m for m in unused if not m.startswith('__') and m not in {
                    'setUp', 'tearDown', 'connectedCallback', 'disconnectedCallback'
                }}
                results['unused_methods'].update(unused)
                
            return results
            
        except Exception as e:
            print(f"    ❌ Error analyzing {file_path}: {e}")
            self.issues_found += 1
            return {}
    
    def analyze_javascript_file(self, file_path: Path) -> Dict:
        """Analyze a JavaScript file for unused items."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            results = {
                'unused_functions': [],
                'unused_variables': [],
                'console_logs': content.count('console.log'),
                'syntax_issues': []
            }
            
            # Find function definitions
            function_patterns = [
                r'function\s+(\w+)',  # function name() {}
                r'(\w+)\s*=\s*function',  # name = function() {}
                r'(\w+)\s*=\s*\([^)]*\)\s*=>',  # name = () => {}
                r'(\w+)\s*\([^)]*\)\s*{'  # method() {}
            ]
            
            defined_functions = set()
            for pattern in function_patterns:
                matches = re.findall(pattern, content)
                defined_functions.update(matches)
            
            # Check usage
            for func in defined_functions:
                if func not in ['constructor', 'connectedCallback', 'disconnectedCallback']:
                    # Count function calls
                    call_count = content.count(f'{func}(')
                    if call_count <= 1:  # Only definition
                        results['unused_functions'].append(func)
            
            # Find variable definitions
            var_patterns = [
                r'(?:let|const|var)\s+(\w+)',
                r'(\w+)\s*=\s*[^=]'  # assignment but not comparison
            ]
            
            defined_vars = set()
            for pattern in var_patterns:
                matches = re.findall(pattern, content)
                defined_vars.update(matches)
            
            # Check variable usage
            for var in defined_vars:
                if len(var) > 1 and var not in ['console', 'window', 'document']:
                    var_count = len(re.findall(r'\b' + re.escape(var) + r'\b', content))
                    if var_count <= 1:  # Only definition
                        results['unused_variables'].append(var)
            
            # Check for common syntax issues
            if content.count('{') != content.count('}'):
                results['syntax_issues'].append("Mismatched braces")
            if content.count('(') != content.count(')'):
                results['syntax_issues'].append("Mismatched parentheses")
                
            return results
            
        except Exception as e:
            print(f"    ❌ Error analyzing {file_path}: {e}")
            self.issues_found += 1
            return {}
    
    def run_python_analysis(self):
        """Run Python analysis."""
        print("🐍 Analyzing Python files...")
        
        python_files = [
            "custom_components/ha_visualiser/__init__.py",
            "custom_components/ha_visualiser/graph_service.py", 
            "custom_components/ha_visualiser/websocket_api.py",
            "custom_components/ha_visualiser/config_flow.py"
        ]
        
        for file_path in python_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                continue
                
            print(f"  📄 {file_path}")
            results = self.analyze_python_file(full_path)
            
            if not results:
                continue
                
            issues_found = False
            
            if results.get('unused_imports'):
                # Filter out common false positives for HA integrations
                unused = [imp for imp in results['unused_imports'] 
                         if imp not in ['_LOGGER', 'DOMAIN', 'logger', 'annotations', 'Any', 'HomeAssistant', 'ConfigType']]
                if unused:
                    print(f"    ⚠️  Unused imports: {', '.join(unused)}")
                    self.warnings_found += len(unused)
                    issues_found = True
            
            if results.get('unused_functions'):
                # Filter out HA integration entry points and websocket handlers
                ha_entry_points = {'async_setup', 'async_setup_entry', 'async_unload_entry', 'async_migrate_entry'}
                websocket_handlers = {'websocket_search_entities', 'websocket_get_neighborhood', 
                                    'websocket_get_filtered_neighborhood', 'websocket_get_graph_statistics',
                                    'async_register_websocket_handlers'}
                unused = [func for func in results['unused_functions'] 
                         if not func.startswith('_') and func not in ha_entry_points and func not in websocket_handlers]
                if unused:
                    print(f"    ⚠️  Unused functions: {', '.join(unused)}")
                    self.warnings_found += len(unused)
                    issues_found = True
            
            if results.get('unused_methods'):
                # Filter out HA integration and API methods that are called externally
                external_api_methods = {'search_entities', 'get_entity_neighborhood', 'get_graph_statistics', 
                                      'get_filtered_neighborhood', 'async_step_user'}
                unused = [method for method in results['unused_methods'] 
                         if method not in external_api_methods]
                if unused:
                    print(f"    ⚠️  Unused methods: {', '.join(unused)}")
                    self.warnings_found += len(unused)
                    issues_found = True
            
            if results.get('unused_variables'):
                common_vars = {'i', 'j', 'k', 'x', 'y', 'e', 'ex', '_', 'PLATFORMS', 'VERSION', 'icon', 'id'}
                unused = [var for var in results['unused_variables'] 
                         if var not in common_vars and len(var) > 1]
                if unused:
                    print(f"    ⚠️  Unused variables: {', '.join(unused)}")
                    self.warnings_found += len(unused)
                    issues_found = True
            
            if not issues_found:
                print(f"    ✅ No issues found")
    
    def run_javascript_analysis(self):
        """Run JavaScript analysis."""
        print("\n🌐 Analyzing JavaScript files...")
        
        js_files = [
            "custom_components/ha_visualiser/www/ha-visualiser-panel.js"
        ]
        
        for file_path in js_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                continue
                
            print(f"  📄 {file_path}")
            results = self.analyze_javascript_file(full_path)
            
            if not results:
                continue
                
            issues_found = False
            
            if results.get('syntax_issues'):
                for issue in results['syntax_issues']:
                    print(f"    ❌ Syntax issue: {issue}")
                    self.issues_found += 1
                issues_found = True
            
            if results.get('unused_functions'):
                # Filter out false positives - JS regex often picks up keywords
                js_keywords = {'function', 'if', 'else', 'for', 'while', 'catch', 'try', 'return'}
                common_false_positives = {'resolve', 'reject', 'callback', 'handler', 'properties'}
                unused = [func for func in results['unused_functions'] 
                         if func not in js_keywords and func not in common_false_positives 
                         and len(func) > 2]
                if unused:
                    print(f"    ⚠️  Unused functions: {', '.join(unused)}")
                    self.warnings_found += len(unused)
                    issues_found = True
            
            if results.get('unused_variables'):
                # Filter out common false positives and DOM-related variables
                dom_vars = {'script', 'div', 'span', 'error', 'event', 'data', 'src', 'onload'}
                css_vars = {'borderColor', 'background', 'color', 'width', 'height'}
                common_vars = {'i', 'j', 'e', 'x', 'y', 'id', 'key', 'value', 'name'}
                unused = [var for var in results['unused_variables'] 
                         if var not in dom_vars and var not in css_vars and var not in common_vars
                         and len(var) > 1 and not var.isupper()]
                if unused:
                    print(f"    ⚠️  Unused variables: {', '.join(unused)}")
                    self.warnings_found += len(unused)
                    issues_found = True
            
            console_logs = results.get('console_logs', 0)
            if console_logs > 5:  # Allow some console.log for debugging
                print(f"    ℹ️  Found {console_logs} console.log statements (consider reducing for production)")
            
            if not issues_found:
                print(f"    ✅ No issues found")
    
    def run_analysis(self):
        """Run complete analysis."""
        print("🔍 Simple Code Analysis")
        print("=" * 50)
        
        self.run_python_analysis()
        self.run_javascript_analysis()
        
        print("\n" + "=" * 50)
        print(f"📊 Analysis Results:")
        print(f"   Critical Issues: {self.issues_found}")
        print(f"   Warnings: {self.warnings_found}")
        
        if self.issues_found == 0:
            print("✅ No critical issues found!")
            return True
        else:
            print("❌ Critical issues found - please review")
            return False

def main():
    """Main entry point."""
    linter = SimpleLinter()
    success = linter.run_analysis()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())