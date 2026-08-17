from typing import Any, List


def transform_image(image: List[List[Any]], pipeline: List[dict]) -> List[List[Any]]:
    img = image

    for step in pipeline:
        name = step.get("transform")
        args = step.get("args", [])

        if name == "flip_horizontal" and len(args) == 0:
            img = [row[::-1] for row in img]

        elif name == "flip_vertical" and len(args) == 0:
            img = img[::-1]

        elif name == "rotate" and len(args) == 1 and args[0] in (90, 180, 270):
            degrees = args[0]

            if degrees == 90:
                img = [list(row) for row in zip(*img[::-1])]
            elif degrees == 180:
                img = [row[::-1] for row in img[::-1]]
            else:  # 270
                img = [list(row) for row in zip(*img)][::-1]

        elif name == "scale" and len(args) == 1 and isinstance(args[0], int) and args[0] > 0:
            factor = args[0]

            # Scale horizontally
            scaled = [
                [pixel for pixel in row for _ in range(factor)]
                for row in img
            ]

            # Scale vertically
            img = [
                row[:] 
                for row in scaled
                for _ in range(factor)
            ]

        elif name == "blur" and len(args) == 0:
            rows = len(img)
            cols = len(img[0]) if rows else 0

            blurred = []

            for r in range(rows):
                new_row = []

                for c in range(cols):
                    total = 0
                    count = 0

                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            nr, nc = r + dr, c + dc

                            if 0 <= nr < rows and 0 <= nc < cols:
                                total += img[nr][nc]
                                count += 1

                    new_row.append(total // count)

                blurred.append(new_row)

            img = blurred

        elif name == "grayscale" and len(args) == 0:
            img = [
                [
                    (pixel[0] + pixel[1] + pixel[2]) // 3
                    if isinstance(pixel, (list, tuple)) and len(pixel) == 3
                    else pixel
                    for pixel in row
                ]
                for row in img
            ]

        # Invalid operation/arguments: leave img unchanged

    return img
