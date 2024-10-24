import streamlit as st
import numpy as np
from PIL import Image
import os

def load_images():
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(__file__)
        
        # Construct the full path to the images
        image1_path = os.path.join(current_dir, "image1.jpg")
        image2_path = os.path.join(current_dir, "image2.jpg")
        
        # Open the images
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)
        
        return image1, image2
    except FileNotFoundError:
        st.warning("Image files not found. Please ensure 'image1.jpg' and 'image2.jpg' are in the same directory as this script.")
        return None, None
    except Exception as e:
        st.error(f"An error occurred while loading images: {str(e)}")
        return None, None

image1, image2 = load_images()

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
            self.calculate_button = st.button("**ژمێرکاری**", key="calculate")
        with col2:
            self.clear_button = st.button("**سڕینەوە**", key="clear")

        if self.calculate_button:
            self.calculate()
        if self.clear_button:
            self.clear_inputs()

    def clear_inputs(self):
        keys_to_clear = [
            "delta_tf", "kf", "molality", "t_solution", "t_solvent",
            "mass_solute", "mr", "moles_solute", "kg_solvent"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        for key in keys_to_clear:
            st.session_state[key] = ""

    def get_float_value(self, key):
        try:
            value = st.session_state[key].strip()
            return float(value) if value else None
        except ValueError:
            return None

    def convert_temperature(self, value, from_unit):
        if value is None:
            return None
        if from_unit == 'Kelvin':
            return value - 273.15
        return value

    def convert_mass(self, value, from_unit, to_unit):
        if value is None or from_unit == to_unit:
            return value
        if from_unit == 'grams' and to_unit == 'kilograms':
            return value / 1000
        if from_unit == 'kilograms' and to_unit == 'grams':
            return value * 1000

    def format_value(self, value):
        return f"{value:.4f}" if value is not None else "unknown"

    def show_calculation_step(self, equation, values, result):
        if equation == 'Δtf = گیراوە-T - توێنەر-T':
            values_str = f" = {values[0]:.4f} - {values[1]:.4f}"
        else:
            values_str = " = " + " / ".join(f"{v:.4f}" for v in values)
        st.write(f"{equation}{values_str} = {result:.4f}")

    def calculate(self):
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

        inputs['t_solution'] = self.convert_temperature(
            inputs['t_solution'],
            st.session_state.t_solution_unit
        )
        inputs['t_solvent'] = self.convert_temperature(
            inputs['t_solvent'],
            st.session_state.t_solvent_unit
        )
        if inputs['mass_solute'] is not None:
            inputs['mass_solute'] = self.convert_mass(
                inputs['mass_solute'],
                st.session_state.mass_solute_unit,
                'grams'
            )
        if inputs['kg_solvent'] is not None:
            inputs['kg_solvent'] = self.convert_mass(
                inputs['kg_solvent'],
                st.session_state.kg_solvent_unit,
                'kilograms'
            )

        # Iteratively calculate all possible values
        calculated = True
        while calculated:
            calculated = False

            # Calculate Δtf
            if inputs['delta_tf'] is None and inputs['kf'] is not None and inputs['molality'] is not None:
                inputs['delta_tf'] = inputs['kf'] * inputs['molality']
                self.show_calculation_step('Δtf = Kf × molality', [inputs['kf'], inputs['molality']], inputs['delta_tf'])
                calculated = True

            # Calculate Δtf using T_solution and T_solvent
            if inputs['delta_tf'] is None and inputs['t_solution'] is not None and inputs['t_solvent'] is not None:
                inputs['delta_tf'] = inputs['t_solution'] - inputs['t_solvent']
                self.show_calculation_step('Δtf = گیراوە-T - توێنەر-T', [inputs['t_solution'], inputs['t_solvent']], inputs['delta_tf'])
                calculated = True

            # Calculate molality from Δtf and Kf
            if inputs['molality'] is None and inputs['delta_tf'] is not None and inputs['kf'] is not None:
                inputs['molality'] = inputs['delta_tf'] / inputs['kf']
                self.show_calculation_step('molality = Δtf / Kf', [inputs['delta_tf'], inputs['kf']], inputs['molality'])
                calculated = True

            # Calculate molality from moles_solute and kg_solvent
            if inputs['molality'] is None and inputs['moles_solute'] is not None and inputs['kg_solvent'] is not None:
                inputs['molality'] = inputs['moles_solute'] / inputs['kg_solvent']
                self.show_calculation_step('molality = تواوە-mole / توێنەر-Kg', [inputs['moles_solute'], inputs['kg_solvent']], inputs['molality'])
                calculated = True

            # Calculate moles_solute from mass_solute and mr
            if inputs['moles_solute'] is None and inputs['mass_solute'] is not None and inputs['mr'] is not None:
                inputs['moles_solute'] = inputs['mass_solute'] / inputs['mr']
                self.show_calculation_step('مۆڵی تواوە = بارستەی تواوە / Mr', [inputs['mass_solute'], inputs['mr']], inputs['moles_solute'])
                calculated = True

            # Calculate mass_solute from moles_solute and mr
            if inputs['mass_solute'] is None and inputs['moles_solute'] is not None and inputs['mr'] is not None:
                inputs['mass_solute'] = inputs['moles_solute'] * inputs['mr']
                self.show_calculation_step('بارستەی تواوە = مۆڵی تواوە × Mr', [inputs['moles_solute'], inputs['mr']], inputs['mass_solute'])
                calculated = True

            # Calculate kg_solvent from molality and moles_solute
            if inputs['kg_solvent'] is None and inputs['molality'] is not None and inputs['moles_solute'] is not None:
                inputs['kg_solvent'] = inputs['moles_solute'] / inputs['molality']
                self.show_calculation_step('توێنەر-Kg = مۆڵی تواوە / molality', [inputs['moles_solute'], inputs['molality']], inputs['kg_solvent'])
                calculated = True

        st.write("-" * 50)
        for param in inputs:
            st.write(f"{param}: {self.format_value(inputs[param])}")

if __name__ == "__main__":
    FreezingPointCalculator()
