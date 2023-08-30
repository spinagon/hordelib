from typing import Generator

import PIL.Image
import pytest

from hordelib import SharedModelManager
from hordelib.comfy_horde import Comfy_Horde
from hordelib.horde import HordeLib
from hordelib.model_manager.hyper import ALL_MODEL_MANAGER_TYPES


@pytest.fixture(scope="session")
def init_horde():
    """This fixture initialises HordeLib and sets the VRAM to leave free to 90%.
    You must call this fixture if your test uses a module which imports `hordelib.comfy_horde`. You will usually
    see a characteristic RuntimeError exception if you forget to call this fixture, but you may also see an
    import error from within comfy if your code does not instantiate the `Comfy_Horde` class."""
    import hordelib

    hordelib.initialise()
    from hordelib.settings import UserSettings

    UserSettings.set_ram_to_leave_free_mb("100%")
    UserSettings.set_vram_to_leave_free_mb("90%")


@pytest.fixture(scope="session")
def hordelib_instance(init_horde) -> HordeLib:
    return HordeLib()


@pytest.fixture(scope="class")
def isolated_comfy_horde_instance(init_horde) -> Comfy_Horde:
    return Comfy_Horde()


@pytest.fixture(scope="session")
def shared_model_manager(hordelib_instance: HordeLib) -> Generator[type[SharedModelManager], None, None]:
    SharedModelManager()
    SharedModelManager.load_model_managers(ALL_MODEL_MANAGER_TYPES)

    assert SharedModelManager()._instance is not None
    assert SharedModelManager.manager is not None
    assert SharedModelManager.manager.codeformer is not None
    assert SharedModelManager.manager.codeformer.download_all_models()
    assert SharedModelManager.manager.compvis is not None

    assert SharedModelManager.manager.download_model("Deliberate")
    assert SharedModelManager.manager.validate_model("Deliberate")
    assert SharedModelManager.manager.download_model("SDXL 1.0")
    assert SharedModelManager.manager.validate_model("SDXL 1.0")

    assert SharedModelManager.manager.controlnet is not None
    assert SharedModelManager.manager.controlnet.download_all_models()
    assert SharedModelManager.preload_annotators()
    assert SharedModelManager.manager.esrgan is not None
    assert SharedModelManager.manager.esrgan.download_all_models()
    assert SharedModelManager.manager.gfpgan is not None
    assert SharedModelManager.manager.gfpgan.download_all_models()
    assert SharedModelManager.manager.safety_checker is not None
    assert SharedModelManager.manager.safety_checker.download_all_models()
    assert SharedModelManager.manager.lora is not None
    assert SharedModelManager.manager.ti is not None

    yield SharedModelManager

    SharedModelManager._instance = None  # type: ignore
    SharedModelManager.manager = None  # type: ignore


_testing_model_name = "Deliberate"


@pytest.fixture(scope="session")
def stable_diffusion_model_name_for_testing(shared_model_manager: type[SharedModelManager]) -> str:
    return _testing_model_name


@pytest.fixture(scope="session")
def sdxl_1_0_base_model_name(shared_model_manager: type[SharedModelManager]) -> str:
    return "SDXL 1.0"


@pytest.fixture(scope="session")
def db0_test_image() -> PIL.Image.Image:
    return PIL.Image.open("images/test_db0.jpg")


@pytest.fixture(scope="session")
def real_image() -> PIL.Image.Image:
    return PIL.Image.open("images/test_annotator.jpg")


def pytest_collection_modifyitems(items):
    """Modifies test items to ensure test modules run in a given order."""
    MODULES_TO_RUN_FIRST = [
        "test_packaging_errors",
        "tests.test_initialisation",
        "tests.test_cuda",
        "tests.test_utils",
        "tests.test_comfy_install",
        "tests.test_comfy",
        "tests.test_payload_mapping",
        "test_shared_model_manager",
        "test_mm_lora",
        "test_mm_ti",
    ]
    MODULES_TO_RUN_LAST = [
        "test.test_blip",
        "test.test_clip",
        "tests.test_inference",
        "tests.test_horde_inference",
        "tests.test_horde_inference_img2img",
        "tests.test_horde_samplers",
        "tests.test_horde_inference_controlnet",
        "tests.test_horde_lora",
        "tests.test_horde_inference_painting",
    ]
    module_mapping = {item: item.module.__name__ for item in items}

    sorted_items = []

    for module in MODULES_TO_RUN_FIRST:
        sorted_items.extend([item for item in items if module_mapping[item] == module])

    sorted_items.extend(
        [item for item in items if module_mapping[item] not in MODULES_TO_RUN_FIRST + MODULES_TO_RUN_LAST],
    )

    for module in MODULES_TO_RUN_LAST:
        sorted_items.extend([item for item in items if module_mapping[item] == module])

    items[:] = sorted_items
