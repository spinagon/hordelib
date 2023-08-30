import typing

from typing_extensions import override

from hordelib.consts import MODEL_CATEGORY_NAMES
from hordelib.model_manager.base import BaseModelManager


class DiffusersModelManager(BaseModelManager):
    def __init__(self, download_reference=False):
        raise NotImplementedError("Diffusers are not yet supported")

        super().__init__(
            model_category_name=MODEL_CATEGORY_NAMES.diffusers,
            download_reference=download_reference,
        )

    @override
    def model_to_ram(
        self,
        model_name: str,
        **kwargs,
    ) -> dict[str, typing.Any]:
        raise NotImplementedError("Diffusers are not yet supported")
