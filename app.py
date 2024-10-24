import streamlit as st
import numpy as np
from PIL import Image
import os

def load_images():
    try:
        current_dir = os.path.dirname(__file__)
        image1_path = os.path.join(current_dir, "image1.jpg")
        image2_path = os.path.join(current_dir, "image2.jpg")
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)
        return image1, image2
    except FileNotFoundError:
        st.warning("Image files not found. Please ensure 'image1.jpg' and 'image2.jpg' are in the same directory as this script.")
        return None, None
    except Exception as e:
        st.error(f"An error occurred while loading images: {str(e)}")
        return None, None

class FreezingPointCalculator:
    def __init__(self):
        st.title("نزمبونەوەی پلەی بەستن: ژمێرکاری بۆ تواوەی نا ئەلیکترۆلیتی")
        self.create_layout()

    def create_layout(self):
        if image1 is not None and image2 is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.image(image1, use_column_width=True)
                st.caption("م.هەکاری جلال")
            with col2:
                st.image(image2, use_column_width=True)
                st.caption("گروپی تێلێگرام")

        col1, col2, col3 = st.columns(3)

        with col1:
            self.delta_tf_input = st.text_input("Δtf:", key="delta_tf")
            self.kf_input = st.text_input("Kf:", key="kf")
            self.molality_input = st.text_input("**molality:**", key="molality")

        with col2:
            self.t_solution_input = st.text_input("**پلەی بەستنی گیراوە:**", key="t_solution")
            self.t_solution_unit = st.selectbox("یەکە:", ["Celsius", "Kelvin"], key="t_solution_unit")
            self.t_solvent_input = st.text_input("**پلەی بەستنی توێنەر:**", key="t_solvent")
            self.t_solvent_unit = st.selectbox("یەکە:", ["Celsius", "Kelvin"], key="t_solvent_unit")

        with col3:
            self.mass_solute_input = st.text_input("**بارستەی تواوە:**", key="mass_solute")
            self.mass_solute_unit = st.selectbox("یەکە:", ["grams", "kilograms"], key="mass_solute_unit")
            self.mr_input = st.text_input("**بارستەی مۆڵی  Mr:**", key="mr")
            self.moles_solute_input = st.text_input("**مۆڵی تواوە:**", key="moles_solute")
            self.kg_solvent_input = st.text_input("**بارستەی توێنەر:**", key="kg_solvent")
            self.kg_solvent_unit = st.selectbox("یەکە:", ["grams", "kilograms"], key="kg_solvent_unit")

        col1, col2 = st.columns(2)
        with col1:
            st.button("**ژمێرکاری**", key="calculate", on_click=self.calculate)
        with col2:
            st.button("**سڕینەوە**", key="clear", on_click=self.clear_inputs)

    def get_float_value(self, key):
        """Convert input value to float, return None if invalid."""
        try:
            value = st.session_state.get(key, "").strip()
            return float(value) if value else None
        except (ValueError, TypeError):
            return None

    def convert_temperature(self, value, from_unit):
        """Convert temperature between Celsius and Kelvin."""
        if value is None:
            return None
        if from_unit == 'Kelvin':
            return value - 273.15
        return value

    def convert_mass(self, value, from_unit, to_unit):
        """Convert mass between grams and kilograms."""
        if value is None or from_unit == to_unit:
            return value
        if from_unit == 'grams' and to_unit == 'kilograms':
            return value / 1000
        if from_unit == 'kilograms' and to_unit == 'grams':
            return value * 1000

    def show_calculation_step(self, equation, values, result):
        """Display calculation step with proper formatting."""
        if equation == 'Δtf = گیراوە-T - توێنەر-T':
            values_str = f" = {values[0]:.4f} - {values[1]:.4f}"
        else:
            values_str = " = " + " / ".join(f"{v:.4f}" for v in values)
        st.write(f"{equation}{values_str} = {result:.4f}")

    def clear_inputs(self):
        """Clear all input fields."""
        keys_to_clear = [
            "delta_tf", "kf", "molality", "t_solution", "t_solvent",
            "mass_solute", "mr", "moles_solute", "kg_solvent"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                st.session_state[key] = ""

    def calculate(self):
        """Perform calculations based on available inputs."""
        st.write("هەنگاوەکانی ژمێرکاری")
        st.write("-" * 50)

        inputs = {
            'delta_tf': self.get_float_value("delta_tf"),
            'kf': self.get_float_value("kf"),
            'molality': self.get_float_value("molality"),
            't_solution': self.get_float_value("t_solution"),
            't_solvent': self.get_float_value("t_solvent"),
            'mass_solute': self.get_float_value("mass_solute"),
            'mr': self.get_float_value("mr"),
            'moles_solute': self.get_float_value("moles_solute"),
            'kg_solvent': self.get_float_value("kg_solvent")
        }

        # Convert units
        inputs['t_solution'] = self.convert_temperature(
            inputs['t_solution'],
            st.session_state.get('t_solution_unit', 'Celsius')
        )
        inputs['t_solvent'] = self.convert_temperature(
            inputs['t_solvent'],
            st.session_state.get('t_solvent_unit', 'Celsius')
        )
        if inputs['mass_solute'] is not None:
            inputs['mass_solute'] = self.convert_mass(
                inputs['mass_solute'],
                st.session_state.get('mass_solute_unit', 'grams'),
                'grams'
            )
        if inputs['kg_solvent'] is not None:
            inputs['kg_solvent'] = self.convert_mass(
                inputs['kg_solvent'],
                st.session_state.get('kg_solvent_unit', 'grams'),
                'kilograms'
            )

        calculations = [
            {
                'param': 'delta_tf',
                'func': lambda kf, m: kf * m,
                'equation': 'Δtf = Kf × molality',
                'params': ['kf', 'molality']
            },
            # ... [rest of the calculations remain the same]
        ]

        iteration_count = 0
        max_iterations = 10
        
        while iteration_count < max_iterations:
            found_new_value = False
            
            for calc in calculations:
                param = calc['param']
                if inputs[param] is None:
                    if all(inputs[p] is not None for p in calc['params']):
                        values = [inputs[p] for p in calc['params']]
                        result = calc['func'](*values)
                        self.show_calculation_step(calc['equation'], values, result)
                        inputs[param] = result
                        found_new_value = True
            
            if not found_new_value:
                break
                
            iteration_count += 1

        st.write("-" * 50)

# The BoilingPointCalculator class would be similar, with the same helper methods
# but using 'tb' instead of 'tf' and 'kb' instead of 'kf'

class BoilingPointCalculator(FreezingPointCalculator):
    def __init__(self):
        st.title("بەرزبونەوەی پلەی کوڵان: ژمێرکاری بۆ تواوەی نا ئەلیکترۆلیتی")
        self.create_layout()

    # Inherit all methods from FreezingPointCalculator
    # Only override the calculate method if needed for specific boiling point calculations

def main():
    global image1, image2
    
    st.markdown(""" <p style='text-align: center; color: gray; font-style: italic;'>
    بۆ یەکەمین جار ئەم جۆرە بەرنامەیە دروستکراوە و گەشەی پێدراوە لە کوردستان و عێراق دا. هیوادارم سوودی لێوەربگرن.
    م. هەکاری جلال محمد </p> """, unsafe_allow_html=True)
    
    image1, image2 = load_images()

    st.sidebar.title("Choose Calculator")
    calculator_type = st.sidebar.radio("Select the calculator:", ("نزمبونەوەی پلەی بەستن", "بەرزبونەوەی پلەی کوڵان"))

    if calculator_type == "نزمبونەوەی پلەی بەستن":
        FreezingPointCalculator()
    elif calculator_type == "بەرزبونەوەی پلەی کوڵان":
        BoilingPointCalculator()

if __name__ == "__main__":
    main()
