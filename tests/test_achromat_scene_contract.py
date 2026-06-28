import importlib.util
from pathlib import Path
import sys


SCENE_PATH = Path("simulations/blender/scenes/achromat_back_reflection.py")
REPO_ROOT = Path(__file__).resolve().parents[1]


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


def test_scene_script_imports_when_executed_by_path_without_repo_on_sys_path(
    monkeypatch,
):
    original_path = list(sys.path)
    filtered_path = [
        path for path in original_path if Path(path or ".").resolve() != REPO_ROOT
    ]
    monkeypatch.setattr(sys, "path", filtered_path)

    module = load_scene_module()

    assert module.SCENE_NAME == "achromat_back_reflection"
    assert str(REPO_ROOT) in sys.path


def test_scene_default_parameters_match_first_demo():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["wavelength_nm"] == 561.0
    assert params["beam_diameter_mm"] == 1.0
    assert params["aperture_diameter_mm"] == 1.0
    assert params["lens_focal_length_mm"] == 100.0
    assert params["lens_diameter_mm"] == 25.4
    assert params["lens_thickness_mm"] == 6.5
    assert params["optical_axis_z_mm"] == 22.1
    assert params["reflected_surfaces"] == ("front_bk7_air", "rear_sf5_air")
    assert "Thorlabs AC254-100-A-ML mounted drawing" in params["lens_source"]
    assert "Thorlabs LMR1/M drawing" in params["mount_source"]
    assert params["initial_tilt_y_deg"] != 0.0
    assert params["initial_decenter_y_mm"] != 0.0
    assert params["exaggeration"] > 1.0


def test_scene_default_parameters_include_cinematic_video_contract():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["show_minimal_labels"] is True
    assert params["hero_camera_name"] == "Hero Camera"
    assert params["default_render_preset"] == "final"
    assert params["render_presets"]["preview"]["engine"] == "BLENDER_EEVEE"
    assert params["render_presets"]["final"]["engine"] == "CYCLES"

    labels = params["scene_labels"]
    assert labels == (
        "Aperture card",
        "AC254-100-A doublet",
        "LMR1 mount",
        "Two return reflections",
    )
