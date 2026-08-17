# part1 - Correctness
from pathlib import Path
import json
from typing import Callable

from PIL import Image, ImageOps, ImageFilter


def _apply_transformations(image: Image.Image, transformations: list[dict]) -> Image.Image:
    for transform in transformations:
        transform_type = transform["type"]

        if transform_type == "grayscale":
            image = ImageOps.grayscale(image)

        elif transform_type == "flip_horizontal":
            image = ImageOps.mirror(image)

        elif transform_type == "flip_vertical":
            image = ImageOps.flip(image)

        elif transform_type == "scale":
            image = ImageOps.scale(image, transform["factor"])

        elif transform_type == "blur":
            image = image.filter(ImageFilter.BoxBlur(transform["radius"]))

        elif transform_type == "rotate":
            image = image.rotate(transform["angle"])

        else:
            raise ValueError(f"Unknown transformation: {transform_type}")

    return image


def process_images(
    image_dir: str,
    transformation_dir: str,
    get_output_path: Callable[[str, str], str],
) -> None:
    image_path = Path(image_dir)
    transformation_path = Path(transformation_dir)

    image_files = sorted(
        p for p in image_path.iterdir()
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )

    transformation_files = sorted(
        p for p in transformation_path.iterdir()
        if p.is_file() and p.suffix.lower() == ".json"
    )

    # Empty input directories produce no output.
    if not image_files or not transformation_files:
        return

    # Read each pipeline once instead of once per image.
    pipelines = []
    for path in transformation_files:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        pipelines.append((path, data["transformations"]))

    for image_path in image_files:
        for transformation_path, transformations in pipelines:
            destination = Path(
                get_output_path(str(image_path), str(transformation_path))
            )
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Open a fresh source image for every pair. This guarantees that
            # one pipeline cannot modify the input seen by another pipeline.
            with Image.open(image_path) as source:
                image = source.copy()

            try:
                image = _apply_transformations(image, transformations)
                image.save(destination)
            finally:
                image.close()

# part 2 - Performance

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json
import os
from typing import Callable

from PIL import Image, ImageOps, ImageFilter


def _apply_transformations(image: Image.Image, transformations: list[dict]) -> Image.Image:
    for transform in transformations:
        kind = transform["type"]

        if kind == "grayscale":
            image = ImageOps.grayscale(image)

        elif kind == "flip_horizontal":
            image = ImageOps.mirror(image)

        elif kind == "flip_vertical":
            image = ImageOps.flip(image)

        elif kind == "scale":
            image = ImageOps.scale(image, transform["factor"])

        elif kind == "blur":
            image = image.filter(
                ImageFilter.BoxBlur(transform["radius"])
            )

        elif kind == "rotate":
            image = image.rotate(transform["angle"])

        else:
            raise ValueError(f"Unknown transformation: {kind}")

    return image


def _process_one(
    image_path: str,
    transformations: list[dict],
    destination: str,
) -> None:
    # Each worker gets its own source image and its own output.
    with Image.open(image_path) as source:
        image = source.copy()

    try:
        image = _apply_transformations(image, transformations)

        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination_path)
    finally:
        image.close()


def process_images(
    image_dir: str,
    transformation_dir: str,
    get_output_path: Callable[[str, str], str],
) -> None:
    image_root = Path(image_dir)
    transformation_root = Path(transformation_dir)

    image_files = sorted(
        p for p in image_root.iterdir()
        if p.is_file()
        and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )

    transformation_files = sorted(
        p for p in transformation_root.iterdir()
        if p.is_file()
        and p.suffix.lower() == ".json"
    )

    if not image_files or not transformation_files:
        return

    # Parse each JSON file exactly once.
    pipelines = []
    for transformation_path in transformation_files:
        with transformation_path.open("r", encoding="utf-8") as f:
            transformations = json.load(f)["transformations"]

        pipelines.append((transformation_path, transformations))

    # Build the complete job list in the parent process.
    jobs = []

    for image_path in image_files:
        for transformation_path, transformations in pipelines:
            destination = get_output_path(
                str(image_path),
                str(transformation_path),
            )

            jobs.append(
                (
                    str(image_path),
                    transformations,
                    str(destination),
                )
            )

    # Leave one CPU available for the parent process.
    workers = max(1, (os.cpu_count() or 1) - 1)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # map waits until every submitted job has completed.
        list(executor.map(
            _process_one,
            (job[0] for job in jobs),
            (job[1] for job in jobs),
            (job[2] for job in jobs),
        ))
