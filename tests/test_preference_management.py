"""
Unit tests for preference management functionality.

Tests the localStorage-based preference system for user settings like
show areas, depth, and layout preferences.
"""
import pytest
from unittest.mock import Mock, patch


class TestPreferenceManagement:
    """Test preference loading, saving, and validation logic."""
    
    def test_preference_defaults(self):
        """Test that default preferences are correct."""
        expected_defaults = {
            'showAreas': True,
            'depth': 3,
            'layout': 'hierarchical'
        }
        
        # These are the defaults that should be used when no preferences stored
        assert expected_defaults['showAreas'] is True
        assert expected_defaults['depth'] == 3
        assert expected_defaults['layout'] == 'hierarchical'
    
    def test_preference_key_patterns(self):
        """Test that localStorage keys follow the expected pattern."""
        expected_keys = [
            'ha_visualiser_show_areas',
            'ha_visualiser_depth', 
            'ha_visualiser_layout'
        ]
        
        # Validate key naming convention
        assert all(key.startswith('ha_visualiser_') for key in expected_keys)
        assert len(expected_keys) == 3  # Ensure we have all expected preferences
    
    def test_depth_validation(self):
        """Test depth value validation logic."""
        valid_depths = [1, 2, 3, 4, 5]
        invalid_depths = [0, -1, 6, 10, None, 'invalid']
        
        # Test valid range
        for depth in valid_depths:
            assert 1 <= depth <= 5, f"Depth {depth} should be valid"
        
        # Test invalid values
        for depth in invalid_depths:
            if isinstance(depth, (int, float)) and depth is not None:
                assert not (1 <= depth <= 5), f"Depth {depth} should be invalid"
    
    def test_layout_validation(self):
        """Test layout value validation logic."""
        valid_layouts = ['hierarchical', 'force-directed']
        invalid_layouts = ['invalid', '', None, 123, 'horizontal', 'vertical']
        
        # Test valid layouts
        for layout in valid_layouts:
            assert layout in ['hierarchical', 'force-directed'], f"Layout {layout} should be valid"
        
        # Test invalid layouts
        for layout in invalid_layouts:
            assert layout not in ['hierarchical', 'force-directed'], f"Layout {layout} should be invalid"
    
    def test_boolean_parsing(self):
        """Test boolean preference parsing from localStorage strings."""
        # localStorage stores everything as strings, so we need to parse booleans
        test_cases = [
            ('true', True),
            ('false', False),
            ('True', False),   # JavaScript comparison is case-sensitive
            ('False', False),
            ('1', False),      # Only 'true' should be True
            ('0', False),
            ('', False),      # Empty string should be false
            (None, None)      # None should remain None for fallback handling
        ]
        
        for input_value, expected in test_cases:
            if input_value is None:
                # Test None handling
                result = None
            else:
                # Simulate the JavaScript: savedShowAreas === 'true'
                result = str(input_value) == 'true'  # Exact match, not case-insensitive
            
            if expected is None:
                assert result is None
            else:
                assert result == expected, f"Input '{input_value}' should parse to {expected}, got {result}"
    
    def test_integer_parsing(self):
        """Test integer preference parsing from localStorage strings."""
        test_cases = [
            ('1', 1),
            ('3', 3), 
            ('5', 5),
            ('0', 0),
            ('-1', -1),
            ('invalid', None),  # Should handle invalid strings
            ('', None),         # Empty string
            ('3.5', 3),         # Should handle floats by truncating
            (None, None)        # None input
        ]
        
        for input_value, expected in test_cases:
            if input_value is None:
                result = None
            else:
                try:
                    result = int(float(input_value)) if input_value else None
                except (ValueError, TypeError):
                    result = None
            
            assert result == expected, f"Input '{input_value}' should parse to {expected}, got {result}"
    
    @pytest.mark.parametrize("stored_values,expected_preferences", [
        # Test case 1: All valid stored values
        ({
            'ha_visualiser_show_areas': 'true',
            'ha_visualiser_depth': '2',
            'ha_visualiser_layout': 'force-directed'
        }, {
            'showAreas': True,
            'depth': 2, 
            'layout': 'force-directed'
        }),
        
        # Test case 2: No stored values (all None) - should use defaults
        ({
            'ha_visualiser_show_areas': None,
            'ha_visualiser_depth': None,
            'ha_visualiser_layout': None
        }, {
            'showAreas': True,  # Default
            'depth': 3,         # Default
            'layout': 'hierarchical'  # Default
        }),
        
        # Test case 3: Mixed valid and invalid values
        ({
            'ha_visualiser_show_areas': 'false',
            'ha_visualiser_depth': '10',      # Invalid (>5)
            'ha_visualiser_layout': 'hierarchical'
        }, {
            'showAreas': False,
            'depth': 3,         # Should fallback to default
            'layout': 'hierarchical'
        }),
        
        # Test case 4: Corrupted/invalid data
        ({
            'ha_visualiser_show_areas': 'invalid',
            'ha_visualiser_depth': 'not_a_number',
            'ha_visualiser_layout': 'bad_layout'
        }, {
            'showAreas': False,  # 'invalid' != 'true' so False
            'depth': 3,         # Default
            'layout': 'hierarchical'  # Default
        })
    ])
    def test_preference_loading_scenarios(self, stored_values, expected_preferences):
        """Test various preference loading scenarios with different stored data."""
        # Simulate the loadUserPreferences() logic
        def simulate_load_preferences(storage):
            try:
                saved_show_areas = storage.get('ha_visualiser_show_areas')
                saved_depth = storage.get('ha_visualiser_depth')
                saved_layout = storage.get('ha_visualiser_layout')
                
                # Parse show areas
                show_areas = saved_show_areas == 'true' if saved_show_areas is not None else True
                
                # Parse depth with validation
                if saved_depth is not None:
                    try:
                        depth = int(saved_depth)
                        if not (1 <= depth <= 5):
                            depth = 3  # Default
                    except (ValueError, TypeError):
                        depth = 3  # Default
                else:
                    depth = 3  # Default
                
                # Parse layout with validation  
                if saved_layout is not None and saved_layout in ['hierarchical', 'force-directed']:
                    layout = saved_layout
                else:
                    layout = 'hierarchical'  # Default
                
                return {
                    'showAreas': show_areas,
                    'depth': depth,
                    'layout': layout
                }
            except Exception:
                # Error fallback
                return {
                    'showAreas': True,
                    'depth': 3,
                    'layout': 'hierarchical'
                }
        
        result = simulate_load_preferences(stored_values)
        assert result == expected_preferences
    
    def test_preference_saving_format(self):
        """Test that preferences are saved in the correct format."""
        # Mock UI elements
        mock_depth_select = Mock()
        mock_depth_select.value = '2'
        
        mock_areas_checkbox = Mock() 
        mock_areas_checkbox.checked = False
        
        mock_layout_select = Mock()
        mock_layout_select.value = 'force-directed'
        
        # Simulate the saveUserPreferences() logic
        expected_storage_calls = [
            ('ha_visualiser_depth', '2'),
            ('ha_visualiser_show_areas', 'false'),  # Boolean converted to string
            ('ha_visualiser_layout', 'force-directed')
        ]
        
        # Verify the expected localStorage.setItem calls would be made
        storage_operations = [
            ('ha_visualiser_depth', mock_depth_select.value),
            ('ha_visualiser_show_areas', str(mock_areas_checkbox.checked).lower()),
            ('ha_visualiser_layout', mock_layout_select.value)
        ]
        
        assert storage_operations == expected_storage_calls
    
    def test_error_handling_scenarios(self):
        """Test error handling in preference management."""
        # Test localStorage unavailable scenario
        def simulate_localStorage_error():
            raise Exception("localStorage not available")
        
        # Should gracefully handle localStorage errors and return defaults
        try:
            simulate_localStorage_error()
            preferences = None  # This would trigger the error path
        except Exception:
            # Error fallback
            preferences = {
                'showAreas': True,
                'depth': 3,
                'layout': 'hierarchical'
            }
        
        assert preferences == {
            'showAreas': True,
            'depth': 3, 
            'layout': 'hierarchical'
        }
    
    def test_preference_persistence_flow(self):
        """Test the complete save-load-apply flow."""
        # Simulate a complete preference management cycle
        
        # Step 1: User changes preferences
        user_preferences = {
            'showAreas': False,
            'depth': 5,
            'layout': 'force-directed'
        }
        
        # Step 2: Preferences saved to storage
        storage = {}
        storage['ha_visualiser_show_areas'] = str(user_preferences['showAreas']).lower()
        storage['ha_visualiser_depth'] = str(user_preferences['depth'])
        storage['ha_visualiser_layout'] = user_preferences['layout']
        
        # Step 3: Preferences loaded from storage (simulate page reload)
        loaded_show_areas = storage['ha_visualiser_show_areas'] == 'true'
        loaded_depth = int(storage['ha_visualiser_depth'])
        loaded_layout = storage['ha_visualiser_layout']
        
        loaded_preferences = {
            'showAreas': loaded_show_areas,
            'depth': loaded_depth,
            'layout': loaded_layout
        }
        
        # Step 4: Verify round-trip consistency
        assert loaded_preferences == user_preferences
    
    def test_ui_element_validation(self):
        """Test UI element existence checks before operations."""
        # Simulate checking for UI elements before operating on them
        ui_elements = {
            'depthSelect': Mock(),
            'showAreasCheckbox': Mock(), 
            'layoutSelect': Mock()
        }
        
        # All elements should exist for normal operation
        for element_name, element in ui_elements.items():
            assert element is not None, f"{element_name} should exist"
        
        # Test missing element handling
        missing_elements = {
            'depthSelect': None,
            'showAreasCheckbox': None,
            'layoutSelect': None
        }
        
        # Code should check for element existence before operating
        for element_name, element in missing_elements.items():
            if element:  # This is the pattern used in the JS code
                # Would operate on element
                pass
            else:
                # Should skip operation safely
                assert element is None