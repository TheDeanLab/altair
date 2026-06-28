import importlib.util
from pathlib import Path


SCENE_PATH = Path("simulations/blender/scenes/achromat_back_reflection.py")


def load_scene_module():
    spec = importlib.util.spec_from_file_location(
        "achromat_back_reflection", SCENE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_scene_script_imports_without_running_blender():
    module = load_scene_module()

    assert module.SCENE_NAME == "achromat_back_reflection"
    assert callable(module.main)


def test_scene_default_parameters_match_first_demo():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["wavelength_nm"] == 561.0
    assert params["beam_diameter_mm"] == 1.0
    assert params["aperture_diameter_mm"] == 1.0
    assert params["lens_focal_length_mm"] == 100.0
    assert params["lens_diameter_mm"] == 25.4
    assert params["initial_tilt_y_deg"] != 0.0
    assert params["initial_decenter_y_mm"] != 0.0
    assert params["exaggeration"] > 1.0
