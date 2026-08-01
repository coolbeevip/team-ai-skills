#!/usr/bin/env python3
"""Calculate an idealized horizontal camera pixel budget."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BudgetRow:
    distance: float
    angular_width_deg: float
    pixels_on_target: float
    meets_required_pixels: bool | None


def positive_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be a finite number greater than zero")
    return number


def nonnegative_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("must be a finite number greater than or equal to zero")
    return number


def hfov_degrees(value: str) -> float:
    number = positive_float(value)
    if number >= 180:
        raise argparse.ArgumentTypeError("must be less than 180 degrees")
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Calculate pixels on a target, maximum threshold distance, and required "
            "image width for an idealized horizontal camera model."
        )
    )
    parser.add_argument(
        "--object-width",
        required=True,
        type=positive_float,
        help="Target physical width. Use the same unit as --distance.",
    )
    parser.add_argument(
        "--distance",
        required=True,
        type=positive_float,
        nargs="+",
        help="One or more target distances in the same unit as --object-width.",
    )
    parser.add_argument(
        "--image-width",
        required=True,
        type=positive_float,
        help="Effective horizontal image width in pixels after crop or resize.",
    )
    parser.add_argument(
        "--hfov-deg",
        required=True,
        type=hfov_degrees,
        help="Horizontal field of view in degrees.",
    )
    parser.add_argument(
        "--required-pixels",
        type=positive_float,
        help="Unmargined target-width threshold in pixels.",
    )
    parser.add_argument(
        "--margin-percent",
        type=nonnegative_float,
        default=0.0,
        help="Engineering margin added to --required-pixels (default: 0).",
    )
    parser.add_argument(
        "--model",
        choices=("rectilinear", "linear-angle"),
        default="rectilinear",
        help="Projection model. linear-angle is a coarse comparison only.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def focal_length_pixels(image_width: float, hfov_deg: float) -> float:
    return image_width / (2 * math.tan(math.radians(hfov_deg) / 2))


def angular_width_degrees(object_width: float, distance: float) -> float:
    return math.degrees(2 * math.atan(object_width / (2 * distance)))


def pixels_on_target(
    *,
    model: str,
    object_width: float,
    distance: float,
    image_width: float,
    hfov_deg: float,
) -> float:
    if model == "rectilinear":
        return focal_length_pixels(image_width, hfov_deg) * object_width / distance
    return image_width * angular_width_degrees(object_width, distance) / hfov_deg


def maximum_distance(
    *,
    model: str,
    object_width: float,
    image_width: float,
    hfov_deg: float,
    required_pixels_with_margin: float,
) -> float:
    if model == "rectilinear":
        return (
            focal_length_pixels(image_width, hfov_deg)
            * object_width
            / required_pixels_with_margin
        )
    required_angle_deg = required_pixels_with_margin * hfov_deg / image_width
    if required_angle_deg >= 180:
        return 0.0
    return object_width / (2 * math.tan(math.radians(required_angle_deg) / 2))


def required_image_width(
    *,
    model: str,
    object_width: float,
    distance: float,
    hfov_deg: float,
    required_pixels_with_margin: float,
) -> float:
    if model == "rectilinear":
        return (
            2
            * math.tan(math.radians(hfov_deg) / 2)
            * distance
            * required_pixels_with_margin
            / object_width
        )
    angle_deg = angular_width_degrees(object_width, distance)
    return required_pixels_with_margin * hfov_deg / angle_deg


def calculate(args: argparse.Namespace) -> dict[str, object]:
    required_with_margin = None
    if args.required_pixels is not None:
        required_with_margin = args.required_pixels * (1 + args.margin_percent / 100)

    rows = []
    for distance in args.distance:
        pixels = pixels_on_target(
            model=args.model,
            object_width=args.object_width,
            distance=distance,
            image_width=args.image_width,
            hfov_deg=args.hfov_deg,
        )
        rows.append(
            BudgetRow(
                distance=distance,
                angular_width_deg=angular_width_degrees(args.object_width, distance),
                pixels_on_target=pixels,
                meets_required_pixels=(
                    None if required_with_margin is None else pixels >= required_with_margin
                ),
            )
        )

    result: dict[str, object] = {
        "model": args.model,
        "assumptions": [
            "object width and distance use the same physical unit",
            "horizontal calculation only",
            "rectilinear model uses ideal pinhole projection near the calibrated region",
            "distortion, blur, noise, occlusion, optics, and model accuracy are not included",
        ],
        "inputs": {
            "object_width": args.object_width,
            "distances": args.distance,
            "image_width_px": args.image_width,
            "hfov_deg": args.hfov_deg,
            "required_pixels": args.required_pixels,
            "margin_percent": args.margin_percent,
        },
        "focal_length_px": (
            focal_length_pixels(args.image_width, args.hfov_deg)
            if args.model == "rectilinear"
            else None
        ),
        "required_pixels_with_margin": required_with_margin,
        "rows": [asdict(row) for row in rows],
    }

    if required_with_margin is not None:
        result["maximum_distance_at_threshold"] = maximum_distance(
            model=args.model,
            object_width=args.object_width,
            image_width=args.image_width,
            hfov_deg=args.hfov_deg,
            required_pixels_with_margin=required_with_margin,
        )
        result["required_image_width_at_distances"] = [
            {
                "distance": distance,
                "required_image_width_px": required_image_width(
                    model=args.model,
                    object_width=args.object_width,
                    distance=distance,
                    hfov_deg=args.hfov_deg,
                    required_pixels_with_margin=required_with_margin,
                ),
            }
            for distance in args.distance
        ]
    return result


def print_text(result: dict[str, object]) -> None:
    inputs = result["inputs"]
    assert isinstance(inputs, dict)
    print(f"Model: {result['model']}")
    if result["model"] == "linear-angle":
        print("Warning: linear-angle is a coarse approximation; do not mix it with pinhole results.")
    if result["focal_length_px"] is not None:
        print(f"Horizontal focal length: {result['focal_length_px']:.2f} px")
    if result["required_pixels_with_margin"] is not None:
        print(
            "Required pixels with margin: "
            f"{result['required_pixels_with_margin']:.2f} px "
            f"({inputs['margin_percent']:.2f}% margin)"
        )
    print("\nDistance budget:")
    for row in result["rows"]:
        status = ""
        if row["meets_required_pixels"] is not None:
            status = "PASS" if row["meets_required_pixels"] else "FAIL"
            status = f" | {status}"
        print(
            f"- distance {row['distance']:.4g}: {row['pixels_on_target']:.2f} px, "
            f"angular width {row['angular_width_deg']:.3f} deg{status}"
        )
    if "maximum_distance_at_threshold" in result:
        print(
            "\nMaximum distance at threshold: "
            f"{result['maximum_distance_at_threshold']:.4g}"
        )
        print("Required image width at each distance:")
        for row in result["required_image_width_at_distances"]:
            print(
                f"- distance {row['distance']:.4g}: "
                f"{row['required_image_width_px']:.2f} px"
            )
    print("\nDesign-budget output only; validate calibration, image quality, and model accuracy in PoC.")


def main() -> None:
    args = parse_args()
    result = calculate(args)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_text(result)


if __name__ == "__main__":
    main()
