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

    # [Previous methods remain unchanged...]

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

        # Convert units
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

        calculations = [
            {
                'param': 'delta_tf',
                'func': lambda kf, m: kf * m,
                'equation': 'Δtf = Kf × molality',
                'params': ['kf', 'molality']
            },
            {
                'param': 'delta_tf',
                'func': lambda ts, tsv: ts - tsv,
                'equation': 'Δtf = گیراوە-T - توێنەر-T',
                'params': ['t_solution', 't_solvent']
            },
            {
                'param': 'molality',
                'func': lambda dt, kf: dt / kf,
                'equation': 'molality = Δtf / Kf',
                'params': ['delta_tf', 'kf']
            },
            {
                'param': 'molality',
                'func': lambda mol, kg: mol / kg,
                'equation': 'molality = تواوە-mole / توێنەر-Kg',
                'params': ['moles_solute', 'kg_solvent']
            },
            {
                'param': 'moles_solute',
                'func': lambda mass, mr: mass / mr,
                'equation': 'تواوە-mole = تواوە-mass / Mr',
                'params': ['mass_solute', 'mr']
            },
            {
                'param': 'moles_solute',
                'func': lambda m, kg: m * kg,
                'equation': 'تواوە-mole = molality × توێنەر-Kg',
                'params': ['molality', 'kg_solvent']
            },
            {
                'param': 'mass_solute',
                'func': lambda mol, mr: mol * mr,
                'equation': 'تواوە-mass = تواوە-mole × Mr',
                'params': ['moles_solute', 'mr']
            },
            {
                'param': 'kg_solvent',
                'func': lambda mol, m: mol / m,
                'equation': 'توێنەر-Kg = تواوە-mole / molality',
                'params': ['moles_solute', 'molality']
            },
            {
                'param': 'mr',
                'func': lambda mass, mol: mass / mol,
                'equation': 'Mr = تواوە-mass / تواوە-mole',
                'params': ['mass_solute', 'moles_solute']
            }
        ]

        # Keep calculating until no new values can be found
        iteration_count = 0
        max_iterations = 10  # Prevent infinite loops
        
        while iteration_count < max_iterations:
            found_new_value = False
            
            for calc in calculations:
                param = calc['param']
                if inputs[param] is None:  # Only try to calculate if we don't have this value
                    if all(inputs[p] is not None for p in calc['params']):  # All required parameters are available
                        values = [inputs[p] for p in calc['params']]
                        result = calc['func'](*values)
                        self.show_calculation_step(calc['equation'], values, result)
                        inputs[param] = result
                        found_new_value = True
            
            if not found_new_value:  # If no new values were calculated, we're done
                break
                
            iteration_count += 1

        st.write("-" * 50)

class BoilingPointCalculator:
    # [Previous methods remain unchanged...]

    def calculate(self):
        st.write("هەنگاوەکانی ژمێرکاری")
        st.write("-" * 50)

        inputs = {
            'delta_tb': self.get_float_value("delta_tb"),
            'kb': self.get_float_value("kb"),
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

        calculations = [
            {
                'param': 'delta_tb',
                'func': lambda kb, m: kb * m,
                'equation': 'Δtb = Kb × molality',
                'params': ['kb', 'molality']
            },
            {
                'param': 'delta_tb',
                'func': lambda ts, tsv: ts - tsv,
                'equation': 'Δtb = گیراوە-T - توێنەر-T',
                'params': ['t_solution', 't_solvent']
            },
            {
                'param': 'molality',
                'func': lambda dt, kb: dt / kb,
                'equation': 'molality = Δtb / Kb',
                'params': ['delta_tb', 'kb']
            },
            {
                'param': 'molality',
                'func': lambda mol, kg: mol / kg,
                'equation': 'molality = تواوە-mole / توێنەر-Kg',
                'params': ['moles_solute', 'kg_solvent']
            },
            {
                'param': 'moles_solute',
                'func': lambda mass, mr: mass / mr,
                'equation': 'تواوە-mole = تواوە-mass / Mr',
                'params': ['mass_solute', 'mr']
            },
            {
                'param': 'moles_solute',
                'func': lambda m, kg: m * kg,
                'equation': 'تواوە-mole = molality × توێنەر-Kg',
                'params': ['molality', 'kg_solvent']
            },
            {
                'param': 'mass_solute',
                'func': lambda mol, mr: mol * mr,
                'equation': 'تواوە-mass = تواوە-mole × Mr',
                'params': ['moles_solute', 'mr']
            },
            {
                'param': 'kg_solvent',
                'func': lambda mol, m: mol / m,
                'equation': 'توێنەر-Kg = تواوە-mole / molality',
                'params': ['moles_solute', 'molality']
            },
            {
                'param': 'mr',
                'func': lambda mass, mol: mass / mol,
                'equation': 'Mr = تواوە-mass / تواوە-mole',
                'params': ['mass_solute', 'moles_solute']
            }
        ]

        # Keep calculating until no new values can be found
        iteration_count = 0
        max_iterations = 10  # Prevent infinite loops
        
        while iteration_count < max_iterations:
            found_new_value = False
            
            for calc in calculations:
                param = calc['param']
                if inputs[param] is None:  # Only try to calculate if we don't have this value
                    if all(inputs[p] is not None for p in calc['params']):  # All required parameters are available
                        values = [inputs[p] for p in calc['params']]
                        result = calc['func'](*values)
                        self.show_calculation_step(calc['equation'], values, result)
                        inputs[param] = result
                        found_new_value = True
            
            if not found_new_value:  # If no new values were calculated, we're done
                break
                
            iteration_count += 1

        st.write("-" * 50)

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
